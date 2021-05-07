import threading

import time

from Xlib import display, X

def snapshot(rt, xywh):
    w = xywh[2]
    h = xywh[3]

    #shift by one pixel to compensate for cz outline width
    return rt.get_image(xywh[0] + 1, xywh[1] + 1, w, h, X.ZPixmap, 0xffffffff).data

    # return raw.data
    # return Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")

def _to_ltwh(bbox):
    x0, y0, x1, y1 = bbox
    return (x0, y0, x1 - x0, y1 - y0)

def capture(ltwh):
    return snapshot(display.Display().screen().root, ltwh)

class CaptureLoop(object):
    def __init__(self):

        self._stop_evt = threading.Event()
        self._stop = False
        self._running = False

        self._handlers = []

    # def initialize(self, bbox):
    #     # todo: the offset is handled by the image handlers
    #     self._top = bbox[1]
    #     self._left = bbox[0]
    #     self._width = bbox[2] - self._left
    #     self._height = bbox[3] - self._top
    #     return snapshot(display.Display().screen().root, _to_ltwh(bbox))
    #
    # def capture(self):
    #     return snapshot(
    #         display.Display().screen().root,
    #         (self._left, self._top, self._width, self._height))
    #
    # def capture_relative(self, ltwh):
    #     return snapshot(
    #         display.Display().screen().root,
    #         tuple(map(operator.add, ltwh, (self._left, self._top, 0, 0))))
    #
    # def _from_bytes(self, data):
    #     return Image.frombytes("RGB", data.size, data.bgra, "raw", "BGRX")

    def initialize(self, handlers):
        self._handlers = handlers

    def start(self, fps=None):
        '''

        Parameters
        ----------
        requests: tuple

        Returns
        -------

        '''
        self._stop = False
        self._stop_evt.clear()

        dsp = display.Display().screen().root

        if fps:
            def start_capped():
                self._start_capped(dsp, 1/fps)
            thread = threading.Thread(target=start_capped)
        else:
            def start_uncapped():
                self._start_uncapped(dsp)

            thread = threading.Thread(target=start_uncapped)

        self._running = True

        thread.start()

    def _start_uncapped(self, display):
        # shift = (x, y, 0, 0)

        handlers = self._handlers

        while not self._stop:
            # t0 = time.time()
            # with self._lock:
            # for handler in self._handlers:
            #     handler.process_image(snapshot(
            #         dsp,
            #         tuple(map(operator.add, handler.ltwh, shift))))

            for handler in handlers:
                handler.process_image(snapshot(display, handler.ltwh))

            # fps =  1 / (time.time() - t0)
            # print(fps)

    def _start_capped(self, display, target):
        # start capture loop
        # shift = (x, y, 0, 0)

        handlers = self._handlers

        while not self._stop:
            t0 = time.time()

            for handler in handlers:
                handler.process_image(snapshot(display, handler.ltwh))

            sleep = target + t0 - time.time()

            if sleep < 0:
                sleep = 0
            self._stop_evt.wait(sleep)

            # fps =  1 / (time.time() - t0)
            # print(fps)

    # def initialize(self, image):
    #     e1 = self._left
    #     e2 = self._top
    #     shift = (e1, e2, 0, 0)
    #     dsp = display.Display().screen().root
    #
    #     for handler in self._handlers:
    #         handler.initialize(snapshot(dsp, tuple(map(operator.add, handler.ltwh, shift))))

    def clear(self):
        # with self._lock:
        self.stop()

    def stop(self):
        self._stop = True
        self._stop_evt.set()
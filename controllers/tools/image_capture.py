import threading
import time
from abc import ABC, abstractmethod
import operator

from Xlib import display, X

from PIL import Image

from data import engine

def snapshot(rt, xywh):
    w = xywh[2]
    h = xywh[3]

    #shift by one pixel to compensate for rectangle outline width
    raw = rt.get_image(xywh[0] + 1, xywh[1] + 1, w, h, X.ZPixmap, 0xffffffff)
    image = Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")
    return image

def _to_ltwh(bbox):
    x0, y0, x1, y1 = bbox
    return (x0, y0, x1 - x0, y1 - y0)

class ImagesHandler(ABC):
    @abstractmethod
    def process_images(self, images):
        pass

class ImageHandler(ABC):
    def __init__(self, rectangle):
        self._rectangle = rectangle
        x0, y0, x1, y1 = self._rectangle.bbox
        self._ltwh = (x0, y0, x1 - x0, y1 - y0)

    @property
    def bbox(self):
        return self._rectangle.bbox

    @property
    def ltwh(self):
        return self._ltwh

    @abstractmethod
    def process_image(self, image):
        raise NotImplementedError

class ImageHandlerFactory(ABC):
    def __init__(self):
        self._handlers  = {}

    def clear(self):
        self._handlers.clear()

    def get_handler(self, rectangle):
        if rectangle.id not in self._handlers:
            handler = self._create_handler(rectangle)
            self._handlers[rectangle.id] = handler
            return handler
        return self._handlers[rectangle.id]

    def display(self, image):
        pass

    @abstractmethod
    def _create_handler(self, rectangle):
        raise NotImplementedError

class ImageCaptureTool(object):
    def __init__(self, handler_factory, fps=None):
        """

        Parameters
        ----------
        handler_factory: ImageHandlerFactory
        fps
        """
        self._stop_evt = threading.Event()
        self._stop = False
        self._spf = fps if not fps else 1/fps
        self._handlers = []

        self._fps = 0
        self._running = False
        self._handler_factory = handler_factory

        self._top = None
        self._left = None

        self._display = None
        self._screen = None

    @property
    def fps(self):
        return self._fps

    def capture(self, bbox):
        self._top = bbox[1]
        self._left = bbox[0]
        return snapshot(display.Display().screen().root, _to_ltwh(bbox))

    def _from_bytes(self, data):
        return Image.frombytes("RGB", data.size, data.bgra, "raw", "BGRX")

    def start(self):
        '''

        Parameters
        ----------
        requests: tuple

        Returns
        -------

        '''
        self._stop = False
        self._stop_evt.clear()
        self._display = display.Display()
        self._screen = self._display.screen()
        if self._spf:
            thread = threading.Thread(target=self._start_capped)
        else:
            thread = threading.Thread(target=self._start_uncapped)
        # dispatcher = threading.Thread(target=self._dispatch)
        # dispatcher.start()
        self._running = True
        thread.start()

    def _start_uncapped(self):
        e1 = self._left
        e2 = self._top
        shift = (e1, e2, 0, 0)
        dsp = self._screen.root
        while not self._stop:
            t0 = time.time()
            # with self._lock:
            for handler in self._handlers:
                handler.process_image(snapshot(dsp, tuple(map(operator.add, handler.ltwh, shift))))
            self._fps =  1 / (time.time() - t0)
            # print(self._fps)

    def _start_capped(self):
        # start capture loop
        target = self._spf
        e1 = self._left
        e2 = self._top
        shift = (e1, e2, 0, 0)
        dsp = self._display.screen().root

        while not self._stop:
            t0 = time.time()
            # with self._lock:
            for handler in self._handlers:
                handler.process_image(snapshot(dsp, tuple(map(operator.add, handler.ltwh, shift))))
            sleep = target + t0 - time.time()
            if sleep < 0:
                sleep = 0
            self._stop_evt.wait(sleep)
            self._fps =  1 / (time.time() - t0)
            # print(self._fps)

    def add_handlers(self, rectangles):
        for r in rectangles:
            self._handlers.append(r)

    def clear(self):
        # with self._lock:
        self.stop()
        self._handlers.clear()
        self._handler_factory.clear()

    def stop(self):
        self._elapsed = 0
        self._total_frames = 0
        self._stop = True
        self._stop_evt.set()

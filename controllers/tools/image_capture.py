import threading
import time
import queue
from collections import deque

import mss
from PIL import Image

from models import models
from models.store_managing import POOL

class ImageCaptureTool(models.Model):
    def __init__(self, fps=None):
        super(ImageCaptureTool, self).__init__()
        self._stop_evt = threading.Event()
        self._stop = False
        self._spf = fps if not fps else 1/fps
        self._sct = mss.mss()
        self._queue = deque()
        self._lock = lock = threading.Lock()
        self._new_data = threading.Condition(lock)
        self._fps = 0

    @property
    def fps(self):
        return self._fps

    def start(self, bbox):
        print("Starting Capture...")
        self._stop_evt.clear()
        self._stop = False

        if self._spf:
            thread = threading.Thread(target=self._start_capped, args=(bbox,))
        else:
            thread = threading.Thread(target=self._start_uncapped, args=(bbox,))
        # dispatcher = threading.Thread(target=self._dispatch)
        # dispatcher.start()
        thread.start()

    def _start_uncapped(self, bbox):
        sct = self._sct
        while not self._stop:
            t0 = time.time()
            img = sct.grab(bbox)
            self._notify(img, "new_frame")
            # img = ImageGrab.grab(bbox)
            # POOL.submit(self._enqueue, img, "new_frame") #this must be non-blocking
            # print(self._total_frames/self._elapsed, "FPS!")
            self._fps =  1 / (time.time() - t0)
            print(self._fps)

    def _start_capped(self, bbox):
        # start capture loop
        sct = self._sct
        target = self._spf
        while not self._stop:
            t0 = time.time()
            img = sct.grab(bbox)
            # img = ImageGrab.grab(bbox)
            self._notify(img, "new_frame")
            # POOL.submit(self._notify, img, "new_frame") #this must be non-blocking
            # print(self._total_frames/self._elapsed, "FPS!")
            sleep = target + t0 - time.time()
            if sleep < 0:
                sleep = 0
            self._stop_evt.wait(sleep)
            self._fps =  1 / (time.time() - t0)
            print(self._fps)

    def _notify(self, data, event):
        data = Image.frombytes("RGB", data.size, data.bgra, "raw", "BGRX")
        for obs in self.get_observers(event):
            obs.handle_data(data, self)

    def _dispatch(self):
        while not self._stop:
            with self._new_data:
                try:
                    data, event = self._queue.pop()
                    for obs in self.get_observers(event):
                        obs.handle_data(data, self)
                except IndexError:
                    self._new_data.wait() #wait until new data is available
            # print("fps: {}".format(1 / (time.time() - self._t0)))

    def _enqueue(self, data, event):
        # self._t0 = time.time()
        with self._lock:
            data = Image.frombytes("RGB", data.size, data.bgra, "raw", "BGRX")
            self._queue.appendleft((data, event))
            self._new_data.notify()


    def stop(self):
        self._elapsed = 0
        self._total_frames = 0
        self._stop = True
        self._stop_evt.set() #trigger event in case the loop is sleeping
        print("Stopped Capturing")

    def _events(self):
        return ["new_frame"]

from os import path
from PIL import Image
import threading
import queue

from models import models
from models.store_managing import POOL

EVENTS = ["write", "load"]

class ImageStore(object):
    def __init__(self, dir_, handler):
        super(ImageStore, self).__init__()
        self._dir = path.join(dir_, "/images")
        self._write_cursor = -1 #todo: should be loaded from metadata
        self._handler = handler

    def load(self, idx):
        POOL.submit(self._read, idx)

    def _read(self, idx):
        img = Image.open(path.join(self._dir, str(idx)+".png", "r"))
        self._handler.submit(img, "load")

    def _store(self, image):
        """

        Parameters
        ----------
        image: PIL.Image.Image
        position

        Returns
        -------

        """
        self._write_cursor += 1
        POOL.submit(self._int_store, image, self._write_cursor)

    def _int_store(self, image, position):
        image.save(path.join(self._dir, str(position) + ".png"))
        self._handler.submit(image, "write")

    def handle_data(self, data, emitter):
        self._store(data)

class ImageEvents(models.Model):
    def __init__(self):
        super(ImageEvents, self).__init__()
        self._thread = threading.Thread(target=self._dispatch)
        self._queue = queue.Queue()
        self._stop = False
        self._update_evt = threading.Event()

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop = True

    def _dispatch(self):
        while not self._stop:
            data, event = self._queue.get()
            for obs in self.get_observers(event):
                obs.handle_data(data, self)

    def _notify(self, data, event):
        data = Image.frombytes("RGB", data.size, data.bgra, "raw", "BGRX")
        self._queue.put((data, event))

    def _events(self):
        return ["write", "new_frame", "load"]

    def submit(self, image, event):
        #notify all observers without blocking
        POOL.submit(self._notify, image, event)
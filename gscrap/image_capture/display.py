import tkinter as tk

from PIL import ImageTk

from gscrap.image_capture import capture_loop

class Display(capture_loop.ImageHandler):
    def __init__(self, canvas, rectangle):
        super(Display, self).__init__(rectangle)
        self._editor = canvas
        self._flag = False

        self._rectangle = rectangle
        x0, y0, x1, y1 = self._rectangle.bbox
        self._ltwh = (x0, y0, x1 - x0, y1 - y0)

    @property
    def ltwh(self):
        return self._ltwh

    @property
    def bbox(self):
        return self._rectangle.bbox

    def process_image(self, image):
        if not self._flag:
            bbox = self.bbox
            self._photo_image = img = ImageTk.PhotoImage(image)
            self._image_item = self._editor.create_image(bbox[0], bbox[1], image=img, anchor=tk.NW)
            self._flag = True
        self._photo_image.paste(image)

class DisplayFactory(capture_loop.ImageHandlerFactory):
    def __init__(self, canvas):
        super(DisplayFactory, self).__init__()
        self._canvas = canvas
        self._image_item = None
        self._photo_image = None

    def _create_handler(self, rectangle):
        return Display(self._canvas, rectangle)
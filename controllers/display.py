import tkinter as tk

from PIL import ImageTk

from controllers.tools import image_capture

#todo: the display displays, tracks and stores images. We use image hashing to detect changes
# in images each frame, and only add image if we do not have it already.
# we capture images in each "capturable" rectangle instance

class Display(image_capture.ImageHandler):
    def __init__(self, canvas, rectangle):
        super(Display, self).__init__(rectangle)
        self._editor = canvas
        self._flag = False

    def process_image(self, image):
        if not self._flag:
            bbox = self.bbox
            self._photo_image = img = ImageTk.PhotoImage(image)
            self._image_item = self._editor.create_image(bbox[0], bbox[1], image=img, anchor=tk.NW)
            self._flag = True
        self._photo_image.paste(image)

class DisplayFactory(image_capture.ImageHandlerFactory):
    def __init__(self, canvas):
        super(DisplayFactory, self).__init__()
        self._canvas = canvas
        self._image_item = None
        self._photo_image = None

    def _create_handler(self, rectangle):
        return Display(self._canvas, rectangle)

def display(image, canvas):
    img = ImageTk.PhotoImage(image)
    return img, canvas.create_image(0, 0, image=img, anchor=tk.NW)
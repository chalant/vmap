import tkinter as tk

from PIL import Image, ImageTk

from gscrap.mapping.tools.detection import grid

def update_photo_image(photo_image, image):
    photo_image.paste(image)

class Item(object):
    __slots__ = ['dimensions', 'image_index']

    def __init__(self):
        self.dimensions = None
        self.image_index = None

class ImageRectangle(grid.GridElement):
    def __init__(
            self,
            width,
            height,
            rectangle_id,
            image_id,
            image_index,
            photo_image,
            bbox):

        super(ImageRectangle, self).__init__(width, height)

        self.rectangle_id = rectangle_id
        self.image_id = image_id
        self.image_index = image_index
        self.photo_image = photo_image
        self.bbox = bbox
        self.top_left = bbox[0], bbox[1]
        self.dimensions = (width, height)

class ImageRectangleFactory(grid.ItemFactory):
    def __init__(self, image_buffer):
        self._image_buffer = image_buffer

    def create_element(self, item, canvas, x, y):
        """

        Parameters
        ----------
        item
        canvas: tkinter.Canvas
        x
        y

        Returns
        -------

        """

        dims = item.dimensions
        idx = item.image_index

        im = Image.frombuffer(
            "RGB",
            dims,
            self._image_buffer.get_image(idx),
            "raw")

        photo_image = ImageTk.PhotoImage(im)

        image_id = canvas.create_image(x, y, image=photo_image, anchor=tk.NW)
        bbox = canvas.bbox(image_id)
        rid = canvas.create_rectangle(*bbox)

        return ImageRectangle(dims[0], dims[1], rid, image_id, idx, photo_image, bbox)

    def reload_element(self, canvas, element, x, y):
        image_id = canvas.create_image(x, y, image=element.photo_image, anchor=tk.NW)
        bbox = canvas.bbox(image_id)
        rid = canvas.create_rectangle(*bbox)

        #ovewrite variables
        element.bbox = bbox
        element.rectangle_id = rid
        element.image_id = image_id

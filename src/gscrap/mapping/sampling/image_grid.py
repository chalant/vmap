import tkinter as tk

from PIL import Image, ImageTk

from gscrap.mapping.sampling import grid

def update_photo_image(photo_image, image):
    photo_image.paste(image)

def clear_canvas(grid, canvas, image_rectangles):
    for ir in image_rectangles:
        canvas.delete(ir.rid)
        canvas.delete(ir.image_id)

    grid.reset()

class Item(grid.AbstractItem):
    __slots__ = ['dimensions', 'image_index']

    def __init__(self, dimensions):
        super(Item, self).__init__(dimensions)

        self.dimensions = dimensions
        self.image_index = None

class ImageRectangle(grid.GridElement):
    __slots__ = [
        'rid',
        'image_id',
        'image_index',
        'photo_image',
        'bbox',
        'top_left',
        'dimensions',
        'center',
        'base_outline'
    ]

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

        self.rid = rectangle_id
        self.image_id = image_id
        self.image_index = image_index
        self.photo_image = photo_image
        self.bbox = bbox

        x0, y0, x1, y1 = bbox

        self.top_left = (x0, y0)
        self.center = (int((x1 - x0)/2), int((y1 - y0)/2))

        self.dimensions = (width, height)

        self.base_outline = "black"

class ImageRectangleFactory(grid.ElementFactory):
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

from PIL import Image

import numpy as np

from gscrap.rectangles import rectangles

from gscrap.sampling import samples as spl

from gscrap.mapping.tools.detection.sampling import image_grid as ig
from gscrap.mapping.tools.detection import grid as gd

class BytesImageBuffer(object):
    def __init__(self, buffer, dimensions):
        self._buffer = memoryview(buffer)
        self._dimensions = dimensions

        self._size = size = np.prod(dimensions)

        self._length = length = size * len(buffer) * 3

        self._indices = [i for i in range(length)]

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, values):
        self._indices = values

    def clear(self):
        self._buffer = memoryview(b'')

    def get_image(self, index):
        return bytes(self._buffer[index*3:self._size * (index + 1) * 3])

    def __iter__(self):
        return iter(self._indices)

    def __len__(self):
        return self._length

class ArrayImageBuffer(object):
    def __init__(self):
        self._n = 0
        self._samples = []
        self._indices = []

    def set_samples(self, samples):
        self._samples.clear()
        self._n = n = len(samples)
        self._samples = samples
        self._indices = [i for i in range(n)]

    def get_image(self, index):
        return self._samples[index]

    def clear(self):
        self._samples.clear()

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, values):
        self._indices = values

    def __iter__(self):
        return iter(self._indices)

    def __len__(self):
        return self._n


class Samples(object):
    def __init__(self, buffer, image_grid):
        self._image_grid = image_grid

        self._video_meta = None
        self._capture_zone = None

        self._filters_active = False
        self._samples_buffer = buffer

        def null_callback(event):
            pass

        self._selected_sample = null_callback

        self._items = []
        self._image_rectangles = {}

        image_grid.on_motion(self._on_motion)
        image_grid.on_left_click(self._on_left_click)

        self._rid = None
        self._prev_rid = None

    def get_sample(self, index):
        return self._samples_buffer.get_image(index)

    def apply_filters(self, filters):
        buffer = self._samples_buffer

        for element in self._image_rectangles.values():
            ig.update_photo_image(
                element.photo_image,
                Image.fromarray(filters.apply(
                    self._as_array(buffer.get_image(
                        element.image_index),
                        element.dimensions))))

    def disable_filters(self):
        #disable filters
        buffer = self._samples_buffer

        for element in self._image_rectangles.values():
            ig.update_photo_image(
                element.photo_image,
                Image.frombuffer(
                    "RGB",
                    element.dimensions,
                    buffer.get_image(element.image_index)))

    def compress_samples(self, filters, equal_fn):
        #compress elements by apply filters, and a comparison function

        buffer = self._samples_buffer

        #load in an array so that the index of each element doesn't change
        samples = [s for s in self._load_and_filter(filters, buffer)]

        indices = spl.compress_samples(
            samples,
            len(buffer),
            equal_fn)

        buffer.indices = indices

    def _load_and_filter(self, filters, buffer):
        for element in self._image_rectangles.values():
            yield filters.apply(
                self._as_array(
                    buffer.get_image(element.image_index),
                    element.dimensions))

    def _as_array(self, image, dimensions):
        # return np.asarray(Image.frombytes("RGB", dimensions, image))
        return np.frombuffer(image, np.uint8).reshape(dimensions[1], dimensions[0], 3)

    def load_samples(self, video_metadata, capture_zone):
        #draw samples into the image grid.
        buffer = []
        items = self._items

        items.clear()
        self._samples_buffer.clear()

        idx = 0

        for sample in spl.load_samples(video_metadata, capture_zone.bbox):
            item = ig.Item(capture_zone.dimensions)
            item.image_index = idx

            items.append(item)
            buffer.append(sample)

            idx += 1

        self._capture_zone = capture_zone

        self._samples_buffer.set_samples(buffer)

    def draw(self):
        #initialize canvas

        capture_zone = self._capture_zone

        if capture_zone:
            image_rectangles = self._image_rectangles

            grid = self._image_grid

            ig.clear_canvas(grid, grid.canvas, image_rectangles.values())

            image_rectangles.clear()

            for item in self._items:
                image_rectangles[item.image_index] = grid.add_item(item)

            grid.update()

    def update_draw(self):
        #redraw
        grid = self._image_grid
        image_rectangles = self._image_rectangles

        ig.clear_canvas(grid, grid.canvas, image_rectangles.values())

        #reload compressed elements
        indices = list(set(self._samples_buffer.indices))
        indices.sort()

        grid.reload(self._get_elements(
            indices,
            image_rectangles))

    def _get_elements(self, indices, image_rectangles):
        for i in indices:
            yield image_rectangles[i]

    def _on_motion(self, event):
        image_rectangles = self._image_rectangles

        res = rectangles.find_closest_enclosing(
            self._image_rectangles,
            event.x, event.y)

        canvas = gd.get_canvas(self._image_grid)

        if res:
            rid = res[-1]

            element = image_rectangles[rid]

            pid = self._rid

            if pid != None:
                pel = image_rectangles[pid]
                canvas.itemconfigure(pel.rectangle_id, outline="black")

            canvas.itemconfigure(element.rectangle_id, outline="red")

            self._rid = rid

        else:
            rid = self._rid

            if rid != None:
                pel = image_rectangles[rid]
                canvas.itemconfigure(pel.rectangle_id, outline="black")

    def _on_left_click(self, event):
        rid = self._rid

        if rid != None:
            self._selected_sample(self._image_rectangles[rid].image_index)

    def selected_sample(self, callback):
        self._selected_sample = callback

    def clear(self):
        self._samples_buffer.clear()
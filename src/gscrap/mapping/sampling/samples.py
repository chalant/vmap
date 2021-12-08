from PIL import Image

import numpy as np

from gscrap.mapping.tools import interaction

from gscrap.sampling import samples as spl

from gscrap.mapping.sampling import image_grid as ig


class SampleEvent(object):
    def __init__(self, click_event, sample_index):
        self.clicked = click_event
        self.sample_index = sample_index

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

    def add_sample(self, sample):
        self._samples.append(sample)
        n = self._n
        self._indices.append(n)
        n += 1
        self._n = n

    def set_samples(self, samples):
        self._samples.clear()
        self._n = n = len(samples)
        self._samples = samples
        self._indices = [i for i in range(n)]

    def get_image(self, index):
        return self._samples[index]

    def clear(self):
        self._samples.clear()
        self._indices.clear()
        self._n = 0

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, values):
        self._indices = values

    @property
    def samples(self):
        return self._samples

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

        self._rc_callback = null_callback
        self._lc_callback = null_callback

        self._items = []
        self._image_rectangles = {}
        self._rectangle_instances = {}

        image_grid.on_motion(self._on_motion)
        image_grid.on_left_click(self._on_left_click)
        image_grid.on_right_click(self._on_right_click)

        self._interaction = None

        self._rid = None
        self._prev_rid = None

        self._filters_on = False

        self._dimensions = (0, 0)

        self._batch_index = 0

    @property
    def batch_index(self):
        return self._batch_index

    def get_sample(self, index):
        return self._samples_buffer.get_image(index)

    def get_image_rectangle(self, idx):
        return self._image_rectangles[idx]

    def apply_filters(self, filters):
        self._filters_on = True

        buffer = self._samples_buffer
        image_rectangles = self._image_rectangles

        for idx in list(set(buffer.indices)):
            element = image_rectangles[idx]
            ig.update_photo_image(
                element.photo_image,
                Image.fromarray(filters.apply(
                    self._as_array(buffer.get_image(
                        element.image_index),
                        element.dimensions))))

    def disable_filters(self):
        #disable filters
        self._filters_on = False
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
        for idx in range(len(buffer)):
            yield filters.apply(
                self._as_array(
                    buffer.get_image(idx),
                    self._dimensions))

    def _as_array(self, image, dimensions):
        # return np.asarray(Image.frombytes("RGB", dimensions, image))
        return np.frombuffer(image, np.uint8).reshape(dimensions[1], dimensions[0], 3)

    def load_samples(self, instance_samples_array, capture_zone, from_=0, to=100, draw=False):
        #draw samples into the image grid.
        buffer = self._samples_buffer
        items = self._items

        items.clear()
        buffer.clear()

        #todo: launch multiple processes or threads to optimize sample extraction

        # futures = []
        # res = [[]] * len(capture_zone._siblings)
        #
        # i = 0
        #
        # for bbox in capture_zone.all_bbox:
        #     fut = io.submit(self._load_task, res[i], video_metadata, bbox)
        #     futures.append(fut)
        #
        #     i += 1
        #
        # for fut in futures:
        #     fut.result()

        self._capture_zone = capture_zone

        grid = self._image_grid
        image_rectangles = self._image_rectangles
        rectangle_instances = self._rectangle_instances

        if draw:
            ig.clear_canvas(grid, grid.canvas, image_rectangles.values())
            image_rectangles.clear()

        # for samples in res:

        self._dimensions = dimensions = capture_zone.dimensions

        idx = 0

        for ins in instance_samples_array:
           with ins as source:

            for i in range(from_, to):
                try:
                    sample = source.get_sample(i)

                    item = ig.Item(dimensions)
                    item.image_index = idx

                    items.append(item)
                    buffer.add_sample(sample)

                    if draw:
                        element = grid.add_item(item)

                        image_rectangles[idx] = element

                        rectangle_instances[element.rid] = element

                        idx += 1
                except IndexError:
                    break

        # for bbox in capture_zone.all_bbox:
        #     for sample in spl.load_samples_with_limit(video_metadata, bbox, from_, samples_per_bbox):
        #         item = ig.Item(dimensions)
        #         item.image_index = idx
        #
        #         items.append(item)
        #         buffer.add_sample(sample)
        #
        #         if draw:
        #             element = grid.add_item(item)
        #
        #             image_rectangles[idx] = element
        #
        #             rectangle_instances[element.rid] = element
        #
        #         idx += 1

        grid.update()

        self._interaction = interaction.Interaction(grid.canvas, grid.width, grid.height)


    def _load_task(self, res_array, video_metadata, bbox):
        for sample in spl.load_samples_with_limit(video_metadata, bbox):
            res_array.append(sample)

    def highlight_sample(self, idx):
        self._interaction.set_base_outline(self._image_rectangles[idx])

    def draw(self):
        #initialize canvas

        capture_zone = self._capture_zone

        if capture_zone:
            image_rectangles = self._image_rectangles
            rectangle_instances = self._rectangle_instances

            grid = self._image_grid

            ig.clear_canvas(grid, grid.canvas, image_rectangles.values())

            image_rectangles.clear()
            rectangle_instances.clear()

            indices = list(set(self._samples_buffer.indices))
            indices.sort()

            items = self._items

            for i in indices:
                item = items[i]
                element = grid.add_item(item)
                image_rectangles[item.image_index] = element
                rectangle_instances[element.rid] = element


            grid.update()

            #reset rid
            self._rid = None

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
        if self._interaction:
            self._rid = self._interaction.highlight_outline(
                self._rectangle_instances,
                event)

    def _on_left_click(self, event):
        rid = self._rid

        if rid != None:
            self._lc_callback(SampleEvent(event, self._rectangle_instances[rid].image_index))

    def _on_right_click(self, event):
        rid = self._rid

        if rid != None:
            self._rc_callback(SampleEvent(event, self._rectangle_instances[rid].image_index))

    def on_right_click(self, callback):
        self._rc_callback = callback

    def on_left_click(self, callback):
        self._lc_callback = callback

    def selected_sample(self, callback):
        self._selected_sample = callback

    def clear(self):
        self._samples_buffer.clear()

        image_rectangles = self._image_rectangles

        grid = self._image_grid

        ig.clear_canvas(grid, grid.canvas, image_rectangles.values())

        image_rectangles.clear()
        self._items.clear()
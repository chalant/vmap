import numpy as np

from gscrap.sampling import samples as spl

class BytesSamplesBuffer(object):
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

class ArraySamplesBuffer(object):
    def __init__(self, samples):
        self._n = len(samples)
        self._samples = samples
        self._indices = [i for i in range(len(samples))]

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
    def __init__(self, image_grid):
        self._image_grid = image_grid

        self._video_meta = None
        self._capture_zone = None

        self._filters_active = False
        self._samples_buffer = None

    def get_sample(self, index):
        return self._samples_buffer[index]

    def apply_filters(self, filters):
        for image in self._image_grid.images:
            image.paste(filters.filter_image(self._as_array(image)))

    def compress_samples(self, filters, equal_fn):
        #compress elements by apply filters, and a comparison function

        grid = self._image_grid

        #load in an array so that the index of each element doesn't change
        samples = [s for s in self._load_and_filter(filters)]

        indices = spl.compress_samples(
            samples,
            len(grid.images),
            equal_fn)

        #clear grid
        grid.clear()

        cz = self._capture_zone

        buffer = self._samples_buffer
        buffer.indices = set(indices)

        #redraw every thing

        grid.draw_images(
            (cz.width, cz.height),
            buffer)

    def _load_and_filter(self, filters):
        for image in self._image_grid.images:
            yield filters.filter_image(self._as_array(image))

    def _as_array(self, image):
        return np.frombuffer(image.image).reshape(image.height,image.width, 3)

    def disable_filters(self):
        #disable filters
        for image in self._image_grid.images:
            image.reset()

    def load_samples(self, video_metadata, capture_zone):
        #draw samples into the image grid.
        buffer = []

        for sample in spl.load_samples(video_metadata, capture_zone.bbox):
            buffer.append(sample)

        self._samples_buffer = samples = ArraySamplesBuffer(buffer)

        grid = self._image_grid

        grid.clear()

        grid.draw_images(
            (capture_zone.width, capture_zone.height),
            samples)

    def clear(self):
        self._samples_buffer.clear()
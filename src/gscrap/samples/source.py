import numpy as np

from gscrap.data.images import images as im

from gscrap.filtering import filters


def as_array(image, dimensions):
    # return np.asarray(Image.frombytes("RGB", dimensions, image))
    return np.frombuffer(image, np.uint8).reshape(dimensions[1], dimensions[0], 3)

class AbstractSampleSource(object):
    def get_samples(self):
        return

    def load_samples(self, connection, scene):
        pass

    def add_sample(self):
        pass

class DynamicSampleSource(AbstractSampleSource):
    __slots__ = [
        'scene',
        'label_type',
        'label_class',
        'dimensions',
        'samples',
        'image_buffer',
        'filter_pipeline'
    ]

    def __init__(self,
                 scene,
                 label_type,
                 label_class,
                 dimensions,
                 filter_pipeline):

        self.scene = scene
        self.label_type = label_type
        self.label_class = label_class

        self.dimensions = dimensions
        self.filter_pipeline = filter_pipeline

        self.samples = []

    def get_samples(self):
        filter_pipeline = self.filter_pipeline

        for label, img in self.samples:
            yield label, filters.apply_filters(filter_pipeline, img)

    def load_samples(self, connection, scene):
        samples = self.samples

        samples.clear()

        for meta in im.get_images(
                connection,
                scene,
                self.label_type,
                self.label_class):
            samples.append((
                meta.label['instance_name'],
                as_array(load_image(meta), (meta.width, meta.height))))

class BakedSampleSource(AbstractSampleSource):
    __slots__ = [
        'scene',
        'label_type',
        'label_class',
        'dimensions',
        'samples',
        'image_buffer',
        'filter_pipeline'
    ]

    def __init__(self,
                 scene,
                 label_type,
                 label_class,
                 dimensions,
                 filter_pipeline):

        self.scene = scene
        self.label_type = label_type
        self.label_class = label_class

        self.dimensions = dimensions
        self.filter_pipeline = filter_pipeline

        self.samples = []

    def get_samples(self):
        return iter(self.samples)

    def load_samples(self, connection, scene):

        samples = self.samples
        samples.clear()

        for meta in im.get_images(
                connection,
                scene,
                self.label_type,
                self.label_class):
            samples.append((
                meta.label['instance_name'],
                filters.apply_filters(
                    self.filter_pipeline,
                    as_array(load_image(meta), (meta.width, meta.height)))))


def load_image(meta):
    with open(meta.path, 'rb') as f:
        return f.read()

def delete_sample(sample_source, label):
    """

    Parameters
    ----------
    connection
    sample_source: BakedSampleSource
    label

    Returns
    -------

    """

    samples = sample_source.samples

    i = 0

    for l, img in samples:
        if l == label:
            samples.pop(i)

        i += 1

def get_samples(sample_source):
    return sample_source.get_samples()

def load_samples(sample_source, connection, scene):
    """

    Parameters
    ----------
    sample_source: AbstractSampleSource
    connection

    Returns
    -------

    """

    sample_source.load_samples(connection, scene)

    return sample_source


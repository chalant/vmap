import numpy as np

from gscrap.data.images import images as im

from gscrap.filtering import filters

class SampleSource(object):
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

def load_image(meta):
    with open(meta.path, 'rb') as f:
        return f.read()

def get_samples(sample_source):
    return sample_source.samples

def load_samples(sample_source, connection, scene):
    """

    Parameters
    ----------
    sample_source: SampleSource
    connection

    Returns
    -------

    """

    def as_array(image, dimensions):
        # return np.asarray(Image.frombytes("RGB", dimensions, image))
        return np.frombuffer(image, np.uint8).reshape(dimensions[1], dimensions[0], 3)

    samples = sample_source.samples

    for meta in im.get_images(
            connection,
            scene,
            sample_source.label_type,
            sample_source.label_class):

        samples.append((
            meta.label['instance_name'],
            filters.apply_filters(
                sample_source.filter_pipeline,
                as_array(load_image(meta), (meta.width, meta.height)))))


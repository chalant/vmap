import numpy as np

from gscrap.data.images import images as im
from gscrap.filtering import filters

class SampleSource(object):
    __slots__ = [
        'scene_name',
        'label_type',
        'label_class',
        'dimensions',
        'samples',
        'image_buffer',
        'filter_pipeline'
    ]

    def __init__(self,
                 scene_name,
                 label_type,
                 label_class,
                 dimensions,
                 filter_pipeline):

        self.scene_name = scene_name
        self.label_type = label_type
        self.label_class = label_class

        self.dimensions = dimensions
        self.filter_pipeline = filter_pipeline

        self.samples = []

def load_image(meta):
    with open(meta.path, 'rb') as f:
        return f.read()

def get_samples(sample_source):
    dimensions = sample_source.dimensions

    for label, img in sample_source.samples:
        yield label, np.frombuffer(
            img,
            np.uint8).reshape(
            dimensions[1], dimensions[0], 3)

def load_samples(sample_source, connection):
    """

    Parameters
    ----------
    sample_source: SampleSource
    connection

    Returns
    -------

    """
    samples = sample_source.samples

    for meta in im.get_images(
            connection,
            sample_source.scene_name,
            sample_source.label_type,
            sample_source.label_class):

        samples.append((
            meta.label['instance_name'],
            filters.apply_filters(
                sample_source.filter_pipeline,
                load_image(meta))))


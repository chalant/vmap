import numpy as np

from gscrap.data.images import images as im

from gscrap.samples import image_buffer as ib

class SampleSource(object):
    __slots__ = [
        'project_name',
        'label_type',
        'label_class',
        'dimensions',
        'samples',
        'image_buffer']

    def __init__(self, project_name, label_type, label_class, dimensions):
        self.project_name = project_name
        self.label_type = label_type
        self.label_class = label_class

        self.dimensions = dimensions

        self.samples = []

def load_image(meta):
    with open(meta.path, 'rb') as f:
        return f.read()

def get_samples(sample_source):
    dimensions = sample_source.dimensions

    for label, index in sample_source.samples:
        yield label, np.frombuffer(
            ib.get_image(index),
            np.uint8).reshape(
            dimensions[1], dimensions[0], 3)

def load_samples(sample_source, connection):
    samples = sample_source.samples

    for meta in im.get_images(
            connection,
            sample_source.project_name,
            sample_source.label_type,
            sample_source.label_class):

        # store image into the image buffer (will return the image index)
        index = ib.add_image(load_image(meta))
        samples.append((meta.label['instance_name'], index))


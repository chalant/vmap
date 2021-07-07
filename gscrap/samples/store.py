from gscrap.data import io

from gscrap.data.images import images as im

class SampleData(object):
    __slots__ = ['project_name', 'position', 'width', 'height']

    def __init__(self, project_name, width, height):
        self.project_name = project_name
        self.position = 0
        self.width = width
        self.height = height


def _save_sample(meta, image):
    with open(meta.path, 'wb') as f:
        f.write(image)

def add_sample(sample_data, image, label, connection):
    meta = im.create_image_metadata(
        sample_data.project_name,
        label["label_name"],
        label["label_type"],
        label["instance_name"],
        sample_data.width,
        sample_data.height)

    sample_data.position += 1

    io.submit(_save_sample, meta, image)

    meta.submit(connection)

    return meta



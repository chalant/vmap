from gscrap.data import io

from gscrap.data.images import images as im

class SampleData(object):
    __slots__ = ['scene', 'position', 'width', 'height', 'rectangle_id']

    def __init__(self, scene, width, height, rectangle_id):
        self.scene = scene
        self.position = 0
        self.width = width
        self.height = height
        self.rectangle_id = rectangle_id


def _save_sample(meta, image, connection):
    with open(meta.path, 'wb') as f:
        f.write(image)

    meta.submit(connection)

def add_sample(sample_data, image, label, connection):
    meta = im.create_image_metadata(
        sample_data.scene,
        label["label_name"],
        label["label_type"],
        label["instance_name"],
        sample_data.width,
        sample_data.height,
        sample_data.rectangle_id
    )

    sample_data.position += 1

    # io.submit(_save_sample, meta, image)

    with open(meta.path, 'wb') as f:
        f.write(image)

    return meta



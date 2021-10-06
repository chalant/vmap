class ImageIndex(object):
    def __init__(self):
        self.index = 0

_IMAGES = []
_INDEX = ImageIndex()

def add_image(image):
    _IMAGES.append(image)
    idx = _INDEX.index
    _INDEX.index += 1

    return idx

def get_image(index):
    return _IMAGES[index]

def clear_images():
    _IMAGES.clear()

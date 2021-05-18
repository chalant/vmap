class ImageFilter(object):
    def __init__(self):
        pass

    def different(self, im1, im2):
        raise NotImplementedError

class NullImageFilter(object):
    def different(self, im1, im2):
        return True

#todo: a filter could crop the image as-well...
class Model(object):
    def __init__(self):
        self._filters = []

    def set_filters(self, filters_):
        pass

    def detect(self, img):
        pass

class MatchingModel(Model):
    def __init__(self, images):
        super(MatchingModel, self).__init__()
        self._images = images

    def detect(self, img):
        for im in self._images:
            im.image()
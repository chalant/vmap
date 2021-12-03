class DetectionController(object):
    def __init__(self, container, width, height, on_label_set=None):
        self._detection_view = None

    def view(self):
        return self._detection_view
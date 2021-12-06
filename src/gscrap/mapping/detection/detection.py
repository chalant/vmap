from gscrap.mapping.detection import view

class DetectionController(object):
    def __init__(self, container, width, height, on_label_set=None):
        self._detection_view = view.DetectionView()
        self._scene = None

        self._container = container

    def view(self):
        return self._detection_view

    def set_scene(self, scene):
        self._scene = scene

    def set_label_type(self, *args):
        pass

    def set_label_class(self, *args):
        pass

    def set_capture_zone(self, capture_zone):
        pass

    def filters_update(self, filters):
        pass

    def set_video_metadata(self, video_meta):
        pass

    def disable_video_read(self):
        pass

    def clear_data(self):
        pass
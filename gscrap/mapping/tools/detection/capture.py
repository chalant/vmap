from gscrap.data.rectangles import rectangle_labels
from gscrap.mapping.tools import display

class CaptureZoneFactory(object):
    def __init__(self, project, siblings):
        self._project = project
        self._siblings = siblings

    def create_instance(self, id_, rectangle_instance):
        return CaptureZone(
            id_,
            rectangle_instance,
            self._project,
            self._siblings)

class CaptureZone(display.DisplayItem):
    def __init__(
            self,
            rid,
            rectangle_instance,
            project,
            siblings):

        """
        Parameters
        ----------
        rid:int
        rectangle_instance: gscrap.data.rectangles.rectangles.RectangleInstance
        project: gscrap.projects.projects.Project
        rectangle_labels: gscrap.data.rectangle_labels.RectangleLabels
        """

        super(CaptureZone, self).__init__(rid, rectangle_instance)

        self._rectangle_instance = rectangle_instance
        self._siblings = siblings

        self._image_item = None

        self._project = project

        self._ltwh = xywh = (
            *self._rectangle_instance.top_left,
            self._rectangle_instance.width,
            self._rectangle_instance.height)

        self._in_view = False

        self._dimensions = (xywh[2], xywh[3])

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def top_left(self):
        return self._rectangle_instance.top_left

    @property
    def rectangle(self):
        return self._rectangle_instance.rectangle

    @property
    def rectangle_id(self):
        return self.rectangle.id

    @property
    def instance(self):
        return self._rectangle_instance

    @property
    def width(self):
        return self.instance.width

    @property
    def height(self):
        return self.instance.height

    @property
    def bbox(self):
        return self._rectangle_instance.bbox

    @property
    def xywh(self):
        return self._ltwh

    @property
    def project_name(self):
        return self._project.name

    @property
    def all_bbox(self):
        for sibling in self._siblings:
            yield sibling.bbox

    def get_labels(self, connection):
        return rectangle_labels.get_rectangle_labels(
            connection,
            self._rectangle_instance.rectangle)

    def get_label_instances(self, connection, label_type, label_name):
        return self._project.get_label_instances(connection, label_name, label_type)

    def process_image(self, image):
        """

        Parameters
        ----------
        image: PIL.Image.Image

        Returns
        -------

        """
        pass
        # todo: pass image

    def handle_image(self, image):
        #called by another capture zone if it has observers
        pass

    def clear(self):
        pass

class ObservableCaptureZone(CaptureZone):
    def __init__(self,
                 rid,
                 rectangle_instance,
                 project,
                 thread_pool,
                 hashes,
                 capture_tool,
                 rectangle_labels):
        super(ObservableCaptureZone, self).__init__(
            rid,
            rectangle_instance,
            project,
            thread_pool,
            hashes,
            capture_tool,
            rectangle_labels
        )

        self._observers = []

    def process_image(self, image):
        pass

    def add_observer(self, observer):
        self._observers.append(observer)
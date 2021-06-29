from uuid import uuid4


from gscrap.labeling import labeling as mdl
from gscrap.data.images import images as im

from gscrap.data import engine

class CaptureZone(object):
    def __init__(
            self,
            rid,
            rectangle,
            project,
            thread_pool,
            rectangle_labels):

        """
        Parameters
        ----------
        rid:int
        rectangle: models.rectangles.RectangleInstance
        project: models.projects.Project
        thread_pool: concurrent.futures.ThreadPoolExecutor
        rectangle_labels: models.rectangle_labels.RectangleLabels
        """

        self._rectangle = rectangle
        self._rectangle_labels = rectangle_labels

        self._thread_pool = thread_pool

        self._photo_image = None
        self._image_item = None
        self._rid = rid


        self._project = project

        self._x = 1
        self._y = 1
        self._i = 0

        self._position = 0

        self._ltwh = xywh = (
            *self._rectangle.top_left,
            self._rectangle.width,
            self._rectangle.height)

        self._in_view = False

        self._dimensions = (xywh[2], xywh[3])

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def rid(self):
        return self._rid

    @property
    def top_left(self):
        return self._rectangle.top_left

    @property
    def rectangle(self):
        return self._rectangle.rectangle

    @property
    def instance(self):
        return self._rectangle

    @property
    def width(self):
        return self.instance.width

    @property
    def height(self):
        return self.instance.height

    @property
    def bbox(self):
        return self._rectangle.bbox

    @property
    def xywh(self):
        return self._ltwh

    def add_sample(self, image, label):
        rct = self._rectangle.rectangle

        meta = im.create_image_metadata(
            self._project.name, label["label_name"],
            label["label_type"], label["instance_name"],
            rct.width, rct.height)

        self._thread_pool.submit(self._save_image, meta, image)

        return meta

    @property
    def project_name(self):
        return self._project.name

    def get_labels(self, connection):
        return self._rectangle_labels.get_labels(connection)

    def get_label_instances(self, connection, label_type, label_name):
        return self._project.get_label_instances(connection, label_name, label_type)

    def get_samples(self, connection, label_type, label_name):
        return im.get_images(connection, self.project_name, label_type, label_name)

    def set_detection(self, detection):
        self._detector.set_model(detection)

    def detect(self, image):
        return self._detector.label(image)

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

    def _save_image(self, meta, image):
        with engine.connect() as connection:
            meta.submit(connection)

        image.save(meta.path, 'PNG')

    def clear(self):
        self._position = 0

class ObservableCaptureZone(CaptureZone):
    def __init__(self,
            rid,
            rectangle,
            project,
            thread_pool,
            hashes,
            capture_tool,
            rectangle_labels):
        super(ObservableCaptureZone, self).__init__(
            rid,
            rectangle,
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
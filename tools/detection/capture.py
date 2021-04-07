from uuid import uuid4


import imagehash

from tools import image_capture
from tools.detection.modeling import models as mdl
from models import images as im

from data import engine

class CaptureZone(image_capture.ImagesHandler):
    def __init__(self, rid, rectangle, project, thread_pool, hashes, capture_tool, rectangle_labels):
        """

        Parameters
        ----------
        rid:int
        rectangle: models.rectangles.RectangleInstance
        project: models.projects.Project
        thread_pool: concurrent.futures.ThreadPoolExecutor
        capture_tool: tools.image_capture.ImageCaptureTool
        rectangle_labels: models.rectangle_labels.RectangleLabels
        """

        self._rectangle = rectangle
        self._rectangle_labels = rectangle_labels

        self._thread_pool = thread_pool

        self._photo_image = None
        self._image_item = None
        self._rid = rid

        self._hashes = hashes

        self._project = project

        self._x = 1
        self._y = 1
        self._i = 0

        self._position = 0

        self._ltwh = (*self._rectangle.top_left, self._rectangle.width, self._rectangle.height)

        self._in_view = False

        self._capture_tool = capture_tool

        self._detector = mdl.Detector()

    @property
    def rid(self):
        return self._rid

    @property
    def top_left(self):
        return self._rectangle.top_left

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
    def ltwh(self):
        return self._ltwh

    @property
    def classifiable(self):
        return self._rectangle.rectangle.classifiable

    def capture(self):
        return self._capture_tool.capture_relative(self._ltwh)

    def add_sample(self, image, label, position):
        pn = self._project.name
        rct = self._rectangle.rectangle

        meta = self._create_metadata(
            pn, rct, str(imagehash.average_hash(image)), position, label)

        self._thread_pool.submit(self._save_image, meta, image)

        return meta

    @property
    def project_name(self):
        return self._project.name

    @property
    def in_view(self):
        return self._in_view

    @in_view.setter
    def in_view(self, value):
        self._in_view = value

    def get_labels(self, connection):
        return self._rectangle_labels.get_labels(connection)

    def get_label_instances(self, connection, label_type, label_name):
        return self._project.get_label_instances(connection, label_name, label_type)

    def get_images(self, connection, label_type, label_name):
        connection.execute(label_name=label_name, )
        return self._rectangle.get_images(connection)

    def set_detection(self, detection):
        self._detector.set_detection(detection)

    def detect(self, image):
        return self._detector.detect(image)

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

    def _create_metadata(self, project_name, rct, hash_, position, label):
        return im.ImageMetadata(
            uuid4().hex,
            project_name,
            rct,
            hash_,
            position,
            label)

    def _save_image(self, meta, image):
        with engine.connect() as connection:
            meta.submit(connection)

        image.save(meta.path, 'PNG')

    def clear(self):
        self._position = 0
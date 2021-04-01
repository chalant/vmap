from uuid import uuid4

import tkinter as tk
from PIL import ImageTk, Image
import imagehash

from tools import image_capture
from controllers.rectangles import rectangles as rt
from models import images as im

from data import engine

class CaptureZone(image_capture.ImagesHandler):
    def __init__(self, rid, rectangle, project, thread_pool, hashes, capture_tool):
        """

        Parameters
        ----------
        rid:int
        rectangle: models.rectangles.RectangleInstance
        project: models.projects.Project
        thread_pool: concurrent.futures.ThreadPoolExecutor
        capture_tool: tools.image_capture.ImageCaptureTool
        """
        self._rectangle = rectangle

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
    def in_view(self):
        return self._in_view

    @in_view.setter
    def in_view(self, value):
        self._in_view = value

    @property
    def label_name(self):
        return self._rectangle.label_name

    @property
    def label_type(self):
        return self._rectangle.label_type

    def get_labels(self, connection):
        project = self._project

        rct = self._rectangle
        res = []

        for instance in project.get_label_instances(
                connection, rct.label_name, rct.label_type):
            res.append(instance["instance_name"])

        return tuple(res)

    def get_images(self, connection):
        return self._rectangle.get_images(connection)

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
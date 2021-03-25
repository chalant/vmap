from uuid import uuid4

import tkinter as tk
from PIL import ImageTk, Image
import imagehash

from tools import image_capture
from controllers.rectangles import rectangles as rt
from models import images as im

from data import engine

class CaptureZone(image_capture.ImagesHandler):
    def __init__(self, canvas, rid, rectangle, project, thread_pool, hashes):
        """

        Parameters
        ----------
        canvas: tkinter.Canvas
        rid:int
        rectangle: models.rectangles.RectangleInstance
        project: models.projects.Project
        thread_pool: concurrent.futures.ThreadPoolExecutor
        """

        self._canvas = canvas

        self._rectangle = rectangle

        self._thread_pool = thread_pool

        self._photo_image = None
        self._image_item = None
        self._rid = rid

        self._images = {}
        self._hashes = hashes

        self._project = project

        self._x = 1
        self._y = 1
        self._i = 0

        self._position = 0

        self._ltwh = (*self._rectangle.top_left, self._rectangle.width, self._rectangle.height)
        self._items = []

        self._prev = None
        self._f_rid = None
        self._width = 0

        self._text = None
        self._in_view = False

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

    def initialize(self, connection):

        self._position = pos = 0

        image = None

        rct = self._rectangle

        for im in self._rectangle.get_images(connection):
            p = im.position
            h = im.hash_key

            self._hashes[h] = im

            if p > pos:
                pos = p
                image = im

        self._position = pos + 1

        # if image:
        #     pi = image.get_image()
        # else:
        # pi =

        self._photo_image = pi = ImageTk.PhotoImage(Image.new('RGB', (rct.width, rct.height)))

        x, y = rct.top_left

        self._image_item = self._canvas.create_image(x, y, image=pi, anchor=tk.NW)

    def capture(self):
        return image_capture.capture(self._ltwh)

    def add_sample(self, image, label):
        position = self._position
        pn = self._project.name
        rct = self._rectangle

        position += 1

        meta = self._create_metadata(
            pn, rct, str(imagehash.average_hash(image)), position, label)

        self._thread_pool.submit(self._save_image, meta, image)

        self._position = position

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
        self._position = 0
        position = 0

        for im in self._rectangle.get_images(connection):
            position += 1
            yield im

        self._position = 0


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

    def on_right_click(self, event):
        # res = rt.find_closest_enclosing(self._images, event.x, event.y)
        # project = self._project

        # if res:
        #     with engine.connect() as connection:
        #         self._options = options = tk.Menu(self._capture_canvas, tearoff=False)
        #         self._label_instances = label_instances = tk.Menu(options, tearoff=False)
        #
        #         options.add_cascade(label="Label instances", menu=label_instances)
        #
        #         rid = res[0]
        #         image = self._images[rid]
        #
        #         for instance in project.get_label_instances(
        #                 connection, image.label_name, image.label_type):
        #             name = instance["instance_name"]
        #             label_instances.add_command(
        #                 label=name,
        #                 command=partial(self._on_set_label_instance, image, instance))
        #
        #         options.tk_popup(event.x_root, event.y_root)

        pass

    def on_motion(self, event):
        #todo: this is for labeling => should be handled by the sampling view

        canvas = self._capture_canvas

        x = event.x + canvas.xview()[0] * (self._width)
        y = event.y + canvas.yview()[0] * (self._y + 1 + self._rectangle.height)

        images = self._images

        res = rt.find_closest_enclosing(images, x, y)

        if res:
            self._f_rid = rid = res[0]
            self._unbind(canvas)

            rct = rt.get_rectangle(images, rid)
            self._text = canvas.create_text(*rct.center, text=rct.label)
            canvas.itemconfigure(rct.rid, outline="red")
            self._prev = rid
        else:
            self._unbind(canvas)
            self._f_rid = None

    def _unbind(self, canvas):
        prev = self._prev
        text = self._text

        if prev:
            canvas.itemconfigure(prev, outline="black")

        if text:
            canvas.delete(text)
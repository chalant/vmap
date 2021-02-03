from concurrent import futures

import tkinter as tk
from PIL import ImageTk, Image

from controllers.tools import image_capture
from controllers.rectangles import rectangles as rt

from data import engine

class ImageRectangle(object):
    def __init__(self, rid, rectangle):
        """

        Parameters
        ----------
        rid
        rectangle: models.rectangles.RectangleInstance
        """
        self._rid = rid
        self._rectangle = rectangle

    @property
    def rid(self):
        return self._rid

    @property
    def top_left(self):
        return self._rectangle.top_left

    @property
    def bbox(self):
        return self._rectangle.bbox


class CaptureZone(object):
    def __init__(self, canvas, rid, rectangle):
        """

        Parameters
        ----------
        canvas
        rid:
        rectangle: models.rectangles.RectangleInstance
        """

        self._canvas = canvas
        self._rectangle = rectangle

        self._photo_image = None
        self._image_item = None
        self._rid = rid

    @property
    def rid(self):
        return self._rid

    @property
    def top_left(self):
        return self._rectangle.top_left

    def instance(self):
        return self._rectangle

    @property
    def bbox(self):
        return self._rectangle.bbox

    def display_image(self, image):
        self._photo_image.paste(image)

    def initialize(self, image):
        self._photo_image = ImageTk.PhotoImage(image)
        self._image_item = self._canvas.create_image(image)

class LabelInstanceMapper(image_capture.ImagesHandler):
    def __init__(self, container, canvas):
        """

        Parameters
        ----------
        container: tkinter.Frame
        canvas: tkinter.Canvas
        """
        self._images = {}

        self._canvas = canvas
        self._container = container

        self._capture_frame = frame = tk.LabelFrame(container, text="Captures")
        self._capture_canvas = cpt = tk.Canvas(frame)

        frame.pack()
        cpt.pack()

        self._instances = {}
        self._rectangles = {}

        self._prev = None
        self._rid = None

        self._items = []

        self._project = None

        self._thread_pool = futures.ThreadPoolExecutor(10)

        self._drawn = False
        self._drawn_instance = None

        self._options = options = tk.Menu(cpt, tearoff=False)

        options.add_command(
            "Set label instance",
            command=self._on_set_label_instance)

        self._selected_image = None

    def start(self, project, connection, capture_state):
        """

        Parameters
        ----------
        project: models.projects.Project
        connection:
        capture_state: controllers.states.CaptureState


        Returns
        -------
        None
        """

        # todo: load latest captured images, or use template image if no images were found and display
        #  them

        canvas = self._canvas
        instances = self._instances

        self._project = project

        for rct in project.get_rectangles(connection):
            # filter rectangle that we can capture
            if rct.capture:
                for instance in rct.get_instances(connection):
                    rid = canvas.create_rectangle(*instance.bbox, width=1, dash=(4,1))
                    instances[rid] = CaptureZone(canvas, rid, instance)

            capture_state.initialize(instances.values())

        canvas.bind("<Motion>", self.on_motion)
        canvas.bind("<Button-1>", self.on_left_click)

    def clear(self):
        canvas = self._canvas
        instances = self._instances

        for rid in instances.keys():
            canvas.delete(rid)

        instances.clear()
        self._rectangles.clear()
        canvas.unbind("<Motion>")

    def process_images(self, images):
        # todo: for each image, hash it, check if we've already captured it, then store it...
        pass

    def get_capture_zones(self):
        return self._instances.values()

    def _unbind(self, canvas):
        prev = self._prev

        if prev:
            canvas.itemconfigure(prev, outline="black")

    def on_motion(self, event):
        #todo: should highlight siblings of the the rectangle we hover on.

        res = rt.find_closest_enclosing(self._instances, event.x, event.y)

        canvas = self._canvas

        if res:
            self._rid = res
            self._unbind(canvas)

            r = res[0]
            rct = rt.get_rectangle(self._instances, r)
            canvas.itemconfigure(rct.rid, outline="red")
            self._prev = r
        else:
            self._unbind(canvas)

    def on_left_click(self, event):
        # todo: start the label instancer: the instancer displays pictures that are being
        #  captured. We can hover on the images and set there labels.
        #  if we click on a new capture area, save, clear, and draw the new capture areas captured
        #  images.
        #  Images are "appended" in a grid each time it is captured.

        rid = self._rid

        project = self._project

        if rid:
            rct = rt.get_rectangle(self._rectangles, rid)

            if not self._drawn_instance:
                with engine.connect() as connection:
                    self._draw_images(connection, rct, project, 3)

            instance_id = rct.instance.id

            if rct.instance.id != self._drawn_instance:

                #clear all images
                for im in self._images.keys():
                    self._capture_canvas.delete(im)

                self._images.clear()

                with engine.connect() as connection:
                    self._draw_images(connection, rct, project, 3)

                self._drawn_instance = instance_id

                self._capture_canvas.unbind("<Button-3>")
                self._capture_canvas.bind("<Button-3>", self._on_right_click)

    def _draw_images(self, connection, rct, project, max_row):
        x = 1
        y = 1

        # submit draw threads
        i = 0

        canvas = self._capture_canvas
        pool = self._thread_pool

        for meta in project.get_image_metadata(connection, rct.instance.id):
            pool.submit(
                self._draw,
                canvas,
                rct,
                meta["image_path"],
                x, y)

            i += 1
            x += rct.width

            if i == max_row:
                i = 0
                y += rct.height

    def _draw(self, canvas, rct, image_path, x, y):
        images = self._images

        image = ImageTk.PhotoImage(Image.open(image_path, formats=("PNG",)))
        rid = canvas.create_image(x, y, image)

        images[rid] = ImageRectangle(rid, rct)

    def _on_right_click(self, event):
        res = rt.find_closest_enclosing(self._images, event.x, event.y)
        if res:
            rid = res[0]
            image = self._images[rid]
            # todo: show menu (set label instance, delete etc.)

    def _on_set_label_instance(self):
        # todo: display a list of available label instances for the image
        pass

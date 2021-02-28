from functools import partial
from concurrent import futures
from uuid import uuid4
import math

import tkinter as tk
from PIL import ImageTk, Image
import imagehash


from controllers.tools import image_capture, preprocess
from controllers.rectangles import rectangles as rt

from models import images

from data import engine

class ImageRectangle(object):
    def __init__(self, rid, iid, cz, bbox, image_metadata):
        """

        Parameters
        ----------
        rid: int
        iid: int
        cz: CaptureZone
        bbox: tuple
        image_metadata: models.images.ImageMetadata
        """

        self._rid = rid
        self._cz = cz
        self._bbox = bbox
        self._iid = iid
        self._meta = image_metadata

        self._changed = False

    @property
    def rid(self):
        return self._rid

    @property
    def iid(self):
        return self._iid

    @property
    def top_left(self):
        bbox = self._bbox
        return bbox[0], bbox[1]

    @property
    def center(self):
        x0, y0, x1, y1 = self._bbox
        return (x0 + x1)/2, (y0 + y1)/2

    @property
    def bbox(self):
        return self._bbox

    @property
    def label_type(self):
        return self._cz.label_type

    @property
    def label_name(self):
        return self._cz.label_name

    @property
    def label_instance_name(self):
        return self._meta.label_instance_name

    @label_instance_name.setter
    def label_instance_name(self, value):
        self._changed = True
        self._meta.label_instance_name = value

    def submit(self, connection):
        if self._changed:
            self._meta.submit(connection)


class CaptureZone(image_capture.ImagesHandler):
    def __init__(self, canvas, capture_canvas, rid, rectangle, project, thread_pool, hashes):
        """

        Parameters
        ----------
        canvas: tkinter.Canvas
        capture_canvas: tkinter.Canvas
        rid:int
        rectangle: models.rectangles.RectangleInstance
        project: models.projects.Project
        thread_pool: concurrent.futures.ThreadPoolExecutor
        """

        self._canvas = canvas
        self._capture_canvas = capture_canvas

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

    @property
    def label_name(self):
        return self._rectangle.label_name

    @property
    def label_type(self):
        return self._rectangle.label_type

    def process_image(self, image):
        """

        Parameters
        ----------
        image: PIL.Image.Image

        Returns
        -------

        """
        hsh = str(imagehash.average_hash(image))
        hashes = self._hashes
        position = self._position
        pn = self._project.name
        rct = self._rectangle

        im = preprocess.preprocess_image(image)

        if hsh not in hashes:
            #create new image instance

            # canvas = self._capture_canvas
            if self._i == 3:
                self._i = 1

                y = self._y + rct.height
                x = 1
            else:
                self._i += 1

                x = self._x + rct.width
                y = self._y

            self._x = x
            self._y = y

            position += 1

            rid = self._image_item

            #todo: create image in canvas
            #self._images[rid] = ImageRectangle(rid, self)
            # todo: we need to draw (append) the image if we're in picture display mode...
            #  also, only draw only what is "viewable"

            #todo: update detect image after pre-processing. Note: Detection depends on the task:
            # could be a number, a rank suit, etc. Ex: if we want to detect POT size, we will
            # use tesseract for instance. Pre-processing might depend on the detection model.

            self._thread_pool.submit(
                self._save_image,
                hashes,
                pn,
                rct.id,
                im,
                hsh,
                position)

        self._photo_image.paste(im) # display image

        self._position = position



    def _save_image(self, hashes, project_name, rct_id, image, hash_, position):
        img = images.ImageMetadata(
            uuid4().hex,
            project_name,
            rct_id,
            hash_,
            position)

        hashes[hash_] = img

        with engine.connect() as connection:
            img.submit(connection)

        image.save(img.path, 'PNG')

    def draw_captured_images(self, connection, max_row, step):
        #todo: draw outlines around images

        #todo: draw what is viewable in the capture canvas, and dynamically load new images as we
        # scroll.

        x = step
        y = 1

        # submit draw threads
        i = 0

        canvas = self._capture_canvas

        images = self._images

        rct = self._rectangle
        m = 0

        for meta in rct.get_images(connection):
            # pool.submit(
            #     self._load_draw,
            #     images,
            #     canvas,
            #     self,
            #     meta["image_id"],
            #     x, y)

            self._load_draw(
                images,
                canvas,
                self,
                meta,
                x, y)

            i += 1
            x += rct.width + step

            if i == max_row:
                i = 0
                y += rct.height + 2
                m = x - step
                x = step

        self._x = x
        self._y = y
        self._i = i

        canvas.config(scrollregion=(0, 0, m, y + rct.height + 1))
        self._width = m
        # canvas.update()

    def _load_draw(self, images, canvas, rct, image_meta, x, y):
        image = image_meta.get_image()

        iid = canvas.create_image(x, y, image=image, anchor=tk.NW)
        bbox = canvas.bbox(iid)
        rid = canvas.create_rectangle(*bbox)

        self._items.append(image)

        images[rid] = ImageRectangle(rid, iid, rct, bbox, image_meta)

    def clear(self):
        with engine.connect() as connection:
            images = self._images
            capture_canvas = self._capture_canvas
            # clear all images
            for k, im in images.items():
                capture_canvas.delete(k)
                capture_canvas.delete(im.iid)
                #submit any changes to the image
                im.submit(connection)

            images.clear()

            self._items.clear()

            self._x = 1
            self._y = 1
            self._i = 0

    def on_right_click(self, event):
        res = rt.find_closest_enclosing(self._images, event.x, event.y)
        project = self._project

        if res:
            with engine.connect() as connection:
                self._options = options = tk.Menu(self._capture_canvas, tearoff=False)
                self._label_instances = label_instances = tk.Menu(options, tearoff=False)

                options.add_cascade(label="Label instances", menu=label_instances)

                rid = res[0]
                image = self._images[rid]

                for instance in project.get_label_instances(
                        connection, image.label_name, image.label_type):
                    name = instance["instance_name"]
                    label_instances.add_command(
                        label=name,
                        command=partial(self._on_set_label_instance, image, instance))

                options.tk_popup(event.x_root, event.y_root)

    def on_motion(self, event):
        canvas = self._capture_canvas

        x = event.x + canvas.xview()[0] * (self._width)
        y = event.y + canvas.yview()[0] * (self._y + 1 + self._rectangle.height)

        canvas = self._capture_canvas
        images = self._images

        res = rt.find_closest_enclosing(images, x, y)

        if res:
            self._f_rid = rid = res[0]
            self._unbind(canvas)

            rct = rt.get_rectangle(images, rid)
            self._text = canvas.create_text(*rct.center, text=rct.label_instance_name)
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

    def _on_set_label_instance(self, image_rectangle, label_instance):
        image_rectangle.label_instance_name = label_instance["instance_name"]



class LabelInstanceMapper(object):
    def __init__(self, container, canvas):
        """

        Parameters
        ----------
        container: tkinter.Frame
        canvas: tkinter.Canvas
        """

        self._canvas = canvas
        self._container = container


        self._capture_frame = frame = tk.LabelFrame(container, text="Samples")

        self._capture_canvas = capture_canvas = tk.Canvas(frame)
        self._filter_canvas = filter_canvas = tk.Canvas(container)

        #todo: display parameters when we click on the preprocessing tools (blur, threshold, zoom, grey)

        self._commands = commands = tk.Frame(frame)
        self._menu = menu = tk.LabelFrame(frame, text="Filters")

        #captures an image of the selected rectangle.
        self._sample = sample = tk.Button(commands, text="Sample")

        self._add_filter = add_filter = tk.Menubutton(menu, text="Add")
        self._open_filters = open_filters = tk.Menubutton(menu, text="Open")

        self._filter_menu = fm = tk.Menu(add_filter, tearoff=0)

        fm.add_command(label="Blur")
        fm.add_command(label="Threshold")
        fm.add_command(label="Zoom")
        fm.add_command(label="Color")
        add_filter.config(menu=fm)

        self._parameter_frame = pr = tk.Frame(container)

        self._v_scroll_bar = vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        self._h_scroll_bar = hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        vbar.config(command=capture_canvas.yview)
        hbar.config(command=capture_canvas.xview)

        self._count = 0

        capture_canvas.config(yscrollcommand=vbar.set)
        capture_canvas.config(xscrollcomman=hbar.set)

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)

        capture_canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        capture_canvas.bind("<Button-4>", self._on_mouse_wheel)
        capture_canvas.bind("<Button-5>", self._on_mouse_wheel)


        frame.pack()
        menu.pack(side=tk.RIGHT, fill=tk.Y)
        add_filter.pack()
        open_filters.pack()


        capture_canvas.pack()
        sample.pack()

        pr.pack()
        commands.pack()

        self._instances = {}

        self._prev = None
        self._rid = None

        self._items = []
        self._hashes = {}

        self._project = None

        self._thread_pool = futures.ThreadPoolExecutor(10)

        self._drawn_instance = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._height = 0
        self._width = 0

    def _on_mouse_wheel(self, event):
        # todo: should create this function as a utility function
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._count -= 1
            self._capture_canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self._count += 1
            self._capture_canvas.yview_scroll(-1, "units")

    def start(self, project, connection, capture_state, main_frame):
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

        canvas = self._canvas

        self._height = main_frame.height
        self._width = main_frame.width

        instances = self._instances
        capture_canvas = self._capture_canvas

        self._project = project
        pool = self._thread_pool

        hashes = self._hashes

        for rct in project.get_rectangles(connection):
            # filter cz that we can capture
            if rct.capture:
                for instance in rct.get_instances(connection):
                    x0, y0, x1, y1 = instance.bbox
                    rid = canvas.create_rectangle(x0-1, y0-1, x1, y1, width=1, dash=(4, 1))
                    instances[rid] = cz = CaptureZone(
                        canvas,
                        capture_canvas,
                        rid,
                        instance,
                        project,
                        pool,
                        hashes)

                    cz.initialize(connection)
            #todo: load the latest captured image and display it in the box
            capture_state.initialize(instances.values())

        canvas.bind("<Motion>", self.on_motion)
        canvas.bind("<Button-1>", self.on_left_click)

    def clear(self):
        canvas = self._canvas
        instances = self._instances

        for rid in instances.keys():
            canvas.delete(rid)

        self._drawn_instance = None

        instances.clear()
        canvas.unbind("<Motion>")

    def get_capture_zones(self):
        return self._instances.values()

    def _unbind(self, canvas):
        prev = self._prev

        if prev:
            canvas.itemconfigure(prev, outline="black")

    def on_motion(self, event):
        #todo: should highlight siblings of the the cz we hover on.
        canvas = self._canvas

        x = event.x + canvas.xview()[0] * self._width
        y = event.y + canvas.yview()[0] * self._height

        instances = self._instances

        res = rt.find_closest_enclosing(instances, x, y)

        if res:
            self._rid = rid = res[0]
            self._unbind(canvas)

            rct = rt.get_rectangle(instances, rid)
            canvas.itemconfigure(rct.rid, outline="red")
            self._prev = rid
        else:
            self._unbind(canvas)
            self._rid = None

    def on_left_click(self, event):
        rid = self._rid

        if rid:

            rct = rt.get_rectangle(self._instances, rid)
            canvas = self._capture_canvas

            w = canvas.winfo_width()

            max_row = math.floor(w / rct.width)
            t = math.floor((w - (rct.width * max_row)) / max_row)

            #todo: we need the scroll region (the sum heights for vbar)

            if not self._drawn_instance:
                with engine.connect() as connection:
                    rct.draw_captured_images(connection, max_row, t)
                    self._drawn_instance = rid

                    # self._v_scroll_bar.update()
                    # self._h_scroll_bar.update()
                    canvas.bind("<Motion>", rct.on_motion)
                    canvas.bind("<Button-3>", rct.on_right_click)

            elif rid != self._drawn_instance:
                rt.get_rectangle(self._instances, self._drawn_instance).clear()
                # rct.clear() #clear drawn elements

                with engine.connect() as connection:
                    rct.draw_captured_images(connection, max_row, t)

                # self._v_scroll_bar.update()
                # self._h_scroll_bar.update()

                self._drawn_instance = rid

                canvas.unbind("<Button-3>")
                canvas.unbind("<Motion>")

                canvas.bind("<Motion>", rct.on_motion)
                canvas.bind("<Button-3>", rct.on_right_click)
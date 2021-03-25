import math

import tkinter as tk

from PIL import ImageTk

from controllers.rectangles import rectangles as rt

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
    def label(self):
        return self._meta.label

    def submit(self, connection):
        if self._changed:
            self._meta.submit(connection)

class SamplesModel(object):
    def __init__(self):
        self._capture_zone = None
        self._sample_observers = []
        self._cz_obs = []

        self._position = 0

    def set_capture_zone(self, capture_zone):
        """

        Parameters
        ----------
        capture_zone: tools.detection.capture.CaptureZone

        Returns
        -------

        """
        self._capture_zone = capture_zone

        with engine.connect() as connection:
            for obs in self._cz_obs:
                obs.capture_zone_update(connection, capture_zone)

    def add_sample(self, image, label):
        cz = self._capture_zone

        if cz:
            meta = cz.add_sample(image, label)
            for obs in self._sample_observers:
                obs.new_sample(image, meta)

    def get_samples(self):
        with engine.connect() as connection:
            return self._capture_zone.get_images(connection)

    def add_sample_observer(self, observer):
        self._sample_observers.append(observer)

    def add_capture_zone_observer(self, observer):
        self._cz_obs.append(observer)

class SamplesView(object):
    def __init__(self, controller, model):
        self._model = model
        self._controller = controller

        self._frame = None
        self._canvas = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._images = {}

        self._width = 0
        self._height = 0

        self._motion_bind = False

    def clear(self):
        images = self._images
        capture_canvas = self._canvas

        # clear all images
        for k, im in images.items():
            capture_canvas.delete(k)
            capture_canvas.delete(im.iid)

        images.clear()

        self._x = 1
        self._y = 1
        self._i = 0

    def render(self, container):
        self._frame = frame = tk.LabelFrame(container, text="Samples")
        self._canvas = canvas = tk.Canvas(frame)

        self._cfv_sb = cfv_sb = tk.Scrollbar(frame, orient=tk.VERTICAL)
        self._cfh_sb = cfh_sb = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        cfv_sb.config(command=canvas.yview)
        cfh_sb.config(command=canvas.xview)

        canvas.config(yscrollcommand=cfv_sb.set)
        canvas.config(xscrollcomman=cfh_sb.set)

        cfv_sb.pack(side=tk.RIGHT, fill=tk.Y)
        cfh_sb.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)
        canvas.bind("<Button-5>", self._on_mouse_wheel)

        frame.pack(fill=tk.X)
        canvas.pack(fill=tk.BOTH)

        return frame

    def deactivate(self):
        self._frame["state"] = tk.DISABLED

    def activate(self):
        self._frame["state"] = tk.ACTIVE

    def capture_zone_update(self, capture_zone):
        """

        Parameters
        ----------
        capture_zone: tools.detection.capture.CaptureZone

        Returns
        -------

        """

        images = self._images
        canvas = self._canvas

        w = canvas.winfo_width()

        max_row = math.floor(w / capture_zone.width)
        step = math.floor((w - (capture_zone.width * max_row)) / max_row)
        max_row = math.floor(w / capture_zone.width)

        x = step
        y = 1

        i = 0
        m = 0
        h = 0
        wd = 0

        for meta in self._model.get_samples():
            self._load_draw(
                images,
                canvas,
                meta,
                x, y)

            i += 1
            x += meta.width + step

            if i == max_row:
                i = 0
                y += meta.height + 2
                m = x - step
                x = step

            h = meta.height
            wd = meta.width

        self._x = x
        self._y = y
        self._i = i

        canvas.config(scrollregion=(0, 0, m, y + h + 1))

        if not self._motion_bind:
            canvas.bind("<Motion>", self._on_motion)

        self._width = wd
        self._height = h

    def filters_update(self, filters):
        # todo: apply filters to image (if filtering is activated)
        pass

    def disable_filters(self):
        pass

    def new_sample(self, image, image_meta):
        # canvas = self._capture_canvas
        i = self._i

        if i == 3:
            i = 1

            y = self._y + image.height
            x = 1
        else:
            i += 1

            x = self._x + image.width
            y = self._y

        self._x = x
        self._y = y
        self._i = i

        self._draw(
            self._images,
            image,
            self._canvas,
            image_meta,
            x, y)

    def _on_motion(self, event):
        canvas = self._canvas
        images = self._images

        x = event.x + canvas.xview()[0] * (self._width)
        y = event.y + canvas.yview()[0] * (self._y + 1 + self._height)

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

    def _draw(self, images, image, canvas, image_meta, x, y):
        iid = canvas.create_image(x, y, image=image, anchor=tk.NW)
        bbox = canvas.bbox(iid)
        rid = canvas.create_rectangle(*bbox)

        images[rid] = ImageRectangle(rid, iid, image_meta.rectangle, bbox, image_meta)

    def _load_draw(self, images, canvas, image_meta, x, y):
        image = ImageTk.PhotoImage(image_meta.get_image())

        self._draw(images, image, canvas, image_meta, x, y)

    def _on_mouse_wheel(self, event):
        # todo: should create this function as a utility function
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self._canvas.yview_scroll(-1, "units")


class SamplesController(object):
    def __init__(self, model):
        self._model = model
        self._view = SamplesView(self, model)

    def view(self):
        return self._view

    def capture_zone_update(self, connection, capture_zone):
        if not capture_zone.classifiable:
            self._view.deactivate() #deactive sampling
        else:
            self._view.activate()

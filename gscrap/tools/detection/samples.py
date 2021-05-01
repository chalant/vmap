import math

import tkinter as tk

import threading

from PIL import ImageTk, Image
import numpy as np

from controllers.rectangles import rectangles as rt

from data import engine


class ImageRectangle(object):
    def __init__(self, rid, iid, cz, bbox, image_metadata, image, photo_image):
        """

        Parameters
        ----------
        rid: int
        iid: int
        cz: CaptureZone
        bbox: tuple
        image_metadata: models.images.ImageMetadata
        """

        self.rid = rid
        self._cz = cz
        self.bbox = bbox
        self.iid = iid
        self._meta = image_metadata
        self.image = image
        self.photo_image = photo_image

        self._changed = False

    @property
    def width(self):
        return self._meta.width

    @property
    def height(self):
        return self._meta.height

    @property
    def rectangle(self):
        return self._meta.rectangle

    @property
    def position(self):
        return self._meta.position

    @position.setter
    def position(self, value):
        meta = self._meta
        if meta.position != value:
            self._changed = True
            meta.position = value

    @property
    def top_left(self):
        bbox = self.bbox
        return bbox[0], bbox[1]

    @property
    def center(self):
        x0, y0, x1, y1 = self.bbox
        return (x0 + x1)/2, (y0 + y1)/2

    @property
    def label_type(self):
        return self._cz.label_type

    @property
    def label_name(self):
        return self._cz.label_name

    @property
    def label(self):
        return self._meta.label["instance_name"]

    def submit(self, connection):
        if self._changed:
            self._meta.submit(connection)

    def delete(self, connection):
        self._meta.delete_image(connection)

    def get_image(self):
        return self.image

class SamplesModel(object):
    def __init__(self):
        self._capture_zone = None
        self._sample_observers = []
        self._cz_obs = []

        self.position = 0

    def add_sample(self, image, label):
        cz = self._capture_zone

        position = self.position
        position += 1

        if cz:
            meta = cz.add_sample(image, label, position)
            for obs in self._sample_observers:
                obs.new_sample(image, meta)

        self.position = position

    def get_samples(self, connection):
        position = 0

        for im in self._capture_zone.get_images(connection):
            position += 1
            yield im

        self.position = position

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
        self._rc_menu = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._images = {}
        self._items = []

        self._width = 0
        self._height = 0

        self._motion_bind = False

        self._prev = None
        self._text = None
        self._f_rid = None

        self._max_row = None
        self._step = None

        self._samples = None

        self._position = 0
        self._image_observers = []

    def clear(self):
        images = self._images
        capture_canvas = self._canvas

        # clear all images
        for k, im in images.items():
            capture_canvas.delete(k)
            capture_canvas.delete(im.iid)

        images.clear()
        self._items.clear()

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
        canvas.config(xscrollcommand=cfh_sb.set)

        cfv_sb.pack(side=tk.RIGHT, fill=tk.Y)
        cfh_sb.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)
        canvas.bind("<Button-5>", self._on_mouse_wheel)

        canvas.bind("<Button-3>", self._on_right_click)

        frame.pack(fill=tk.X)
        canvas.pack(fill=tk.BOTH)

        return frame

    def deactivate(self):
        self._canvas["state"] = tk.DISABLED

    def activate(self):
        self._canvas["state"] = tk.NORMAL

    def samples_update(self, samples):
        """

        Parameters
        ----------
        samples: tools.detection.sampling.Samples

        Returns
        -------

        """

        with engine.connect() as connection:
            self._draw_samples(samples.width, samples.get_images(connection))

        if not self._motion_bind:
            self._canvas.bind("<Motion>", self._on_motion)
            self._motion_bind = True

    def _draw_samples(self, width, images_meta, create=True):
        images = self._images
        canvas = self._canvas
        items = self._items

        images.clear() #clear previous data

        w = canvas.winfo_width()

        max_row = math.floor(w / width)
        step = math.floor((w - (width * max_row)) / max_row)

        x = step
        y = 1

        i = 0
        m = 0
        h = 0
        wd = 0

        if create:
            fn = self._load_draw
        else:
            fn = self._update_draw

        for meta in images_meta:
            img = fn(images, canvas, meta, x, y)

            if create:
                items.append(img)  # store images in order

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

        mw = canvas.winfo_width()
        mh = canvas.winfo_height()

        if y + h + 1 > mh:
            self._mh = y + h + 1
            canvas.configure(scrollregion=(0, 0, mw, y + h + 1))
        else:
            self._mh = mh
            canvas.configure(scrollregion=(0, 0, mw, mh))

        self._width = wd
        self._height = h
        self._max_row = max_row
        self._step = step

        for obs in self._image_observers:
            obs.images_update(images.values())


    def enable_filters(self, filters):
        for image in self._images.values():
            image.photo_image.paste(Image.fromarray(filters.filter_image(np.asarray(image.image))))

    def disable_filters(self, filters):
        for image in self._images.values():
            image.photo_image.paste(image.image)

    def new_sample(self, image, image_meta):
        canvas = self._canvas

        w = canvas.winfo_width()

        if not self._max_row:
            self._max_row = math.floor(w / image_meta.width)

        max_row = self._max_row

        if not self._step:
            self._step = math.floor((w - (w* max_row)) / max_row)

        step = self._step

        i = self._i

        x = self._x
        y = self._y

        self._items.append(
            self._create_draw(
                self._images,
                image,
                self._canvas,
                image_meta,
                x, y))

        i += 1

        x = self._x + image_meta.width + step
        y = self._y

        if i == max_row:
            i = 0
            y = self._y + image_meta.height + 2
            x = step

        self._x = x
        self._y = y
        self._i = i
        self._width = image_meta.width
        self._height = image_meta.height

        mw = canvas.winfo_width()
        mh = canvas.winfo_height()
        h = image_meta.height

        if y + h + 1 > mh:
            self._mh = y + h + 1
            canvas.configure(scrollregion=(0, 0, mw, y + h + 1))
        else:
            self._mh = mh
            canvas.configure(scrollregion=(0, 0, mw, mh))

    def add_image_observer(self, observer):
        self._image_observers.append(observer)

    def _on_motion(self, event):
        canvas = self._canvas
        images = self._images

        # x = event.x + canvas.xview()[0] * (self._x)
        x = event.x
        y = event.y + canvas.yview()[0] * self._mh

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

    def _create_draw(self, images, image, canvas, image_meta, x, y):
        ph_im = ImageTk.PhotoImage(image)
        iid = canvas.create_image(x, y, image=ph_im, anchor=tk.NW)
        bbox = canvas.bbox(iid)
        rid = canvas.create_rectangle(*bbox)

        images[rid] = img = self._create_image_rectangle(
            rid,
            iid,
            image_meta,
            bbox,
            image,
            ph_im)

        return img

    def _update_draw(self, images, canvas, image_rectangle, x, y):
        iid = canvas.create_image(x, y, image=image_rectangle.photo_image, anchor=tk.NW)
        bbox = canvas.bbox(iid)
        rid = canvas.create_rectangle(*bbox)

        images[rid] = img = self._update_image_rectangle(image_rectangle, rid, iid, bbox)

        return img


    def _update_image_rectangle(self, image_rectangle, rid, iid, bbox):
        image_rectangle.rid = rid
        image_rectangle.iid = iid
        image_rectangle.bbox = bbox

        return image_rectangle

    def _create_image_rectangle(self, rid, iid, image_meta, bbox, image, photo_image):
        return ImageRectangle(rid, iid, image_meta.rectangle, bbox, image_meta, image, photo_image)

    def _load_draw(self, images, canvas, image_meta, x, y):
        return self._create_draw(images, image_meta.get_image(), canvas, image_meta, x, y)

    def _on_mouse_wheel(self, event):
        # todo: should create this function as a utility function
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self._canvas.yview_scroll(-1, "units")

    def _on_right_click(self, event):
        rid = self._f_rid
        if rid:
            menu = tk.Menu(self._frame, tearoff=0)
            menu.add_command(label="Delete", command=self._delete_image)
            menu.tk_popup(event.x_root, event.y_root)

    def _delete_image(self):
        rid = self._f_rid
        items = self._items
        canvas = self._canvas

        canvas.unbind("<Motion>")

        self._f_rid = None
        self._prev = None

        with engine.connect() as connection:
            rct = self._images.pop(rid)

            self._unbind(canvas)

            self._text = None

            p = rct.position
            k = p - 1

            for item in items[p::]:
                item.position = p
                p += 1

            for item in items:
                canvas.delete(item.rid)
                canvas.delete(item.iid)

            items.pop(k)  # remove item from list

            self._draw_samples(self._width, items, False)

            rct.delete(connection)

        with engine.connect() as connection:
            for item in items:
                item.submit(connection)

            pos = len(items) - 1

            self._controller.samples.position = pos if pos > 0 else 0

        canvas.bind("<Motion>", self._on_motion)


class SamplesController(object):
    def __init__(self, model):
        """

        Parameters
        ----------
        model: tools.detection.samples.SamplesModel
        """
        self._model = model

        self._view = SamplesView(self, model)

        self.samples = None

    def view(self):
        return self._view

    # def capture_zone_update(self, connection, capture_zone):
    #     view = self._view
    #     if not capture_zone.classifiable:
    #         view.deactivate() #deactive sampling
    #     else:
    #         view.activate()
    #         view.capture_zone_update(connection, capture_zone)

    def samples_update(self, samples):
        sp = self.samples

        if sp:
            sp.clear_image_observers()

        self.samples = samples

        view = self._view

        samples.add_image_observer(view)

        view.samples_update(samples)

    def filters_update(self, filters):
        """

        Parameters
        ----------
        filters: tools.detection.filtering.filtering.FilteringModel

        Returns
        -------

        """

        view = self._view

        if filters.filters_enabled:
            view.enable_filters(filters)
        else:
            view.disable_filters(filters)

    def add_images_observer(self, observer):
        self._view.add_image_observer(observer)
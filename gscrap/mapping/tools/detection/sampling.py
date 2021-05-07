from collections import defaultdict

from sqlalchemy import text

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
import numpy as np

from gscrap.detection import models as mdl
from gscrap.data import engine
from gscrap.data.images import images

_GET_IMAGE = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name AND label_name=:label_name AND label_type=:label_type
    ORDER BY position ASC
    """
)

class Samples(object):
    def __init__(self, capture_zone, label):
        """

        Parameters
        ----------
        capture_zone
        label: models.rectangle_labels.RectangleLabel
        """
        self._capture_zone = capture_zone
        self._label = label

        self.position = 0

        self._image_observers = []

        self._detection = mdl.NullDetection()

    @property
    def classifiable(self):
        return self._label.classifiable

    @property
    def capture(self):
        return self._label.capture

    @property
    def label_type(self):
        return self._label.label_type

    @property
    def label_name(self):
        return self._label.label_name

    @property
    def width(self):
        return self._capture_zone.width

    @property
    def height(self):
        return self._capture_zone.height

    def get_images(self, connection):
        position = 0
        label = self._label
        cz = self._capture_zone

        for im in connection.execute(
                _GET_IMAGE,
                project_name=cz.project_name,
                label_name=label.label_name,
                label_type=label.label_type):

            position += 1
            yield images.ImageMetadata(
                im["image_id"],
                im["project_name"],
                cz.rectangle,
                im["hash_key"],
                im["position"],
                {'label_name':im.label_name,
                 'label_type':im.label_type,
                 'instance_name':im.label_instance_name})

        self.position = position

    def add_sample(self, image, label):
        position = self.position
        position += 1

        meta = self._capture_zone.add_sample(image, label, position)

        self.position = position

        for obs in self._image_observers:
            obs.new_sample(image, meta)

    def set_detection(self, detection):
        self._detection = detection

    def detect(self, img):
        return self._detection.detect(img)

    def add_image_observer(self, observer):
        self._image_observers.append(observer)

    def clear_image_observers(self):
        self._image_observers.clear()

class ImageSource(object):
    def __init__(self, filtering_model):
        self._filtering_model = filtering_model

        self.height = 0
        self.width = 0

    def set_images(self, images):
        self._images = images

    def get_images(self):
        for im in self._images:
            yield im.label, self._filtering_model.filter_image(np.asarray(im.image))


class SamplingView(object):
    def __init__(self, controller, model):
        """

        Parameters
        ----------
        controller: SamplingController
        model: tools.detection.samples.SamplesModel
        """
        self._controller = controller
        self._model = model

        self._frame = None
        self._label_frame = None
        self._label = None
        self._label_options = None
        self.canvas = None

        self._commands = None
        self.update_button = None
        self.save = None
        self.menu = None

        self.label_instance = None


    def capture_zone_update(self, connection, capture_zone):
        """

        Parameters
        ----------
        capture_zone: tools.detection.capture.CaptureZone

        Returns
        -------

        """
        # ops = self.label_instance_options
        # # menu = ops["menu"]
        # # controller = self._controller
        #
        #
        # ops["values"] = tuple([label for label in capture_zone.get_labels(connection)])
            # menu.add_command(label=label, command=controller.set_label)
        pass

    def render(self, container):
        controller = self._controller

        self._frame = frame = tk.Frame(container)

        self._canvas_frame = cf = tk.Frame(frame)
        self.canvas = cv = tk.Canvas(cf, width=80, height=80, bg="white")

        self._label_frame = lf = tk.Frame(frame)
        self._label_type = lt = tk.Label(lf, text="Type")
        self._label_class = lc = tk.Label(lf, text="Class")
        self._label_instance = li = tk.Label(lf, text="Label")

        self.label_type = label_type = tk.StringVar(lf, "N/A")
        self.label_class = label_class = tk.StringVar(lf, "N/A")
        self.label_instance = label_instance = tk.StringVar(lf, "N/A")

        self.label_instance_options = lio = ttk.Combobox(
            lf, values=("N/A",), textvariable=label_instance, state='readonly')
        self.label_type_options = lto = ttk.Combobox(
            lf, values=("N/A",), textvariable=label_type, state='readonly')
        self.label_class_options = lco = ttk.Combobox(
            lf, values=("N/A",), textvariable = label_class, state='readonly')

        label_class.trace("w", controller.set_label_class)
        label_instance.trace("w", controller.set_label)
        label_type.trace("w", controller.set_label_type)

        self._filtering = flt = tk.Label(lf, text="Filters")
        self._toggles = tlg = tk.Frame(lf)

        self._filtering_on = flt_on = tk.Radiobutton(tlg, text="On", command=controller.enable_filters, value=1)
        self._filtering__off = flt_off = tk.Radiobutton(tlg, text="Off", command=controller.disable_filters, value=2)

        lio["state"] = tk.DISABLED
        lto["state"] = tk.DISABLED
        lco["state"] = tk.DISABLED

        self._commands = cmd = tk.Frame(frame)
        self._image_options = image = tk.Label(lf, text="Image")
        self._menu_button = mb = tk.Menubutton(lf, text="Commands")
        self.menu = menu = tk.Menu(mb, tearoff=0)

        menu.add_command(label="Update", command=controller.update)
        menu.add_command(label="Save", command=controller.save)
        menu.add_command(label="Detect", command=controller.detect)
        # self.update_button = ub = tk.Button(cmd, text="Update", command=controller.update)  # update thumbnail
        # self.save = save = tk.Button(cmd, text="Save", command=controller.save)  # save sample
        # self.detect = detect = tk.Button(cmd, text="Detect", command=controller.detect)

        menu.entryconfig("Save", state=tk.DISABLED)
        menu.entryconfig("Detect", state=tk.DISABLED)
        menu.entryconfig("Update", state=tk.DISABLED)


        frame.grid(row=0, column=0)
        cf.grid(row=1, column=0)

        cv.grid(row=0, column=0)
        lf.grid(row=1, column=1, sticky=tk.NW)
        cmd.grid(row=0, column=0, sticky=tk.NW)

        # mb.grid(row=0, column=0)


        # lf.pack()
        tlg.grid(row=1, column=1)

        #label type
        lt.grid(row=2, column=0)
        lto.grid(row=2, column=1)

        #label class
        lc.grid(row=3, column=0)
        lco.grid(row=3, column=1)

        #label instance
        li.grid(row=4, column=0)
        lio.grid(row=4, column=1)

        flt.grid(row=1, column=0)
        flt_on.grid(row=0, column=0)
        flt_off.grid(row=0, column=1)

        image.grid(row=0, column=0)

        mb.grid(row=0, column=1)
        mb.config(menu=menu)

        return frame

    def filter_update(self, filters):
        # todo: apply filter on image
        pass

    def update_thumbnail(self, img):
        self._thumbnail.paste(img)

    def create_thumbnail(self, image):
        self._thumbnail = tn = ImageTk.PhotoImage(image)
        controller = self._controller

        controller.set_image(image)
        canvas = self.canvas

        return canvas.create_image(
            canvas.winfo_width() / 2,
            canvas.winfo_height() / 2,
            anchor=tk.CENTER,
            image=tn)


    def close(self):
        self._frame.destroy()

class SamplingController(object):
    def __init__(self, model, filtering_model):
        """

        Parameters
        ----------
        controller: SamplingController
        model: tools.detection.samples.SamplesModel
        filtering_model: tools.detection.filtering.filtering.FilteringModel
        """

        self._model = model
        self._filtering_model = filtering_model
        self._sampling_view = SamplingView(self, model)


        self._image = None

        self._label_set = False
        self._thumbnail_set = False

        self._label = None

        self._capture_zone = None
        self._item = None
        self._labels = None

        self._filters_on = False

        self._samples_observers = []

        self._image_source = ImageSource(filtering_model)

        self._samples = None
        self._detection = False

    def view(self):
        return self._sampling_view

    def set_image(self, image):
        self._image = image

    def update(self):
        self._image = image = self._capture_zone.capture()
        self._sampling_view.update_thumbnail(image)

    def close(self):
        self._sampling_view.close()

    def save(self):
        image = self._image

        if image:
            self._samples.add_sample(image, {
                "label_name":self._label_class,
                "label_type":self._label_type,
                "instance_name":self._label
            })

    def set_label_type(self, *args):
        view = self._sampling_view
        self._label_type = label_type = view.label_type.get()
        view.label_class_options['values'] = tuple([label.label_name for label in self._labels[label_type]])

        view.label_class_options["state"] = tk.ACTIVE

    def set_label_class(self, *args):

        view = self._sampling_view
        label_type = self._label_type

        self._label_class = label_class = view.label_class.get()

        with engine.connect() as connection:
            view.label_instance_options['values'] = tuple([
                instance['instance_name'] for instance in
                self._capture_zone.get_label_instances(
                    connection,
                    label_type,
                    label_class)])

        view.label_instance_options["state"] = tk.ACTIVE

        samples = next((l for l in self._labels[label_type] if l.label_name == label_class))

        if samples.classifiable:
            view.menu.entryconfig("Save", state=tk.ACTIVE)
            samples.set_detection(mdl.DifferenceMatching(self._image_source))
        else:
            view.menu.entryconfig("Save", state=tk.DISABLED)
            samples.set_detection(mdl.Tesseract())

        view.menu.entryconfig("Detect", state=tk.ACTIVE)

        self._label = view.label_instance.get()

        for obs in self._samples_observers:
            obs.samples_update(samples)

        self._samples = samples

    def set_label(self, *args):
        view = self._sampling_view
        label = view.label_instance.get()

        if label == "Unknown":
            view.menu.entryconfig("Save", state=tk.DISABLED)

        self._label = label

    def detect(self):
        detected = self._samples.detect(self._filtering_model.filter_image(np.asarray(self._image)))

        self._sampling_view.label_instance.set(detected)

    def enable_filters(self):
        self._filtering_model.enable_filtering()

    def disable_filters(self):
        self._filtering_model.disable_filtering()

    def create_thumbnail(self, view, capture_zone):
        sv = self._sampling_view
        cz = self._capture_zone
        item = self._item

        if item and cz:
            view.canvas.delete(item)

        self._capture_zone = capture_zone
        self._image = image = capture_zone.capture()
        self._item = sv.create_thumbnail(image)

        self._thumbnail_set = True

        sv.menu.entryconfig("Update", state=tk.ACTIVE)

        view.label_type_options["state"] = tk.ACTIVE

        # if self._label:
        #     sv.menu.entryconfig("Save", state=tk.ACTIVE)

    def set_capture_zone(self, capture_zone):
        with engine.connect() as connection:
            sv = self._sampling_view

            sv.menu.entryconfig("Detect", state=tk.DISABLED)

            sv.label_instance_options["state"] = tk.DISABLED
            sv.label_class_options["state"] = tk.DISABLED

            sv.menu.entryconfig("Save", state=tk.DISABLED)

            self._labels = labels = defaultdict(list)

            for label in capture_zone.get_labels(connection):
                labels[label.label_type].append(Samples(capture_zone, label))

            sv.label_type_options["values"] = tuple(labels.keys())

            # sv.capture_zone_update(connection, capture_zone)

            self.create_thumbnail(sv, capture_zone)

    def filters_update(self, filters):
        """

        Parameters
        ----------
        filters: tools.detection.filtering.filtering.FilteringModel

        Returns
        -------

        """
        view = self._sampling_view
        image = self._image

        if image:
            if filters.filters_enabled:
                # if not self._filters_on:
                view.update_thumbnail(Image.fromarray(filters.filter_image(np.asarray(image))))
                self._filters_on = True
            else:
                if self._filters_on:
                    view.update_thumbnail(image)
                    self._filters_on = False

    def images_update(self, images):
        self._image_source.set_images(images)

    def add_samples_observer(self, observer):
        self._samples_observers.append(observer)
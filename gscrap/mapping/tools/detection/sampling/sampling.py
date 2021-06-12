from collections import defaultdict

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
import numpy as np

from gscrap.mapping.tools.detection import image_grid as ig
from gscrap.mapping.tools.detection.sampling import samples as spl

from gscrap.detection import models as mdl

from gscrap.data import engine
from gscrap.data.images import images
from gscrap.mapping.tools import navigation

def crop_image(bbox, image):
    x0, y0, x1, y1 = bbox
    return image[y0:y1, x0:x1, :]

class SamplesStore(object):
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

        for im in images.get_images(
                connection,
                cz.project_name,
                label.label_type,
                label.label_name):

            position += 1
            yield im

        self.position = position

    def add_sample(self, image, label):
        position = self.position
        position += 1

        meta = self._capture_zone.add_sample(
            image,
            label,
            position)

        self.position = position

        for obs in self._image_observers:
            obs.add_image(image, meta)

    def set_detection(self, detection):
        self._detection = detection

    def detect(self, img):
        return self._detection.detect(img)

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
    def __init__(self, controller, image_grid):
        """

        Parameters
        ----------
        controller: SamplingController
        """
        self._controller = controller

        self._sampling_frame = None
        self._label_frame = None
        self._label = None
        self._label_options = None

        self._commands = None
        self.update_button = None
        self.save = None
        self.menu = None

        self.label_instance = None

        self.navigation_view = navigation.NavigationView(80, 80)

        self._image_grid = image_grid

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
        self._sampling_frame = sampling_frame = tk.Frame(frame)

        self._canvas_frame = cf = tk.Frame(sampling_frame)

        nav = self.navigation_view.render(cf)

        self._label_frame = lf = tk.Frame(sampling_frame)
        self._label_type = lt = tk.Label(lf, text="Type")
        self._label_class = lc = tk.Label(lf, text="Class")
        self._label_instance = li = tk.Label(lf, text="Label")

        self.label_type = label_type = tk.StringVar(lf, "N/A")
        self.label_class = label_class = tk.StringVar(lf, "N/A")
        self.label_instance = label_instance = tk.StringVar(lf, "N/A")

        self.label_instance_options = lio = ttk.Combobox(
            lf, values=("N/A",),
            textvariable=label_instance,
            state='readonly')

        self.label_type_options = lto = ttk.Combobox(
            lf, values=("N/A",),
            textvariable=label_type,
            state='readonly')

        self.label_class_options = lco = ttk.Combobox(
            lf, values=("N/A",),
            textvariable=label_class,
            state='readonly')

        label_class.trace("w", controller.set_label_class)
        label_instance.trace("w", controller.set_label)
        label_type.trace("w", controller.set_label_type)

        self._filtering = flt = tk.Label(lf, text="Filters")
        self._toggles = tlg = tk.Frame(lf)

        self._filtering_on = flt_on = tk.Radiobutton(
            tlg, text="On",
            command=controller.enable_filters,
            value=1)

        self._filtering__off = flt_off = tk.Radiobutton(
            tlg, text="Off",
            command=controller.disable_filters,
            value=2)

        lio["state"] = tk.DISABLED
        lto["state"] = tk.DISABLED
        lco["state"] = tk.DISABLED

        self._commands = cmd = tk.Frame(sampling_frame)
        self._image_options = image = tk.Label(lf, text="Image")
        self._menu_button = mb = tk.Menubutton(lf, text="Commands")
        self.menu = menu = tk.Menu(mb, tearoff=0)

        # menu.add_command(label="Update", command=controller.update)
        menu.add_command(label="Save", command=controller.save)
        menu.add_command(label="Detect", command=controller.detect)
        # self.update_button = ub = tk.Button(cmd, text="Update", command=controller.update)  # update thumbnail
        # self.save = save = tk.Button(cmd, text="Save", command=controller.save)  # save sample
        # self.detect = detect = tk.Button(cmd, text="Detect", command=controller.detect)

        menu.entryconfig("Save", state=tk.DISABLED)
        menu.entryconfig("Detect", state=tk.DISABLED)
        # menu.entryconfig("Update", state=tk.DISABLED)

        sampling_frame.grid(row=0, column=0)
        cf.grid(row=1, column=0)

        # cv.grid(row=0, column=0)
        nav.grid(row=0, column=0)

        lf.grid(row=1, column=1, sticky=tk.NW)
        cmd.grid(row=0, column=0, sticky=tk.NW)

        # mb.grid(row=0, column=0)

        # lf.pack()
        tlg.grid(row=1, column=1)

        # label type
        lt.grid(row=2, column=0)
        lto.grid(row=2, column=1)

        # label class
        lc.grid(row=3, column=0)
        lco.grid(row=3, column=1)

        # label instance
        li.grid(row=4, column=0)
        lio.grid(row=4, column=1)

        flt.grid(row=1, column=0)
        flt_on.grid(row=0, column=0)
        flt_off.grid(row=0, column=1)

        image.grid(row=0, column=0)

        mb.grid(row=0, column=1)
        mb.config(menu=menu)

        # samples image grid
        samples = tk.LabelFrame(frame, text="Samples")
        self._image_grid.render(samples)
        samples.grid(row=1, column=0)

        return frame

    def update_thumbnail(self, img):
        self._thumbnail.paste(img)

    def delete_thumbnail(self, tid):
        self.navigation_view.canvas.delete(tid)

    def create_thumbnail(self, image):
        self._thumbnail = tn = ImageTk.PhotoImage(image)
        return self.navigation_view.set_thumbnail(tn)

    def close(self):
        self._sampling_frame.destroy()

class SamplingController(object):
    def __init__(self, filtering_model):
        """

        Parameters
        ----------
        filtering_model: tools.detection.filtering.filtering.FilteringModel
        """

        self._filtering_model = filtering_model

        self._image_grid = image_grid = ig.ImageGrid()

        self._sampling_view = view = SamplingView(self, image_grid)

        self._image = None

        self._label_set = False
        self._thumbnail_set = False

        self._label = None

        self._item = None
        self._labels = None

        self._filters_on = False

        self._samples_observers = []

        self._image_source = ImageSource(filtering_model)

        self._samples = None

        self._navigator = navigator = navigation.NavigationController(self._frame_update)

        navigator.set_view(view.navigation_view)

        # detectors

        self._dm_detector = dmd = mdl.DifferenceMatching(self._image_source)
        self._tesseract = trt = mdl.Tesseract()
        self._null_detector = nd = mdl.NullDetection()
        self._detector = nd

        # # keep these these references so that we can update the threshold
        # dlc = lc.DifferentLabel(dmd)
        # ulc = lc.UnknownLabel(trt)
        #
        # # keep a reference to this so that we can change the threshold
        #
        # self._dlc = dlc
        # self._ulc = ulc

        self._samples_grid = spl.Samples(image_grid)

        image_grid.on_left_click(self._selected_sample)

        self._video_metadata = None
        self._capture_zone = None

    def _selected_sample(self, index, click_event):
        im = self._samples_grid.get_sample(index)
        # todo: image display image in the thumbnail in the sampling view.

    def view(self):
        return self._sampling_view

    def _frame_update(self, image):
        self._sampling_view.update_thumbnail(
            self._apply_filters(
                self._filtering_model, image))

    def close(self):
        self._sampling_view.close()

    def save(self):
        #todo: save sample

        image = self._image

        if image:
            self._samples.add_sample(
                image,
                {
                    "label_name": self._label_class,
                    "label_type": self._label_type,
                    "instance_name": self._label
            })

    def set_label_type(self, *args):
        view = self._sampling_view
        self._label_type = label_type = view.label_type.get()
        view.label_class_options['values'] = tuple([label.label_name for label in self._labels[label_type]])

        view.label_class_options["state"] = tk.ACTIVE

    def set_label_class(self, *args):

        view = self._sampling_view
        label_type = self._label_type
        capture_zone = self._capture_zone

        self._label_class = label_class = view.label_class.get()

        with engine.connect() as connection:
            view.label_instance_options['values'] = tuple([
                instance['instance_name'] for instance in
                capture_zone.get_label_instances(
                    connection,
                    label_type,
                    label_class)])

        view.label_instance_options["state"] = tk.ACTIVE

        # todo: do nothing if this raises a stopiteration error
        labels = next((l for l in self._labels[label_type] if l.label_name == label_class))

        # navigator = self._navigator

        # update navigator and detection

        if labels.classifiable:
            # comparator = self._dlc
            view.menu.entryconfig("Save", state=tk.ACTIVE)
            # todo: need a view to set the threshold of the detector
            # samples.set_detection(self._dm_detector)
            self._detector = self._dm_detector
        else:
            # comparator = self._ulc
            # can't save an unclassifiable element
            view.menu.entryconfig("Save", state=tk.DISABLED)
            # samples.set_detection(self._tesseract)
            self._detector = self._tesseract

        # navigator.set_image_comparator(comparator)
        # navigator.restart()

        view.menu.entryconfig("Detect", state=tk.ACTIVE)

        self._label = view.label_instance.get()

        # for obs in self._samples_observers:
        #     obs.samples_update(samples)

    def set_label(self, *args):
        view = self._sampling_view
        label = view.label_instance.get()

        if label == "Unknown":
            view.menu.entryconfig("Save", state=tk.DISABLED)

        self._label = label

    def detect(self):
        self._sampling_view.label_instance.set(
            self._detector.detect(
                self._filtering_model.filter_image(
                    self._image)))

    def enable_filters(self):
        self._filtering_model.enable_filtering()

    def disable_filters(self):
        self._filtering_model.disable_filtering()

    def create_thumbnail(self, view, capture_zone, frame):
        cz = self._capture_zone
        item = self._item

        if item and cz:
            view.delete_thumbnail(item)

        self._image = image = crop_image(capture_zone.bbox, frame)
        self._item = view.create_thumbnail(Image.fromarray(image))

        self._thumbnail_set = True

        # sv.menu.entryconfig("Update", state=tk.ACTIVE)

        view.label_type_options["state"] = tk.ACTIVE

        # if self._label:
        #     sv.menu.entryconfig("Save", state=tk.ACTIVE)

    def set_capture_zone(self, capture_zone):

        with engine.connect() as connection:
            sv = self._sampling_view
            meta = self._video_metadata

            sv.menu.entryconfig("Detect", state=tk.DISABLED)

            sv.label_instance_options["state"] = tk.DISABLED
            sv.label_class_options["state"] = tk.DISABLED

            sv.menu.entryconfig("Save", state=tk.DISABLED)

            # load labels for the capture zone.

            self._labels = labels = defaultdict(list)

            # todo: load samples and apply filters if they are active

            # set sample store for each label type
            for label in capture_zone.get_labels(connection):
                labels[label.label_type].append(label)

            sv.label_type_options["values"] = tuple(labels.keys())

            # todo: no navigator

            # # sv.capture_zone_update(connection, capture_zone)
            # frame = self._navigator.current_frame
            #
            # if frame:
            #     self.create_thumbnail(sv, capture_zone, frame)

            self._capture_zone = capture_zone

            # todo: when loading samples, we should exclude already labeled samples

            if meta:
                self._samples_grid.load_samples(meta, capture_zone)

    def filters_update(self, filters):
        """

        Parameters
        ----------
        filters: tools.detection.filtering.filtering.FilteringModel

        Returns
        -------

        """
        image = self._image

        if image:
            self._sampling_view.update_thumbnail(
                self._apply_filters(filters, image))

    def _apply_filters(self, filters, image):
        if filters.filters_enabled:
            return Image.fromarray(filters.filter_image(image))
        return Image.fromarray(image)

    def images_update(self, images):
        self._image_source.set_images(images)

    def set_video_metadata(self, video_meta):
        # self._navigator.set_video_metadata(video_meta)
        self._video_metadata = video_meta
        cz = self._capture_zone

        if cz:
            self._samples_grid.load_samples(video_meta, cz)

    def add_samples_observer(self, observer):
        self._samples_observers.append(observer)

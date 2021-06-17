from collections import defaultdict

import tkinter as tk

from PIL import Image
import numpy as np

from gscrap.mapping.tools.detection import image_grid as ig
from gscrap.mapping.tools.detection.sampling import samples as spl

from gscrap.detection import models as mdl
from gscrap.detection import utils as mdl_utils

from gscrap.data import engine
from gscrap.data.images import images

from gscrap.mapping.tools.detection.sampling import view as vw
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

class SamplingController(object):
    def __init__(self, filtering_model, on_label_set=None):
        """

        Parameters
        ----------
        filtering_model: tools.detection.filtering.filtering.FilteringModel
        """

        self._filtering_model = filtering_model

        self._image_grid = image_grid = ig.ImageGrid()

        self._sampling_view = view = vw.SamplingView(self, image_grid)

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

        self._preview = preview = vw.PreviewController()

        preview.set_view(view.preview)

        # detectors

        self._dm_detector = mdl.DifferenceMatching(self._image_source)
        self._tesseract = mdl.Tesseract()
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

        def null_callback(label):
            pass

        self._label_callback = on_label_set if on_label_set else null_callback

        self._threshold = mdl_utils.DEFAULT_THRESH
        self._max_threshold = 0

    def _selected_sample(self, index, click_event):
        self._preview.display(self._samples_grid.get_sample(index))

    def view(self):
        return self._sampling_view

    def _frame_update(self, image):
        self._sampling_view.update_thumbnail(
            self._apply_filters(
                self._filtering_model,
                image))

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

        # todo: do nothing if this raises a stop iteration error
        labels = next((l for l in self._labels[label_type] if l.label_name == label_class))

        #todo: once the label class and label type have been set, do a callback to observers
        # ex: the we load filters associated with the label.

        #todo: should separate sampling from detection.

        if labels.classifiable:
            # comparator = self._dlc
            view.menu.entryconfig("Save", state=tk.ACTIVE)
            #todo: need a view to set the threshold of the detector
            # activate threshold slider. each time we set threshold,
            # the samples get compressed.

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

            dims = (capture_zone.width, capture_zone.height)

            self._capture_zone = capture_zone
            self._max_threshold = mt = mdl_utils.max_threshold(dims)

            #initialize preview
            self._preview.initialize(dims)

            sv.threshold.config(to=mt)

            if meta:
                grid = self._samples_grid
                grid.load_samples(meta, capture_zone)
                # grid.compress_samples(
                #     self._filtering_model,
                #     self._image_equal)
                grid.draw()

                sv.threshold["state"] = tk.NORMAL

    def _image_equal(self, im1, im2):
        return mdl_utils.different_image(
            im1, im2, self._threshold)

    def set_threshold(self, value):
        #update threshold and re-compress elements
        self._threshold = value

        grid = self._samples_grid

        grid.compress_samples(
            self._filtering_model,
            self._image_equal)

        grid.draw()

    def get_max_threshold(self):
        return self._max_threshold

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
            grid = self._samples_grid
            grid.load_samples(video_meta, cz)
            grid.compress_samples(
                self._filtering_model,
                self._image_equal)

            grid.draw()

            self._sampling_view.threshold["state"] = tk.NORMAL

    def add_samples_observer(self, observer):
        self._samples_observers.append(observer)

    def clear(self):
        self._samples_grid.clear()

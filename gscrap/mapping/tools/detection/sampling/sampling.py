from uuid import uuid4

from collections import defaultdict

import numpy as np

import tkinter as tk

from PIL import Image

from gscrap.samples import source as sc
from gscrap.samples import store as st

from gscrap.labeling import labeling as mdl
from gscrap.labeling import utils as mdl_utils
from gscrap.labeling import labeler as lbl

from gscrap.data import engine
from gscrap.data.filters import filters

from gscrap.mapping.tools.detection import grid as gd

from gscrap.mapping.tools.detection.sampling import view as vw
from gscrap.mapping.tools.detection.sampling import image_grid as ig
from gscrap.mapping.tools.detection.sampling import samples as spl

class SamplingController(object):
    def __init__(self, filtering_model, width, height, on_label_set=None):
        """

        Parameters
        ----------
        filtering_model: gscrap.mapping.tools.detection.filtering.filtering.FilteringModel
        """

        self._filtering_model = filtering_model
        self._filter_group = None
        self._parameter_id = None

        self._image = None

        self._label_set = False
        self._thumbnail_set = False

        self._label = None
        self._label_class = None
        self._label_type = None

        self._item = None
        self._labels = None

        self._filters_on = False

        self._samples_observers = []

        self._samples_store = None
        self._save_sample = False

        self._preview = preview = vw.PreviewController()

        self._image_buffer = buffer = spl.ArrayImageBuffer()

        self._image_grid = image_grid = gd.Grid(
            ig.ImageRectangleFactory(buffer),
            width,
            height)

        self._samples_grid = samples_grid = spl.Samples(buffer, image_grid)

        samples_grid.selected_sample(self._selected_sample)

        self._sampling_view = view = vw.SamplingView(self, image_grid)

        preview.set_view(view.preview)

        self._selected_image_index = None

        # labeling

        self._labeler = labeler = lbl.Labeler()

        self._difference_matching = mdl.DifferenceMatching()
        self._tesseract = mdl.Tesseract()

        self._labeling = labeler.labeling

        self._video_metadata = None
        self._capture_zone = None

        def null_callback(label):
            pass

        self._label_callback = on_label_set if on_label_set else null_callback

        self._threshold = mdl_utils.DEFAULT_THRESH
        self._max_threshold = 0
        self._model_name = ''

    def _selected_sample(self, index):
        p_idx = self._selected_image_index
        view = self._sampling_view

        if p_idx != index:
            view.label_class_options["state"] = tk.DISABLED
            view.label_instance_options["state"] = tk.DISABLED
            view.label_instance.set("N/A")
            view.save_button["state"] = tk.DISABLED

        self._selected_image_index = index
        self._preview.display(self._samples_grid.get_sample(index))

        view.label_type_options["state"] = tk.ACTIVE

    def view(self):
        return self._sampling_view

    def close(self):
        self._sampling_view.close()

    def save(self):
        with engine.connect() as connection:
            image_idx = self._selected_image_index
            label = self._label

            if image_idx != None and label != 'N/A' and self._save_sample:
                st.add_sample(
                    self._samples_data,
                    self._image_buffer.get_image(image_idx),
                    {
                        "label_name": self._label_class,
                        "label_type": self._label_type,
                        "instance_name": label
                    },
                    connection
                )

            self._save_filters_mappings(connection, self._filtering_model)

    def _save_filters_mappings(self, connection, filter_model):
        label_class = self._label_class
        label_type = self._label_type
        capture_zone = self._capture_zone

        pgr = self._filter_group
        ppr = self._parameter_id

        group_id = filter_model.group_id

        # map labels to models and filters.

        parameter_id = filter_model.parameter_id
        project_name = capture_zone.project_name
        #if the filter_labels already belonged to a group, update the group and parameter

        if parameter_id and group_id and pgr and ppr:
            if group_id != pgr:
                #if group has changed, remove the label from previous group

                #note: label per project is always mapped to ONE group_id and parameter_id pair.

                filters.update_filter_labels_group(
                    connection,
                    label_type,
                    label_type,
                    project_name,
                    group_id)

            if parameter_id != ppr:
                filters.update_filter_labels_parameter_id(
                    connection,
                    label_type,
                    label_type,
                    project_name,
                    group_id)

        elif parameter_id and group_id:
            #if did not belong to any group, add it to database
            filters.store_filter_labels(
                connection,
                group_id,
                label_type,
                label_class,
                parameter_id,
                project_name
            )

        model_name = self._model_name

        if model_name:
            self._labeling.store(connection, model_name)

    def set_label_type(self, *args):
        view = self._sampling_view
        self._label_type = label_type = view.label_type.get()

        view.label_class_options['values'] = tuple(
            [label.label_name for label in self._labels[label_type]])

        view.label_class_options["state"] = tk.NORMAL

    def set_label_class(self, *args):

        view = self._sampling_view
        label_type = self._label_type
        capture_zone = self._capture_zone

        self._label_class = label_class = view.label_class.get()

        # todo: do nothing if this raises a stop iteration error
        labels = next((l for l in self._labels[label_type] if l.label_name == label_class))

        #todo: once the label class and label type have been set, do a callback to observers
        # ex: the we load filters associated with the label.

        fm = self._filtering_model

        #todo: should separate sampling from detection.

        labeling = None

        #try loading labeling model
        with engine.connect() as connection:
            meta = mdl.load_labeling_model_metadata(
                connection,
                labels,
                capture_zone.project_name)

            if meta:
                labeling = mdl.get_labeling_model(meta['model_type']).load(
                    connection,
                    meta['model_name'])

            filter_group = filters.get_filter_group(
                connection,
                label_class,
                label_type,
                capture_zone.project_name)

            if filter_group:
                self._filter_group = filter_group['group_id']
                #this will be displayed on the filters canvas.
                fm.import_filters(
                    connection,
                    filter_group)

            self._parameter_id = fm.parameter_id

            if labels.classifiable:
                sample_source = sc.SampleSource(
                    capture_zone.project_name,
                    label_type,
                    label_class,
                    capture_zone.dimensions
                )

                #load samples into the sample source
                sc.load_samples(sample_source, connection)

                # comparator = self._dlc
                self._labeling = lb = self._difference_matching if not labeling else labeling

                threshold = lb.threshold

                view.threshold['state'] = tk.NORMAL
                view.threshold.config(to=self._max_threshold)
                view.threshold.set(threshold)

                self._threshold = threshold

                lb.set_samples_source(sample_source)

                self._save_sample = True

            else:
                # can't save an unclassifiable element
                view.threshold['state'] = tk.DISABLED
                self._labeling = lb = self._tesseract if not labeling else labeling

                self._save_sample = False

            labeler = self._labeler

            #set labeling model
            labeler.labeling = lb

            #store mappings if its a new model...
            if not labeling:
                #map model to label and store
                self._model_name = model_name = uuid4().hex

                lb.store(connection, model_name)

                mdl.store_label_model(
                    connection,
                    model_name,
                    label_type,
                    label_class,
                    capture_zone.project_name
                )

            view.detect_button["state"] = tk.NORMAL

            label = self._detect(labeler, capture_zone.dimensions)

            if label == "N/A":
                view.label_instance_options['values'] = tuple([
                    instance['instance_name'] for instance in
                    capture_zone.get_label_instances(
                        connection,
                        label_type,
                        label_class)])

                view.label_instance_options["state"] = tk.ACTIVE
                self._label = view.label_instance.get()

                view.save_button["state"] = tk.NORMAL

            else:
                view.label_instance.set(label)
                view.save_button["state"] = tk.DISABLED

    def set_label(self, *args):
        view = self._sampling_view
        label = view.label_instance.get()

        if label == "Unknown":
            view.detect_button["state"] = tk.DISABLED

        self._label = label

    def detect(self):
        self._sampling_view.label_instance.set(
            self._detect(
                self._labeler,
                self._capture_zone.dimensions))

    def _detect(self, labeler, dimensions):
        return lbl.label(labeler, np.frombuffer(
                    self._samples_grid.get_sample(
                        self._selected_image_index),
                    np.uint8).reshape(dimensions[1], dimensions[0], 3))

    def enable_filters(self):
        self._filtering_model.enable_filtering()
        self._filters_on = True

    def disable_filters(self):
        self._filtering_model.disable_filtering()
        self._filters_on = False

    def set_capture_zone(self, capture_zone):

        with engine.connect() as connection:
            sv = self._sampling_view
            meta = self._video_metadata

            sv.detect_button["state"] = tk.DISABLED

            sv.label_instance_options["state"] = tk.DISABLED
            sv.label_class_options["state"] = tk.DISABLED

            sv.save_button["state"] = tk.DISABLED

            # load labels for the capture zone.
            self._labels = labels = defaultdict(list)

            # set sample store for each label type
            for label in capture_zone.get_labels(connection):
                labels[label.label_type].append(label)

            sv.label_type_options["values"] = tuple(labels.keys())

            dims = (capture_zone.width, capture_zone.height)

            self._capture_zone = capture_zone
            self._max_threshold = mt = mdl_utils.max_threshold(dims)

            self._samples_data = st.SampleData(
                capture_zone.project_name,
                capture_zone.width,
                capture_zone.height
            )

            #initialize preview
            self._preview.initialize(dims)

            sv.threshold.config(to=mt)

            if meta:
                grid = self._samples_grid
                grid.clear()

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
        self._threshold = float(value)

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

        if not self._filters_on:
            idx = self._selected_image_index
            preview = self._preview

            grid = self._samples_grid

            buffer = self._image_buffer

            if filters.filters_enabled:
                grid.apply_filters(filters)

                if idx:
                    preview.display(self._apply_filters(
                        filters,
                        self._from_buffer(buffer.get_image(idx))))

            else:
                grid.disable_filters()

                if idx:
                    preview.display(self._from_buffer(buffer.get_image(idx)))

    def _apply_filters(self, filters, image):
        if filters.filters_enabled:
            return Image.fromarray(filters.apply(image))
        return Image.fromarray(image)

    def _from_buffer(self, image):
        Image.frombuffer(
            "RGB",
            self._capture_zone.dimensions,
            image)

    def set_video_metadata(self, video_meta):
        # self._navigator.set_video_metadata(video_meta)
        self._video_metadata = video_meta
        # cz = self._capture_zone
        #
        # if cz:
        #     print("CZ")
        #
        #     grid = self._samples_grid
        #     grid.clear()
        #
        #     grid.load_samples(video_meta, cz)
        #     grid.compress_samples(
        #         self._filtering_model,
        #         self._image_equal)
        #
        #     grid.draw()
        #
        #     self._sampling_view.threshold["state"] = tk.NORMAL

    def disable_video_read(self):
        self._video_metadata = None

    def add_samples_observer(self, observer):
        self._samples_observers.append(observer)

    def clear(self):
        self._samples_grid.clear()

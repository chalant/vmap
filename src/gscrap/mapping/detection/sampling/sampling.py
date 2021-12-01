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

from gscrap.data import io
from gscrap.data.filters import filters
from gscrap.data.images import images as im

from gscrap.mapping.detection import grid as gd

from gscrap.mapping.detection.filtering import filtering

from gscrap.mapping.detection.sampling import view as vw
from gscrap.mapping.detection.sampling import image_grid as ig
from gscrap.mapping.detection.sampling import samples as spl
from gscrap.mapping.detection.sampling import samples_grid as spg


class SamplingController(object):
    def __init__(self, container, width, height, on_label_set=None):
        """

        Parameters
        ----------
        filtering_model: gscrap.mapping.tools.detection.filtering.filtering.FilteringModel
        """

        self.scene = None

        self._filtering_window_active = False
        self._filtering_model = filtering_model = filtering.FilteringModel()
        self._filtering = filtering.FilteringController(filtering_model)
        self._filtering_view = filtering_view = filtering.FilteringView(self, filtering_model, 300, 400)

        filtering_model.add_filters_import_observer(filtering_view)
        filtering_model.add_filter_observer(self)

        self._filter_group = None
        self._parameter_id = None

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
        self._image_metadata = None

        self._preview = preview = vw.PreviewController()

        self._image_buffer = buffer = spl.ArrayImageBuffer()

        self._image_grid = image_grid = gd.Grid(
            ig.ImageRectangleFactory(buffer),
            width,
            height)

        self._samples_view = samples_view = spl.Samples(buffer, image_grid)

        self._samples_grid = spg.SamplesGrid(buffer, 600, 400)

        self._sample_source = None

        self._bin_window_active = False
        self._draw_info = None

        samples_view.on_left_click(self._selected_sample)
        samples_view.on_right_click(self._on_right_click)

        self._sampling_view = view = vw.SamplingView(self, image_grid)

        preview.set_view(view.preview)

        self._selected_image_index = None

        # labeling

        self._labeler = labeler = lbl.Labeler()

        self._labeling = labeler.labeling

        self._video_metadata = None
        self._capture_zone = None

        def null_callback(label):
            pass

        self._label_callback = on_label_set if on_label_set else null_callback

        self._threshold = mdl_utils.DEFAULT_THRESH
        self._max_threshold = 0
        self._model_name = ''

        self._container = container

    def _get_reverse_image_index(self, image_buffer, sample_index):
        for i, j in enumerate(image_buffer.indices):
            if j == sample_index:
                yield i, j

    def unmap_label_from_filters(self):
        with self.scene.connect() as connection:
            filters.remove_label_from_group(
                connection,
                self._label_class,
                self._label_type,
                self.scene.name)

    def display_filters(self):
        def on_closing():
            self._filters_window_active = False
            self._filtering_view.rendered = False

            top.destroy()
            view.filters_button["state"] = tk.NORMAL

        top = tk.Toplevel(self._container)

        top.protocol("WM_DELETE_WINDOW", on_closing)
        top.attributes('-topmost', True)

        view = self._sampling_view

        view.filters_button["state"] = tk.DISABLED

        self._filtering_view.render(top)

    def display_sample_bin(self):
        def on_closing():
            self._bin_window_active = False
            top.destroy()
            view.bin_button["state"] = tk.NORMAL

        view = self._sampling_view

        view.bin_button["state"] = tk.DISABLED

        top = tk.Toplevel(self._container)

        top.protocol("WM_DELETE_WINDOW", on_closing)
        top.attributes('-topmost', True)

        sample_index = self._sample_index
        samples_grid = self._samples_grid

        samples_grid.render(top)

        self._draw_info = info = spg.DrawInfo()

        indices = []

        capture_zone = self._capture_zone

        for i, j in self._get_reverse_image_index(self._image_buffer, sample_index):
            indices.append(i)
            item = ig.Item(capture_zone.dimensions)
            info.items.append(item)
            item.image_index = i

        samples_grid.draw(info, indices)

        self._bin_window_active = True

    def _on_right_click(self, event):
        pass

    def _selected_sample(self, event):
        p_idx = self._selected_image_index
        view = self._sampling_view

        if self._filtering_window_active:
            view.filters_button["state"] = tk.DISABLED
            self._filtering_model.clear_filters()
            self._filtering_view.add_button["state"] = tk.DISABLED

        if not self._bin_window_active:
            view.bin_button["state"] = tk.NORMAL

        else:
            samples_grid = self._samples_grid
            self._draw_info = info = spg.DrawInfo()

            indices = []

            capture_zone = self._capture_zone

            for i, j in self._get_reverse_image_index(self._image_buffer, event.sample_index):
                indices.append(i)
                item = ig.Item(capture_zone.dimensions)
                info.items.append(item)
                item.image_index = i

            samples_grid.draw(info, indices)

        self._clicked = event.clicked
        self._sample_index = index = event.sample_index

        if p_idx != index:
            view.label_class_options["state"] = tk.DISABLED
            view.label_instance_options["state"] = tk.DISABLED
            view.label_instance.set("N/A")
            view.save_button["state"] = tk.DISABLED
            view.clear_button["state"] = tk.DISABLED

        self._selected_image_index = index
        self._preview.display(self._samples_view.get_sample(index))

        view.label_type_options["state"] = tk.ACTIVE

    def set_scene(self, scene):
        self._filtering.set_scene(scene)
        self.scene = scene

    def view(self):
        return self._sampling_view

    def close(self):
        self._sampling_view.close()

    def clear_sample(self):
        with self.scene.connect() as connection:
            image_metadata = self._image_metadata

            view = self._sampling_view

            view.label_class_options["state"] = tk.DISABLED
            view.label_instance_options["state"] = tk.DISABLED
            view.label_instance.set("")
            view.save_button["state"] = tk.DISABLED
            view.clear_button["state"] = tk.DISABLED

            # self._filtering_model.clear_filters()

            if self._filtering_window_active:
                self._filtering_view.add_button["state"] = tk.DISABLED

            sc.delete_sample(self._sample_source, image_metadata.label['instance_name'])
            image_metadata.delete_image(connection)

    def save(self):
        with self.scene.connect() as connection:
            view = self._sampling_view
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
                    connection)

            self._filtering.save()

            self._save_filters_mappings(connection, self._filtering_model)

            model_name = self._model_name

            if model_name:
                self._labeling.update(connection, model_name)

            view.save_button["state"] = tk.DISABLED
            view.clear_button["state"] = tk.NORMAL
            view.label_instance_options["state"] = tk.DISABLED

            if self._sample_source:
                sc.load_samples(self._sample_source, connection, self.scene)

    def _save_filters_mappings(self, connection, filter_model):
        label_class = self._label_class
        label_type = self._label_type
        capture_zone = self._capture_zone

        pgr = self._filter_group
        ppr = self._parameter_id

        group_id = filter_model.group_id

        # map labels to models and filters.

        parameter_id = filter_model.parameter_id
        scene_name = capture_zone.scene_name
        # if the filter_labels already belonged to a group, update the group and parameter

        if pgr and ppr:
            if group_id != pgr:
                # if group has changed, remove the label from previous group

                #todo: remove
                # or parameter_id != ppr

                filters.remove_label_from_group(connection, label_class, label_type, scene_name)

                # note: label per project is always mapped to ONE group_id and parameter_id pair.
                filters.update_filter_labels_group(
                    connection,
                    label_class,
                    label_type,
                    scene_name,
                    group_id,
                )

            if parameter_id != ppr:
                # filters.remove_label_from_parameters(
                #     connection,
                #     label_class,
                #     label_type,
                #     scene_name
                # )

                #todo: remove parameter_id
                filters.update_filter_labels_parameter_id(
                    connection,
                    label_class,
                    label_type,
                    scene_name,
                    parameter_id)

        elif parameter_id and group_id:
            # if did not belong to any group, add it to database
            filters.store_filter_labels(
                connection,
                group_id,
                label_type,
                label_class,
                parameter_id,
                scene_name
            )

    def set_label_type(self, *args):
        view = self._sampling_view
        self._label_type = label_type = view.label_type.get()

        view.label_class_options['values'] = tuple(
            [label.label_name for label in self._labels[label_type]])

        view.label_class_options["state"] = tk.NORMAL
        view.save_button["state"] = tk.NORMAL

    def set_label_class(self, *args):
        view = self._sampling_view
        label_type = self._label_type
        capture_zone = self._capture_zone

        scene = self.scene

        label_class = view.label_class.get()

        labeler = self._labeler

        # todo: do nothing if this raises a stop iteration error
        label_group = next((l for l in self._labels[label_type] if l.label_name == label_class))

        with scene.connect() as connection:

            # filters.remove_label_from_group(connection, label_class, label_type, scene.name)

            if label_class != self._label_class or self._label_class == None:

                self._label_class = label_class

                # todo: once the label class and label type have been set, do a callback to observers
                # ex: the we load filters associated with the label.

                fm = self._filtering_model

                labeling = None

                # try loading labeling model
                meta = mdl.load_labeling_model_metadata(
                    connection,
                    label_group,
                    capture_zone.scene_name)

                if meta:
                    model_name = meta['model_name']
                    labeling = mdl.get_labeling_model(meta['model_type'], label_type).load(
                        connection,
                        model_name)

                    self._model_name = meta['model_name']

                filter_group = filters.get_filter_group(
                    connection,
                    label_class,
                    label_type,
                    capture_zone.scene_name)

                self._filter_group = None
                self._parameter_id = None

                if filter_group:
                    self._filter_group = filter_group['group_id']
                    # this will be displayed on the filters canvas.
                    fm.import_filters(
                        connection,
                        filter_group)


                if not self._filtering_window_active:
                    view.filters_button["state"] = tk.NORMAL
                else:
                    self._filtering_view.add_button["state"] = tk.NORMAL

                self._parameter_id = fm.parameter_id

                if label_group.classifiable:
                    if self._sample_source:
                        self._sample_source.samples.clear()

                    self._sample_source = sample_source = sc.DynamicSampleSource(
                        capture_zone.scene_name,
                        label_type,
                        label_class,
                        capture_zone.dimensions,
                        fm.filter_pipeline
                    )

                    # load samples into the sample source
                    sc.load_samples(sample_source, connection, scene)

                    # comparator = self._dlc
                    self._labeling = lb = mdl.get_labeling_model(
                        'difference_matching',
                        label_group.label_type) if not labeling else labeling

                    threshold = lb.threshold

                    view.threshold['state'] = tk.NORMAL
                    view.threshold.config(to=self._max_threshold)
                    view.threshold.set(threshold)

                    self.set_threshold(threshold)

                    lb.set_samples_source(sample_source)

                    self._save_sample = True

                else:
                    # can't save an unclassifiable element
                    # view.threshold['state'] = tk.DISABLED
                    self._labeling = lb = mdl.get_labeling_model(
                        'tesseract',
                        label_group.label_type) if not labeling else labeling

                    self._save_sample = False

                # set labeling model
                labeler.labeling = lb

                # store mappings if its a new model...
                if not labeling:
                    # map model to label and store
                    self._model_name = model_name = uuid4().hex

                    mdl.add_model(
                        connection,
                        model_name,
                        lb.model_type)

                    lb.store(
                        connection,
                        model_name)

                    mdl.store_label_model(
                        connection,
                        model_name,
                        label_type,
                        label_class,
                        capture_zone.scene_name
                    )

                labeler.set_filter_pipeline(fm.filter_pipeline)

            label = self._detect(labeler, capture_zone.dimensions)

            view.label_instance_options["state"] = tk.ACTIVE
            view.save_button["state"] = tk.NORMAL

            if not label:
                view.label_instance_options['values'] = tuple([
                    instance['instance_name'] for instance in
                    capture_zone.get_label_instances(
                        connection,
                        label_type,
                        label_class)])

                self._label = view.label_instance.get()

            else:
                view.label_instance.set(label)
                view.clear_button["state"] = tk.NORMAL

                if label_group.classifiable:
                    self._image_metadata = im.get_image(
                        connection,
                        scene,
                        {'label_type': label_type,
                         'label_class': label_class,
                         'instance_name': label})

                    view.save_button["state"] = tk.DISABLED

                view.label_instance_options["state"] = tk.DISABLED

    def set_label(self, *args):
        view = self._sampling_view
        label = view.label_instance.get()

        # if label == "Unknown":
        #     view.detect_button["state"] = tk.DISABLED

        self._label = label

    def _detect(self, labeler, dimensions):
        return lbl.label(labeler, np.frombuffer(
            self._samples_view.get_sample(
                self._selected_image_index),
            np.uint8).reshape(dimensions[1], dimensions[0], 3))

    def enable_filters(self):
        self._filtering_model.enable_filtering()
        self._filters_on = True

    def disable_filters(self):
        self._filtering_model.disable_filtering()
        self._filters_on = False

    def set_capture_zone(self, capture_zone):
        '''

        Parameters
        ----------
        capture_zone: gscrap.mapping.tools.detection.capture.CaptureZone

        Returns
        -------

        '''

        with self.scene.connect() as connection:
            sv = self._sampling_view
            meta = self._video_metadata

            # self._filtering_model.clear_filters()

            # sv.detect_button["state"] = tk.DISABLED

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

            self._max_threshold = mt = 2000

            self._samples_data = st.SampleData(
                capture_zone.scene,
                capture_zone.width,
                capture_zone.height,
                capture_zone.rectangle_id
            )

            # initialize preview
            self._preview.initialize(dims)

            sv.threshold.config(to=mt)

            pcz = self._capture_zone

            if pcz and meta:
                if capture_zone.rectangle_id != pcz.rectangle_id:
                    io.submit(self._load_samples, sv, meta, capture_zone)
                    self._threshold = 0
                    sv.threshold.set(0)

                    # todo: problem: setting these creates events!!!

                    # sv.label_type_options.set("N/A")
                    # sv.label_instance_options.set("N/A")
                    # sv.label_class_options.set("N/A")
                    sv.label_type_options["state"] = tk.DISABLED
                    sv.label_class_options["state"] = tk.DISABLED
                    sv.label_instance_options["state"] = tk.DISABLED

            elif meta:
                io.submit(self._load_samples, sv, meta, capture_zone)

            self._capture_zone = capture_zone

    def _load_samples(self, view, meta, capture_zone):
        grid = self._samples_view
        grid.clear()

        grid.load_samples(meta, capture_zone, True)

        grid.compress_samples(
            self._filtering_model,
            self._image_equal)
        grid.draw()

        view.threshold["state"] = tk.NORMAL

    def _image_equal(self, im1, im2):
        return mdl_utils.different_image(
            im1, im2, self._threshold)

    def set_threshold(self, value):
        # update threshold and re-compress elements
        self._threshold = v = float(value)

        grid = self._samples_view

        grid.compress_samples(
            self._filtering_model,
            self._image_equal)

        grid.draw()

        if self._filters_on:
            grid.apply_filters(self._filtering_model)

        model = self._model_name

        if model and self._save_sample:
            self._labeling.threshold = v

        if self._bin_window_active:
            sample_index = self._sample_index
            samples_grid = self._samples_grid

            self._draw_info = info = spg.DrawInfo()

            indices = []

            capture_zone = self._capture_zone

            for i, j in self._get_reverse_image_index(self._image_buffer, sample_index):
                indices.append(i)
                item = ig.Item(capture_zone.dimensions)
                info.items.append(item)
                item.image_index = i

            samples_grid.draw(info, indices)

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

        # idx = self._selected_image_index
        # preview = self._preview

        grid = self._samples_view

        # buffer = self._image_buffer

        grid.compress_samples(
            filters,
            self._image_equal)
        grid.draw()

        if filters.filters_enabled:
            grid.apply_filters(filters)
        else:
            grid.disable_filters()

        self._labeler.set_filter_pipeline(filters.filter_pipeline)

        if self._sample_source:
            self._sample_source.filter_pipeline = filters.filter_pipeline

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

        cz = self._capture_zone
        if cz:
            io.submit(
                self._load_samples,
                self._sampling_view,
                video_meta, cz)

    def disable_video_read(self):
        self._video_metadata = None

    def add_samples_observer(self, observer):
        self._samples_observers.append(observer)

    def load_data(self):
        meta = self._video_metadata
        cz = self._capture_zone

        if meta and cz:
            io.submit(
                self._load_samples,
                self._sampling_view,
                meta, cz)

    def clear_data(self):
        self._samples_view.clear()

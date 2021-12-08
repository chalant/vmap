import base64

from collections import defaultdict

from gscrap.sampling import samples

from gscrap.windows import windows, factory

from gscrap.mapping.tools import tools
from gscrap.mapping.tools import interaction


from gscrap.mapping.capture import capture_zone_display as czp

class CaptureSelectionTool(tools.Tool):
    def __init__(self, main_view, selection_mode):
        """

        Parameters
        ----------
        capture_tool:
        main_view: gscrap.mapping.view.MainView
        """

        self._canvas = canvas = main_view.canvas

        self._interaction = interaction.Interaction(canvas, 0, 0)

        self._display = czp.CaptureZoneDisplay(canvas)
        self._capture_zones = None
        self._loaded = set()

        self._window_manager = wm = windows.DefaultWindowModel(400, 600)
        self._windows_controller = wc = windows.WindowController(
            wm,
            factory.WindowFactory())

        # self._filtering_model = fm = filtering.FilteringModel()

        # self._samples_model = spm = samples.SamplesModel()
        # self._samples = spl = samples.SamplesController(spm)

        self._selection_tool = sc = selection_mode

        # self._filtering = flt = filtering.FilteringController(fm)

        # fm.add_filter_observer(spl)
        # fm.add_filter_observer(sc)
        # fm.add_filters_import_observer(flt.view())

        # spm.add_capture_zone_observer(flt)
        # spm.add_capture_zone_observer(spl)
        # spm.add_capture_zone_observer(sc)

        # spm.add_sample_observer(spl)

        # sc.add_samples_observer(flt)
        # sc.add_samples_observer(spl)

        # spl.add_images_observer(sc)

        # wc.add_window(spl)
        # wc.add_window(flt)
        wc.add_window(sc)

        self._instances_by_rectangle_id = defaultdict(list)

        self._prev = None
        self._rid = None

        self._drawn_instance = None

        self._x = 1
        self._y = 1
        self._i = 0

    def get_view(self, container):
        return self._windows_controller.start(container)

    def start_tool(self, scene):
        """

        Parameters
        ----------
        scene: gscrap.projects.scenes._Scene

        Returns
        -------
        None
        """

        itc = self._interaction

        sampling = self._selection_tool

        sampling.set_scene(scene)

        itc.width = scene.width
        itc.height = scene.height

        self._capture_zones = capture_zones = self._display.draw(scene)

        self._load_samples(self._video_metadata)

        #if rectangle instance positions have change or rectangle instance have been delete
        # we clear previous samples


        #reload all the cleared data
        # sampling.load_data()

        itc.on_left_click(self._on_left_click)

        itc.start(capture_zones)

    def _load_samples(self, video_metadata):
        print('Loading Samples...')
        capture_zones = self._capture_zones

        pri = self._loaded

        if self._video_metadata:
            if capture_zones:
                if video_metadata.video_id == self._video_metadata.video_id:
                    if pri:
                        print("Updating Samples")
                        self._update_load(pri, video_metadata, capture_zones)
                        print("Done")

                    else:
                        print("Creating Samples")
                        self._overwrite_load(video_metadata, capture_zones)
                        print("Done")
                else:
                    print("Overwriting Samples")
                    self._overwrite_load(video_metadata, capture_zones)
                    print("Done")
        else:
            print("Creating Samples")
            self._overwrite_load(video_metadata, capture_zones)
            print("Done")

    def _overwrite_load(self, video_metadata, capture_zones):
        self._loaded = to_load = {
            self._ints_to_bytes(cz.bbox) + self._encode_from_string(cz.rectangle_instance.id)
            for cz in capture_zones.values()}

        for id_ in to_load:
            name = self._decode_to_string(id_[8::])

            try:
                samples.clear_samples(name)
            except FileNotFoundError:
                pass

            bbox = self._ints_from_bytes(id_[0:8])

            samples.store_samples(
                name,
                samples.load_all_samples(video_metadata, bbox)
            )

    def _update_load(self, previous_ids, video_metadata, capture_zones):
        nri = {
            self._ints_to_bytes(cz.bbox) + self._encode_from_string(cz.rectangle_instance.id)
            for cz in capture_zones.values()}

        to_remove = previous_ids.difference(nri)  # remove elements of this set
        to_load = nri.difference(previous_ids)

        for id_ in to_remove:
            name = self._decode_to_string(id_[8::])

            samples.clear_samples(name)

        for id_ in to_load:
            # first 8 bytes is the bbox

            name = self._decode_to_string(id_[8::])

            bbox = self._ints_from_bytes(id_[0:8])

            samples.store_samples(
                name,
                samples.load_all_samples(video_metadata, bbox, from_=0))

        self._loaded = nri


    def _encode_from_string(self, str_):
        return base64.b16encode(str.encode(str_))

    def _decode_to_string(self, bytes_):
        return base64.b16decode(bytes_).decode()

    def _ints_to_bytes(self, ints):
        sequence = b''

        for i in ints:
            sequence += int.to_bytes(i, 2, 'little')

        return sequence

    def _ints_from_bytes(self, sequence):
        j = 0

        result = []

        for _ in range(4):
            result.append(int.from_bytes(sequence[j:j + 2], 'little'))
            j += 2

        return result

    def clear_tool(self):
        self._drawn_instance = None

        #clear sampling tool
        self._selection_tool.clear_data()

        self._interaction.unbind()

        self._display.clear()

    def _on_left_click(self, rct):
        """

        Parameters
        ----------
        rct: gscrap.data.rectangles.rectangles.RectangleInstance

        Returns
        -------

        """
        rid = rct.id

        sampling = self._selection_tool

        drawn_instance = self._drawn_instance
        capture_zones = self._capture_zones

        if not drawn_instance or rid != drawn_instance:
            self._drawn_instance = rid
            sampling.set_capture_zone(capture_zones[rid])

    def enable_read(self, video_meta):
        self._video_metadata = video_meta

        self._selection_tool.set_video_metadata(video_meta)

    def disable_read(self):
        self._selection_tool.disable_video_read()

    def stop(self):
        pass
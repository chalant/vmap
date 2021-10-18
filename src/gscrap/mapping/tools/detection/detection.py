from collections import defaultdict

from gscrap.data.rectangles import rectangle_labels as rl

from gscrap.windows import windows, factory

from gscrap.mapping.tools import tools
from gscrap.mapping.tools import display
from gscrap.mapping.tools import interaction

from gscrap.mapping.tools.detection.sampling import sampling as spg
from gscrap.mapping.tools.detection.sampling import samples as spl
from gscrap.mapping.tools.detection.filtering import filtering
from gscrap.mapping.tools.detection import capture

class DetectionTool(tools.Tool):
    def __init__(self, main_view):
        """

        Parameters
        ----------
        capture_tool:
        main_view: gscrap.mapping.view.MainView
        """

        self._canvas = canvas = main_view.canvas

        self._display = None

        self._interaction = interaction.Interaction(canvas, 0, 0)

        self._capture_zones = {}

        self._window_manager = wm = windows.DefaultWindowModel(400, 600)
        self._windows_controller = wc = windows.WindowController(
            wm,
            factory.WindowFactory())

        #todo: refactor filtering. the filter

        self._filtering_model = fm = filtering.FilteringModel()

        # self._samples_model = spm = samples.SamplesModel()
        # self._samples = spl = samples.SamplesController(spm)

        self._sampling = sc = spg.SamplingController(fm, 360, 400)

        self._filtering = flt = filtering.FilteringController(fm)

        # fm.add_filter_observer(spl)
        fm.add_filter_observer(sc)
        fm.add_filters_import_observer(flt.view())

        # spm.add_capture_zone_observer(flt)
        # spm.add_capture_zone_observer(spl)
        # spm.add_capture_zone_observer(sc)

        # spm.add_sample_observer(spl)

        sc.add_samples_observer(flt)
        sc.add_samples_observer(spl)

        # spl.add_images_observer(sc)

        # wc.add_window(spl)
        wc.add_window(flt)
        wc.add_window(sc)

        self._instances_by_rectangle_id = defaultdict(list)

        self._prev = None
        self._rid = None

        self._drawn_instance = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._capture_zone_factory = None

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

        sampling = self._sampling

        sampling.set_scene(scene)

        itc.width = scene.width
        itc.height = scene.height

        capture_zones = self._capture_zones
        ins_by_rid = self._instances_by_rectangle_id

        czf = capture.CaptureZoneFactory(scene, ins_by_rid)

        self._display = dsp = display.RectangleDisplay(
            self._canvas)

        #load capture zones...
        with scene.connect() as connection:
            for rct in scene.get_rectangles(connection):
                cap_labels = [label for label in rl.get_rectangle_labels(connection, rct) if label.capture]

                #create capturable rectangles
                if cap_labels:
                    for instance in rct.get_instances(connection):

                        zone = dsp.draw(instance, czf)

                        capture_zones[zone.id] = zone

                        ins_by_rid[rct.id].append(zone)

        #reload all the cleared data
        sampling.load_data()

        itc.on_left_click(self._on_left_click)

        itc.start(capture_zones)

    def clear_tool(self):
        self._drawn_instance = None

        #clear sampling tool
        self._sampling.clear_data()

        self._instances_by_rectangle_id.clear()

        dsp = self._display

        self._interaction.unbind()

        for cz in self._capture_zones.values():
            dsp.delete(cz)

    def _on_left_click(self, rct):
        """

        Parameters
        ----------
        rct: gscrap.data.rectangles.rectangles.RectangleInstance

        Returns
        -------

        """
        rid = rct.id

        sampling = self._sampling

        drawn_instance = self._drawn_instance
        capture_zones = self._capture_zones

        if not drawn_instance:
            self._drawn_instance = rid
            sampling.set_capture_zone(capture_zones[rid])

        elif rid != drawn_instance:
            self._drawn_instance = rid
            sampling.set_capture_zone(capture_zones[rid])

    def enable_read(self, video_meta):
        self._sampling.set_video_metadata(video_meta)

    def disable_read(self):
        self._sampling.disable_video_read()

    def stop(self):
        pass
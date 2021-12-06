from collections import defaultdict

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

        #reload all the cleared data
        sampling.load_data()

        itc.on_left_click(self._on_left_click)

        itc.start(capture_zones)

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
        self._selection_tool.set_video_metadata(video_meta)

    def disable_read(self):
        self._selection_tool.disable_video_read()

    def stop(self):
        pass
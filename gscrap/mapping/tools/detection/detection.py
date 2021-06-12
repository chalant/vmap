from gscrap.rectangles import rectangles as rt

from gscrap.data import rectangle_labels as rl, engine

from gscrap.mapping.tools.detection.sampling import sampling as spg
from gscrap.mapping.tools.detection.sampling import samples as spl
from gscrap.mapping.tools.detection.filtering import filtering
from gscrap.mapping.tools.detection import capture

from gscrap.mapping.tools import tools

from gscrap.windows import windows

class DetectionTool(tools.Tool):
    def __init__(self, main_view, thread_pool):
        """

        Parameters
        ----------
        capture_tool:
        main_view: gscrap.mapping.view.MainView
        """

        self._canvas = main_view.canvas

        self._window_manager = wm = windows.WindowModel(400, 500)
        self._windows_controller = wc = windows.WindowController(wm)

        self._filtering_model = fm = filtering.FilteringModel()
        self._filtering = flt = filtering.FilteringController(fm)

        # self._samples_model = spm = samples.SamplesModel()
        # self._samples = spl = samples.SamplesController(spm)

        self._sampling = sc = spg.SamplingController(fm)

        fm.add_filter_observer(spl)
        fm.add_filter_observer(sc)
        fm.add_filters_import_observer(flt.view())

        # spm.add_capture_zone_observer(flt)
        # spm.add_capture_zone_observer(spl)
        # spm.add_capture_zone_observer(sc)

        # spm.add_sample_observer(spl)

        sc.add_samples_observer(flt)
        sc.add_samples_observer(spl)

        # spl.add_images_observer(sc)

        wc.add_window(sc)
        # wc.add_window(spl)
        wc.add_window(flt)

        self._instances = {}

        self._prev = None
        self._rid = None

        self._items = []
        self._hashes = {}

        self._project = None

        self._thread_pool = thread_pool

        self._drawn_instance = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._height = 0
        self._width = 0

    def get_view(self, container):
        return self._windows_controller.start(container)

    def start_tool(self, project):
        """

        Parameters
        ----------
        project: models.projects.Project

        Returns
        -------
        None
        """

        canvas = self._canvas

        self._height = project.height
        self._width = project.width

        instances = self._instances

        self._project = project

        pool = self._thread_pool
        hashes = self._hashes

        #todo: set capture tool!!!

        capture_tool = None

        #todo: set detection model
        # note: depending on where we load the rectangles, we can set caching on rectangles
        # ex: in logging, we cache images

        #load capture zones...
        with engine.connect() as connection:
            for rct in project.get_rectangles(connection):
                labels = rl.RectangleLabels(rct)

                cap_labels = [label for label in labels.get_labels(connection) if label.capture]

                #create capturable rectangles
                if cap_labels:
                    for instance in rct.get_instances(connection):
                        x0, y0, x1, y1 = instance.bbox
                        rid = canvas.create_rectangle(
                            x0-1, y0-1,
                            x1, y1,
                            width=1,
                            dash=(4, 1))

                        instances[rid] = capture.CaptureZone(
                            rid,
                            instance,
                            project,
                            pool,
                            hashes,
                            capture_tool,
                            labels)

        canvas.bind("<Motion>", self.on_motion)
        canvas.bind("<Button-1>", self.on_left_click)

    def clear_tool(self):
        canvas = self._canvas
        instances = self._instances

        for rid in instances.keys():
            canvas.delete(rid)

        self._drawn_instance = None

        instances.clear()
        canvas.unbind("<Motion>")
        canvas.unbind("<Button-1>")

    def get_capture_zones(self):
        return self._instances.values()

    def _unbind(self, canvas):
        prev = self._prev

        if prev:
            canvas.itemconfigure(prev, outline="black")

    def on_motion(self, event):
        canvas = self._canvas

        x = event.x + canvas.xview()[0] * self._width
        y = event.y + canvas.yview()[0] * self._height

        instances = self._instances

        res = rt.find_closest_enclosing(instances, x, y)

        if res:
            self._rid = rid = res[0]
            self._unbind(canvas)

            rct = rt.get_rectangle(instances, rid)
            canvas.itemconfigure(rct.rid, outline="red")
            self._prev = rid
        else:
            self._unbind(canvas)
            self._rid = None

    def on_left_click(self, event):
        rid = self._rid

        if rid:
            drawn_instance = self._drawn_instance
            rct = rt.get_rectangle(self._instances, rid)

            if not drawn_instance:
                self._drawn_instance = rid
                self._sampling.set_capture_zone(rct)

            elif rid != drawn_instance:
                self._drawn_instance = rid
                self._sampling.set_capture_zone(rct)

    def set_video_metadata(self, video_meta):
        self._sampling.set_video_metadata(video_meta)

    def stop(self):
        pass
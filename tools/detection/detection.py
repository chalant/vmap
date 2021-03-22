from concurrent import futures

from controllers.rectangles import rectangles as rt

from tools.detection import capture
from tools.detection import sampling
from tools.detection import samples
from tools.detection.filtering import filtering, filters

from tools import windows

class DetectionTools(object):
    def __init__(self, container, canvas):
        """

        Parameters
        ----------
        container: tkinter.Frame
        canvas: tkinter.Canvas
        """

        self._canvas = canvas
        self._container = container

        self._window_manager = wm = windows.WindowModel(400, 500)
        self._windows_controller = wc = windows.WindowController(wm)

        wc.start(container)

        self._samples_model = spm = samples.SamplesModel()
        self._samples = spl = samples.SamplesController(spm)

        self._sampling = sc = sampling.SamplingController(spm)

        self._filtering_model = fm = filtering.FilteringModel()
        self._filtering = flt = filtering.FilteringController(fm)

        spm.add_capture_zone_observer(flt) #register filtering controller

        wm.add_window(sc)
        wm.add_window(spl)
        wm.add_window(flt)

        self._instances = {}

        self._prev = None
        self._rid = None

        self._items = []
        self._hashes = {}

        self._project = None

        self._thread_pool = futures.ThreadPoolExecutor(10)

        self._drawn_instance = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._height = 0
        self._width = 0

    def start(self, project, connection, capture_state, main_frame):
        """

        Parameters
        ----------
        project: models.projects.Project
        connection:
        capture_state: controllers.states.CaptureState


        Returns
        -------
        None
        """

        canvas = self._canvas

        self._height = main_frame.height
        self._width = main_frame.width

        instances = self._instances

        self._project = project
        pool = self._thread_pool

        hashes = self._hashes

        for rct in project.get_rectangles(connection):
            # filter cz that we can capture
            if rct.capture:
                for instance in rct.get_instances(connection):
                    x0, y0, x1, y1 = instance.bbox
                    rid = canvas.create_rectangle(x0-1, y0-1, x1, y1, width=1, dash=(4, 1))
                    instances[rid] = cz = capture.CaptureZone(
                        canvas,
                        rid,
                        instance,
                        project,
                        pool,
                        hashes)

                    # cz.initialize(connection)
            capture_state.initialize(instances.values())

        canvas.bind("<Motion>", self.on_motion)
        canvas.bind("<Button-1>", self.on_left_click)

    def clear(self):
        canvas = self._canvas
        instances = self._instances

        for rid in instances.keys():
            canvas.delete(rid)

        self._drawn_instance = None

        instances.clear()
        canvas.unbind("<Motion>")

    def get_capture_zones(self):
        return self._instances.values()

    def _unbind(self, canvas):
        prev = self._prev

        if prev:
            canvas.itemconfigure(prev, outline="black")

    def on_motion(self, event):
        #todo: should highlight siblings of the the cz we hover on.
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
            rct = rt.get_rectangle(self._instances, rid)

            if not self._drawn_instance:
                self._drawn_instance = rid
                self._samples_model.set_capture_zone(rct)

            elif rid != self._drawn_instance:
                self._drawn_instance = rid
                self._samples_model.set_capture_zone(rct)
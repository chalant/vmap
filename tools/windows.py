import tkinter as tk

class WindowModel(object):
    def __init__(self, width, max_height):
        self._window_observers = []

        self._windows = {}

        self._height = 0
        self._width = width
        self._max_height = max_height

        self._items = []

    @property
    def width(self):
        return self._width

    @property
    def max_height(self):
        return self._max_height

    def add_window(self, window):
        windows = self._windows

        for obs in self._window_observers:
            rid = obs.new_window(window)
            windows[rid] = window

    def add_window_observer(self, observer):
        self._window_observers.append(observer)

class WindowView(object):
    def __init__(self, controller, model):
        """

        Parameters
        ----------
        controller
        model: WindowModel
        """
        self._frame = None
        self._canvas = None
        self._vbar = None
        self._hbar = None

        self._model = model
        self._controller = controller

        self._count = 0

        self._height = 0
        self._row = 0

        model.add_window_observer(self)

    def render(self, container):
        self._frame = frame = tk.Frame(container)
        self._canvas = canvas = tk.Canvas(
            frame,
            height=self._model.max_height,
            width=self._model.width)

        self._vbar = vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

        vbar.config(command=canvas.yview)

        canvas.config(yscrollcommand=vbar.set)



        # canvas.configure(scrollregion=canvas.bbox("all"))
        # canvas.bind("<Configure>", lambda e:canvas.configure(scrollregion=canvas.bbox("all")))

        frame.pack(fill=tk.BOTH, expand=1)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH, expand=1)


        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)
        canvas.bind("<Button-5>", self._on_mouse_wheel)

        return canvas

    def close(self):
        frame = self._frame
        if frame:
            frame.destroy()

    def new_window(self, window):
        canvas = self._canvas
        if canvas:
            h = self._height
            frame = window.render(canvas)
            # frame.update()
            wn = canvas.create_window(self._row, h, window=frame, anchor=tk.NW)
            canvas.update()
            h += canvas.bbox(wn)[3]
            self._height = h
            canvas.configure(scrollregion=(0, 0, 0, h))
            return wn
        return

    def _on_mouse_wheel(self, event):
        # todo: should create this function as a utility function
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self._canvas.yview_scroll(-1, "units")

class WindowController(object):
    def __init__(self, model):
        self._view = WindowView(self, model)
        self._model = model

    def start(self, container):
        self._view.render(container)

    def close(self):
        self._view.close()
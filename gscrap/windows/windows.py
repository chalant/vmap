import tkinter as tk

class Element(object):
    __slots__ =  ['rid', 'bbox']

    def __init__(self, rid, bbox):
        self.rid = rid
        self.bbox = bbox

class DefaultWindowModel(object):
    def __init__(self, width, max_height):

        self._height = 0
        self._width = width
        self._max_height = max_height

    @property
    def width(self):
        return self._width

    @property
    def max_height(self):
        return self._max_height

class WindowRows(object):
    def __init__(self, controller, model):
        """

        Parameters
        ----------
        controller
        model: DefaultWindowModel
        """
        self._frame = None
        self._canvas = None
        self._vbar = None
        self._hbar = None

        self._model = model

        self._count = 0

        self._height = 0
        self._row = 0

        def null_callback(event):
            pass

        self._motion_callback = null_callback
        self._left_click_callback = null_callback
        self._right_click_callback = null_callback

        self._left_click_bind = False
        self._right_click_bind = False
        self._motion_bind = False

    def render(self, container):
        model = self._model

        self._frame = frame = tk.Frame(
            container,
            height=model.max_height,
            width=model.width
        )

        self._canvas = canvas = tk.Canvas(frame, height=model.max_height)

        self._vbar = vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

        vbar.config(command=canvas.yview)

        canvas.config(yscrollcommand=vbar.set)

        # canvas.configure(scrollregion=canvas.bbox("all"))
        # canvas.bind("<Configure>", lambda e:canvas.configure(scrollregion=canvas.bbox("all")))

        frame.pack(fill=tk.BOTH)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH)

        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)
        canvas.bind("<Button-5>", self._on_mouse_wheel)

        return frame

    def close(self):
        frame = self._frame
        if frame:
            frame.destroy()

    def add_item(self, factory, element):
        canvas = self._canvas

        h = self._height

        eid = factory.create(self._row, h, canvas, element)

        canvas.update()
        bbox = canvas.bbox(eid)

        h += bbox[3] - bbox[1]

        self._height = h

        canvas.configure(scrollregion=(0, 0, 0, h))

        return eid, bbox


    def _on_mouse_wheel(self, event):
        # todo: should create this function as a utility function
        # respond to Linux or Windows wheel event
        canvas = self._canvas

        if event.num == 5 or event.delta == -120:
            canvas.yview_scroll(1, "units")

        elif event.num == 4 or event.delta == 120:
            canvas.yview_scroll(-1, "units")

    def _on_motion(self, event):
        self._motion_callback(self._update_position(event))

    def _on_left_click(self, event):
        self._left_click_callback(self._update_position(event))

    def _on_right_click(self, event):
        self._right_click_callback(self._update_position(event))

    def _update_position(self, event):
        # x = event.x + canvas.xview()[0] * (self._x)
        # x = event.x
        # y = event.y + canvas.yview()[0] * self._height
        event.y = event.y + int(self._canvas.yview()[0] * self._height)
        return event

    def on_motion(self, callback):
        if not self._motion_bind:
            self._canvas.bind("<Motion>", self._on_motion)
            self._motion_bind = True

        self._motion_callback = callback


    def on_left_click(self, callback):
        if not self._left_click_bind:
            self._canvas.bind("<Button-1>", self._on_left_click)
            self._left_click_bind = True

        self._left_click_callback = callback

    def on_right_click(self, callback):
        if not self._right_click_bind:
            self._canvas.bind("<Button-3>", self._on_right_click)

        self._right_click_callback = callback

    def delete_element(self, id_):
        self._canvas.delete(id_)

    def clear(self):
        self._height = 0
        self._row = 0

        canvas = self._canvas

        if canvas:
            canvas.unbind("<MouseWheel>")
            canvas.unbind("<Button-4>")
            canvas.unbind("<Button-5>")

        self._right_click_bind = False
        self._left_click_bind = False
        self._motion_bind = False

class WindowController(object):
    def __init__(self, model, item_factory):
        self._view = WindowRows(self, model)
        self._model = model

        self._windows = []
        self._items = []

        self._factory = item_factory
        self._started = False

    def start(self, container):
        view = self._view
        frame = self._view.render(container)

        factory = self._factory

        windows = self._windows
        items = self._items

        for window in windows:
            rid, bbox = view.add_item(factory, window.view())
            items.append(rid)

        windows.clear()

        self._started = True

        return frame

    def add_window(self, window):
        view = self._view

        if self._started:
            rid, bbox = view.add_item(self._factory, window.view())
            self._items.append(rid)
        else:
            self._windows.append(window)

    def clear(self):
        view = self._view

        for item in self._items:
            self._view.delete_element(item)

        view.clear()

    def close(self):
        self._view.close()
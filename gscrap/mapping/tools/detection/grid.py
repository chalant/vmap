import tkinter as tk

from abc import ABC, abstractmethod

def get_canvas(grid):
    """

    Parameters
    ----------
    grid: Grid

    Returns
    -------
    tkinter.Canvas
    """
    return grid.canvas

class GridElement(ABC):
    def __init__(self, width, height):
        self.width = width
        self.height = height

class ItemFactory(ABC):
    @abstractmethod
    def create_element(self, item, canvas, x, y):
        raise NotImplementedError

    @abstractmethod
    def reload_element(self, canvas, element, x, y):
        raise NotImplementedError

def delete_items(canvas, item_ids):
    for item_id in item_ids:
        canvas.delete(item_id)

class Grid(object):
    def __init__(self, item_factory, width, height):
        self._grid_width = width
        self._grid_height = height

        self._factory = item_factory

        self._step = 2

        self._x = 0
        self._y = 0

        def null_callback(event):
            pass

        self._on_motion_callback = null_callback
        self._on_right_click_cb = null_callback
        self._on_left_click_cb = null_callback

        self._on_motion_bind = False
        self._on_left_bind = False
        self._on_right_bind = False


    def render(self, container):
        self._frame = frame = tk.Frame(container)
        self.canvas = canvas = tk.Canvas(
            frame,
            width=self._grid_width,
            height=self._grid_height)

        self._cfv_sb = cfv_sb = tk.Scrollbar(frame, orient=tk.VERTICAL)
        self._cfh_sb = cfh_sb = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        cfv_sb.config(command=canvas.yview)
        cfh_sb.config(command=canvas.xview)

        canvas.config(yscrollcommand=cfv_sb.set)
        canvas.config(xscrollcommand=cfh_sb.set)

        cfv_sb.pack(side=tk.RIGHT, fill=tk.Y)
        cfh_sb.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)
        canvas.bind("<Button-5>", self._on_mouse_wheel)

        frame.pack(fill=tk.X)
        canvas.pack(fill=tk.BOTH)

        return frame

    def add_item(self, item):
        canvas = self.canvas

        factory = self._factory

        x = self._x
        y = self._y

        step = self._step

        width  = self._grid_width

        #todo: what if the element width is bigger than the canvas width?

        element = factory.create_element(item, canvas, x, y)

        x = x + element.width + step

        if x > width:
            y = y + element.height + 2
            x = 0

        self._x = x
        self._y = y

        return element

    def reload(self, elements):
        #redraw everything

        x = 0
        y = 0

        canvas = self.canvas
        factory = self._factory

        step = self._step

        width = self._grid_width

        for element in elements:
            factory.reload_element(canvas, element, x, y)

            x = x + element.width + step

            if x > width:
                y = y + element.height + 2
                x = 0

        self._x = x
        self._y = y

        self.update()

    def update(self):
        #update grid view
        canvas = self.canvas
        h = self._grid_height
        w = self._grid_width
        y = self._y

        self._grid_height = y + 1

        if y + 1 > h:
            canvas.configure(scrollregion=(0, 0, w, y + 1))

    def _update_position(self, event):
        # x = event.x + canvas.xview()[0] * (self._x)
        # x = event.x
        # y = event.y + canvas.yview()[0] * self._height
        event.y = event.y + int(self.canvas.yview()[0] * self._grid_height)
        return event

    def _on_mouse_wheel(self, event):
        canvas = self.canvas

        if event.num == 5 or event.delta == -120:
            canvas.yview_scroll(1, "units")

        elif event.num == 4 or event.delta == 120:
            canvas.yview_scroll(-1, "units")

    def _on_right_click(self, event):
        self._on_right_click_cb(self._update_position(event))

    def _on_left_click(self, event):
        self._on_left_click_cb(self._update_position(event))

    def _on_motion(self, event):
        self._on_motion_callback(self._update_position(event))

    def on_motion(self, callback):
        if not self._on_motion_bind:
            self.canvas.bind("<Motion>", self._on_motion)
            self._on_motion_bind = True

        self._on_motion_callback = callback

    def on_right_click(self, callback):
        if not self._on_right_bind:
            self.canvas.bind("<Button-3>", self.on_right_click)
            self._on_right_bind = True

        self._on_right_click_cb = callback

    def on_left_click(self, callback):
        if not self._on_left_bind:
            self.canvas.bind("<Button-1>", self._on_left_click_cb)
            self._on_left_bind = True

        self._on_left_click_cb = callback



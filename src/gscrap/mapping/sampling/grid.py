import tkinter as tk

from abc import ABC, abstractmethod

from gscrap.mapping.tools import interaction

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

class AbstractItem(ABC):
    def __init__(self, dimensions):
        self.dimensions = dimensions

class ElementFactory(ABC):
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

        self._height = height

        self._factory = item_factory

        self._step = 2

        self._x = 1
        self._y = 1

        self._scroll_height = 1

        def null_callback(event):
            pass

        self._on_motion_callback = null_callback
        self._on_right_click_cb = null_callback
        self._on_left_click_cb = null_callback

        self._on_motion_bind = False
        self._on_left_bind = False
        self._on_right_bind = False

        self.canvas = None

        self._interaction = None
        self._rendered = False

    @property
    def height(self):
        return self._grid_height

    @property
    def width(self):
        return self._grid_width

    def render(self, container):
        self._frame = frame = tk.Frame(container,
            width=self._grid_width,
            height=self._grid_height)

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

        canvas.bind("<Button-1>", self._on_left_click_cb)
        canvas.bind("<Button-3>", self._on_right_click)

        canvas.bind("<Motion>", self._on_motion)

        frame.pack(fill=tk.X)
        canvas.pack(fill=tk.BOTH)

        return frame

    def add_item(self, item):
        """

        Parameters
        ----------
        item: AbstractItem

        Returns
        -------

        """
        canvas = self.canvas

        factory = self._factory

        x = self._x
        y = self._y

        step = self._step

        width  = self._grid_width

        #todo: what if the element width is bigger than the canvas width?

        element = factory.create_element(item, canvas, x, y)

        x = x + element.width + step

        if x + item.dimensions[0] > width:
            y += item.dimensions[1] + 2
            x = 1

        self._x = x
        self._y = y
        self._scroll_height = y + element.height

        return element

    def reset(self):
        self._x = 1
        self._y = 1
        self._grid_height = self._height

    def reload(self, elements):
        #redraw everything

        x = 1
        y = 1

        canvas = self.canvas
        factory = self._factory

        step = self._step

        width = self._grid_width

        for element in elements:
            factory.reload_element(canvas, element, x, y)

            x = x + element.width + step

            if x + element.dimensions[0] > width:
                y += element.dimensions[1] + 2
                x = 1

        self._x = x
        self._y = y

        self.update()

    def update(self):
        #update grid view
        canvas = self.canvas
        w = self._grid_width

        canvas.configure(scrollregion=(0, 0, w, self._scroll_height))

    def _adjust_mouse_position(self, event):
        # x = event.x + canvas.xview()[0] * (self._x)
        # x = event.x
        # y = event.y + canvas.yview()[0] * self._height
        event.y = event.y + int(self.canvas.yview()[0] * self._scroll_height)
        return event

    def _on_mouse_wheel(self, event):
        if self._rendered:
            canvas = self.canvas

            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, "units")

            elif event.num == 4 or event.delta == 120:
                canvas.yview_scroll(-1, "units")

    def _on_right_click(self, event):
        self._on_right_click_cb(self._adjust_mouse_position(event))

    def _on_left_click(self, event):
        self._on_left_click_cb(self._adjust_mouse_position(event))

    def _on_motion(self, event):
        self._on_motion_callback(self._adjust_mouse_position(event))

    def on_motion(self, callback):
        # if not self._on_motion_bind:
        #     self.canvas.bind("<Motion>", self._on_motion)
        #     self._on_motion_bind = True

        self._on_motion_callback = callback

    def on_right_click(self, callback):
        self._on_right_click_cb = callback

    def on_left_click(self, callback):
        self._on_left_click_cb = callback



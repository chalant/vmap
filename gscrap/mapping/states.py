

from collections import namedtuple

import Xlib.display

MyGeom = namedtuple('MyGeom', 'x y height width')

import tkinter as tk

def get_active_window(dsp, root):
    win_id = root.get_full_property(dsp.intern_atom('_NET_ACTIVE_WINDOW'),
                                    Xlib.X.AnyPropertyType).value[0]
    try:
        return dsp.create_resource_object('window', win_id)
    except Xlib.error.XError:
        pass

def get_absolute_geometry(root, win):
    """
    Returns the (x, y, height, width) of a window relative to the top-left
    of the screen.
    """
    geom = win.get_geometry()
    x, y = geom.x, geom.y

    while True:
        parent = win.query_tree().parent
        pgeom = parent.get_geometry()
        x += pgeom.x
        y += pgeom.y
        if parent.id == root.id:
            break
        win = parent

    return x, y, geom.width, geom.height

def to_bbox(x, y, w, h):
    """
    Returns (x1, y1, x2, y2) relative to the top-left of the screen.
    """
    return (x, y, x + w, y + h)

class State(object):
    def on_capture(self):
        pass

    def on_window_selection(self):
        pass

    def on_mapping(self):
        pass

    def on_resize(self, event):
        pass

class WindowSelected(State):
    # todo: need to track window position etc.
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.main_frame.MainFrame
        """
        self._manager = manager

    def on_capture(self):
        self._manager.capture_state.on_capture()

    def on_window_selection(self):
        self._manager.state = self._manager.initial
        self._manager.window_selection_button["text"] = "Select Window"

    def on_mapping(self):
        self._manager.mapping_state.on_mapping()

    def on_resize(self, event):
        # canvas = self._mapper.canvas
        # # determine the ratio of old width/height to new width/height
        # wscale = float(event.width) / canvas.winfo_width()
        # hscale = float(event.height) / canvas.winfo_height()
        # # self._mapper.template_image.resize(event.width, event.height)
        # # resize the canvas
        # # canvas.config(width=self.width, height=self.height)
        # # rescale all the objects tagged with the "all" tag
        # canvas.scale("all", 0, 0, wscale, hscale)
        pass

    def update(self):
        self._manager.capture_button["state"] = "normal"
        self._manager.window_selection_button["text"] = "Unbind Window"

    def stop(self):
        pass

class CaptureState(object):
    def on_capture(self):
        pass

    def stop(self):
        pass

    def initialize(self, handlers):
        pass

class Capturing(CaptureState):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.main_frame.MainFrame
        """
        self._manager = manager

    def on_capture(self):
        self._manager.capture_state = st = self._manager.not_capturing

        # self._mapper.next_button["state"] = "normal"
        # self._mapper.prev_button["state"] = "normal"
        self._manager.capture_tool.stop()
        st.update()

    def update(self):
        self._manager.capture_button["text"] = "Stop Capture"
        self._manager.window_selection_button["state"] = "normal"

    def initialize(self, handlers):
        capture_tool = self._manager.capture_tool
        capture_tool.clear()
        capture_tool.add_handlers(handlers)
        capture_tool.start() #resumes image_capture

    def stop(self):
        self._manager.capture_tool.stop()
        # self._manager.capture_tool.stop()
        self._manager.capture_state = self._manager.not_capturing
        self._manager.capture_state.update()

class NotCapturing(CaptureState):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: MainFrame
        """
        self._manager = manager

    def on_capture(self):
        self._manager.capture_state = st = self._manager.capturing

        # self._mapper.next_button["state"] = "normal"
        # self._mapper.prev_button["state"] = "normal"
        self._manager.capture_tool.start()
        st.update()

    def update(self):
        self._manager.capture_button["text"] = "Resume Capture"
        self._manager.window_selection_button["state"] = "normal"

    def initialize(self, handlers):
        capture_tool = self._manager.capture_tool
        capture_tool.clear()
        capture_tool.add_handlers(handlers)

    def stop(self):
        pass

class MappingInactive(object):
    def __init__(self, controller, view):
        """

        Parameters
        ----------
        controller: gscrap.mapping.controller.MappingController
        view: gscrap.mapping.view.MainView
        """

        self._controller = controller
        self._view = view

    def on_mapping(self):
        pass

    def update(self):
        self._view.mapping_button["state"] = tk.DISABLED

    def update_image(self, image):
        self._controller.mapping_tool.update_image(image)

    def stop(self):
        pass
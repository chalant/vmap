import xdo
from xdo.xdo import libxdo

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

    return MyGeom(x, y, geom.height, geom.width)

def get_window_bbox(geom):
    """
    Returns (x1, y1, x2, y2) relative to the top-left of the screen.
    """
    x = geom.x
    y = geom.y
    return (x, y, x + geom.width, y + geom.height)

class State(object):
    def on_capture(self):
        pass

    def on_window_selection(self):
        pass

    def on_mapping(self):
        pass

    def on_resize(self, event):
        pass

class Initial(State):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: mapping.main_frame.MainFrame
        """
        self._manager = manager
        self._container = self._get_container(self._manager)

        self._xdo = xdo.Xdo()

        self._img = None
        self._img_item = None


    def on_capture(self):
        self._manager.capture_state.on_capture()

    def on_window_selection(self):
        self._manager.container["cursor"] = "target"
        self._manager.container.grab_set_global()
        self._manager.container.bind('<Button-1>', self._on_click)
        self._manager.container.bind('<Button-3>', self._on_abort)

    def on_mapping(self):
        self._manager.mapping_state.on_mapping()

    def on_resize(self, event):
        pass

    def update(self):
        self._manager.capture_button["state"] = "disabled"
        self._manager.capture_button["text"] = "Start Capture"

    def _on_abort(self, event):
        self._manager.container.grab_release()
        self._manager.container["cursor"] = "arrow"

    def _on_click(self, event):

        try:
            win_id = self._xdo.get_window_at_mouse()
            self._manager.container.grab_release()

            container = self._container
            container["cursor"] = "arrow"

            self._xdo.activate_window(win_id)
            self._xdo.wait_for_window_active(win_id)

            w = self._manager.width
            h = self._manager.height

            #set window size
            if w:
                self._xdo.set_window_size(win_id, w, h)
                libxdo.xdo_wait_for_window_size(self._xdo._xdo, win_id, w, h, 0, 0)

            dsp = Xlib.display.Display()
            root = dsp.screen().root

            geom = get_absolute_geometry(root, get_active_window(dsp, root))

            img = self._manager.capture_tool.initialize(get_window_bbox(geom))

            #todo: only change state if the image was mapping_active
            self._manager.mapping_state = cst = self._manager.mapping_active
            cst.update()

            self._manager.state = self._manager.window_selected
            self._manager.on_window_selected(geom.width, geom.height, img)
        except:
            self._manager.container.grab_release()
        # self._manager.display(self._p)

    def _get_container(self, manager):
        return manager.container

    def stop(self):
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

class MappingState(object):
    def on_mapping(self):
        pass

class MappingActive(MappingState):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.main_frame.MainFrame
        """
        self._manager = manager

    def on_mapping(self):
        self._manager.mapping_tool.start(self._manager.template_image)
        self._manager.mapping_state = self._manager.mapping_inactive
        self._manager.mapping_state.update()

    def update(self):
        self._manager.mapping_button["state"] = tk.ACTIVE

    def update_image(self, image):
        pass

    def stop(self):
        pass

class MappingInactive(MappingState):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.main_frame.MainFrame
        """
        self._manager = manager

    def on_mapping(self):
        pass

    def update(self):
        self._manager.mapping_button["state"] = tk.DISABLED

    def update_image(self, image):
        self._manager.mapping_tool.update_image(image)

    def stop(self):
        pass
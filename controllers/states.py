import threading

import xdo

from controllers import display as ds

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
        manager: controllers.main_frame.MainFrame
        """
        self._manager = manager
        self._container = self._get_container(self._manager)

        self._xdo = xdo.Xdo()

        self._img = None
        self._img_item = None

    def on_capture(self):
        self._manager.capture_state.on_capture()

    def on_window_selection(self):
        self._manager.next_button["state"] = "disabled"
        self._manager.prev_button["state"] = "disabled"
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
        self._manager.next_button["state"] = "disabled"
        self._manager.prev_button["state"] = "disabled"

    def _on_abort(self, event):
        self._manager.container.grab_release()
        self._manager.container["cursor"] = "arrow"

    def _on_click(self, event):
        self._manager.state = st = self._manager.window_selected
        st.update()
        container = self._container
        win_id = self._xdo.get_window_at_mouse()
        self._manager.container.grab_release()
        container["cursor"] = "arrow"

        self._xdo.activate_window(win_id)
        self._xdo.wait_for_window_active(win_id)
        loc = self._xdo.get_window_location(win_id)
        size = self._xdo.get_window_size(win_id)

        #todo: pass in ltwh instead of bbox
        img = self._manager.capture_tool.capture(self._bbox(loc, size))
        #todo: only change state if the image was mapping_active
        self._manager.mapping_state = cst = self._manager.mapping_active
        cst.update()

        #todo: we need a cleaner way of setting left and top values
        self._manager.capture_tool._left = loc[0] - 10
        self._manager.capture_tool._top = loc[1] - 8

        self._manager.template_image, self._img_item = ds.display(img, self._manager.canvas)
        self._manager.canvas.config(scrollregion=(0,0, img.width, img.height), height=size[1], width=size[0])

    def _get_container(self, manager):
        return manager.container

    def _bbox(self, loc, size):
        x0 = loc[0] - 10
        y0 = loc[1] - 8
        return (x0, y0, x0 + size[0], y0 + size[1])

    def stop(self):
        pass

class WindowSelected(State):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.main_frame.MainFrame

        """

        """
        Window selection state: all the buttons are disabled
        until selection is done. Right click to quit selection.

        When a window is selected, it starts recording...
        Stop recording button is then activated (recording is done in the back ground
        User can navigate through frames by clicking buttons (next, previous...)
        """
        self._manager = manager

    def on_capture(self):
        self._manager.capture_state.on_capture()

    def on_window_selection(self):
        self._manager.state = st = self._manager.initial
        self._manager.window_selection_button["text"] = "Select Window"
        st.update()

    def on_mapping(self):
        self._manager.mapping_state.on_mapping()

    def on_resize(self, event):
        # canvas = self._manager.canvas
        # # determine the ratio of old width/height to new width/height
        # wscale = float(event.width) / canvas.winfo_width()
        # hscale = float(event.height) / canvas.winfo_height()
        # # self._manager.template_image.resize(event.width, event.height)
        # # resize the canvas
        # # canvas.config(width=self.width, height=self.height)
        # # rescale all the objects tagged with the "all" tag
        # canvas.scale("all", 0, 0, wscale, hscale)
        pass

    def update(self):
        self._manager.next_button["state"] = "normal"
        self._manager.prev_button["state"] = "normal"
        self._manager.capture_button["state"] = "normal"
        self._manager.window_selection_button["text"] = "Unbind Window"

    def stop(self):
        pass

class CaptureState(object):
    def on_capture(self):
        pass

    def stop(self):
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

        # self._manager.next_button["state"] = "normal"
        # self._manager.prev_button["state"] = "normal"
        self._manager.capture_tool.stop()
        st.update()

    def update(self):
        self._manager.capture_button["text"] = "Stop Capture"
        self._manager.window_selection_button["state"] = "normal"

    def stop(self):
        self._manager.capture_tool.stop()

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

        # self._manager.next_button["state"] = "normal"
        # self._manager.prev_button["state"] = "normal"
        self._manager.capture_tool.start()
        st.update()

    def update(self):
        self._manager.capture_button["text"] = "Resume Capture"
        self._manager.window_selection_button["state"] = "normal"

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

    def update(self):
        self._manager.mapping_button["state"] = "normal"

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
        self._manager.mapping_button["state"] = "disabled"

    def stop(self):
        pass
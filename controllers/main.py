from uuid import uuid4

import tkinter as tk
from PIL import ImageTk, Image

from Xlib import display
from Xlib import X
from Xlib.ext import record
from Xlib.protocol import rq

from controllers import controller
from controllers.tools import mapping
from controllers.tools import image_capture

class GrabMouse(object):
    def __init__(self, callback):
        self._display1 = None
        self._display2 = None

        self._callback = callback

    def _handle_event(self, reply):
        display = self._display2
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, display.display, None, None)
            if event.detail == X.Button1:
                print("PRESS!", event)
                #todo: if the selected element is not a window, or
                # the window is closed, etc don't change state
                self._close(display)
                self._callback(event)
            elif event.detail == X.Button3:
                print("ABORT!", event)
                self._close(display)

    def _close(self, display):
        display.record_disable_context(self._ctx)
        # display.ungrab_pointer(X.CurrentTime)
        # display.screen().root.ungrab_button(0, [0])
        display.flush()

        self._display1.record_disable_context(self._ctx)
        # self._display1.ungrab_pointer(X.CurrentTime)
        self._display1.flush()

    def _grab_pointer(self, ctx):
        display = self._display2
        try:
            # display.screen().root.grab_pointer(
            #     True,
            #     X.ButtonPressMask | X.ButtonReleaseMask, X.GrabModeAsync,
            #     X.GrabModeAsync, 0, 0, X.CurrentTime)
            display.record_enable_context(ctx, self._handle_event)
            display.record_free_context(ctx)
        except:
            self._close(display)

    def __call__(self):
        self._display1 = display.Display()
        self._display2 = dis = display.Display()

        self._ctx = ctx = dis.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.ButtonPressMask, X.ButtonReleaseMask),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])
        self._grab_pointer(ctx)


class Initial(object):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: MainFrame
        """
        self._manager = manager
        self._grab_mouse = GrabMouse(self._on_click)

    def on_capture(self):
        pass

    def on_window_selection(self):
        self._manager.next_button["state"] = "disabled"
        self._manager.prev_button["state"] = "disabled"
        self._grab_mouse()

    def on_load(self):
        pass

    def on_new(self):
        pass

    def _on_click(self, event):
        self._manager.state = self._manager.window_selected
        self._manager.next_button["state"] = "normal"
        self._manager.prev_button["state"] = "normal"
        self._manager.capture_button["state"] = "normal"
        self._manager.window_selection_button["text"] = "Unbind Window"
        self._manager.mapping_button["state"] = "normal"

class Capturing(object):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: MainFrame
        """
        self._manager = manager

    def on_capture(self):
        self._manager.state = self._manager.window_selected

        # self._manager.next_button["state"] = "normal"
        # self._manager.prev_button["state"] = "normal"
        self._manager.capture_button["text"] = "Resume Capture"
        self._manager.window_selection_button["state"] = "normal"
        self._manager.capture_tool.stop()

    def on_window_selection(self):
        pass

    def on_load(self):
        pass

    def on_new(self):
        pass


class WindowSelected(object):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: MainFrame

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
        # if selection successful, move to table mapping
        # save screen shot to common path.
        # else retry,
        # if user clicks right, move to initial state

        self._manager.state = self._manager.capturing

        # self._manager.next_button["state"] = "disabled"
        # self._manager.prev_button["state"] = "disabled"
        self._manager.capture_button["text"] = "Stop Capture"
        self._manager.window_selection_button["state"] = "disabled"
        self._manager.capture_tool.start((300, 200, 1200, 700))  # todo: pass a bounding box!


    def on_window_selection(self):
        self._manager.state = self._manager.initial
        self._manager.window_selection_button["text"] = "Select Window"

        self._manager.capture_button["state"] = "disabled"
        self._manager.capture_button["text"] = "Start Capture"

    def on_load(self):
        pass

    def on_new(self):
        pass

class Display(controller.Controller):
    def __init__(self, id_, canvas):
        super(Display, self).__init__(id_)
        self._editor = canvas
        self._flag = False

    def handle_data(self, data, emitter):
        if not self._flag:
            self._current_image = img = ImageTk.PhotoImage(data)
            self._image_item = self._editor.create_image(0, 0, image=self._current_image, anchor=tk.NW)
            self._editor.config(width=img.width(), height=img.height())
            self._flag = True
        self._current_image.paste(data)

class MainFrame(controller.Controller):
    """
    Used for editing elements and performing image capture

    We can either load sequences from a file or capture sequences from a window
    captures are made using a thread (or a process) that loops forever and takes
    screenshots. Note: We have to watch for events where the window is minimized, or is not
    on the foreground... capture must be paused on these events and resumed anytime the window
    appears... Also, when window is displaced we should track it if possible...
    """
    def __init__(self,
                 container,
                 id_,
                 rectangles):
        """

        Parameters
        ----------
        container
        id_
        rectangles: models.rectangles.Rectangles
        """
        super(MainFrame, self).__init__(id_)
        self._container = container

        commands = tk.LabelFrame(container, text="Commands")
        self._editor = editor = tk.Canvas(container)

        commands.grid(row=0, column=0, sticky="wens")
        editor.grid(row=1, column=0, sticky="wens")

        self.initial = Initial(self)
        self.window_selected = WindowSelected(self)
        self.capturing = Capturing(self)

        self._state = self.initial

        self.mapping_tool = mapping.MappingTool(self, uuid4().hex, rectangles)
        self.capture_tool = ct = image_capture.ImageCaptureTool(60)

        self._display = dis = Display(uuid4().hex, editor)

        ct.add_observer(dis, "new_frame")

        self._mapping_btn = mb = tk.Button(
            commands,
            text="Mapping",
            command=self._on_mapping,
            state="disabled"
        )

        self._capture_btn = cb = tk.Button(
            commands,
            text="Start Capture",
            command=self._on_capture,
            state="disabled"
        )

        self._win_select_btn = wb = tk.Button(
            commands,
            text="Select Window",
            command=self._on_window_selection
        )

        self._prev_btn = pb = tk.Button(commands, text="Prev", state="disabled")
        self._next_btn = nb = tk.Button(commands, text="Next", state="disabled")

        wb.grid(row=0, column=0)
        cb.grid(row=0, column=1)
        mb.grid(row=0, column=2)
        pb.grid(row=0, column=3)
        nb.grid(row=0, column=4)

        # self._thread = threading.Thread(target=self._display)
        # self._thread.start()

    @property
    def current_image(self):
        return self._current_image

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def capture_button(self):
        return self._capture_btn

    @property
    def next_button(self):
        return self._next_btn

    @property
    def prev_button(self):
        return self._prev_btn

    @property
    def window_selection_button(self):
        return self._win_select_btn

    @property
    def mapping_button(self):
        return self._mapping_btn

    def _on_mapping(self):
        pass

    def _on_capture(self):
        self._state.on_capture()

    def _on_window_selection(self):
        self._state.on_window_selection()

    def submit(self, data, event):
        data = Image.frombytes("RGB", data.size, data.bgra, "raw", "BGRX")
        # if not self._current_image:
        # store current
        if not self._flag:
            self._current_image = ImageTk.PhotoImage(data)
            self._flag = True
        self._current_image.paste(data)
        self._editor.configure(image=self._current_image)
        # self._editor.configure(image=self._current_image)
        # self._editor.update()
        # print("fps: {}".format(1 / (time.time() - t0)))

    def handle_data(self, data, emitter):
        pass


    def update(self, event, emitter):
        if event == "new":
            pass
        elif event == "open":
            pass
        elif event == "write":
            pass






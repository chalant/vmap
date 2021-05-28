from uuid import uuid4

import tkinter as tk

from gscrap.image_capture import capture_loop as ic
from gscrap.image_capture import video_recorder as vd

from gscrap.data.images import videos as vds
from gscrap.data import engine

_BUFFER_SIZE = 10 #10 mb

class VideoParams(object):
    def __init__(self, fps):
        self.fps = fps

class NewRecordView(object):
    def __init__(self, on_confirm):
        self.fps_label = None
        self.fps_input = None
        self.fps = 30

        self._on_confirm = on_confirm

    def render(self, container):
        frame = tk.Frame(container)
        options = tk.Frame(container)
        buttons = tk.Frame(container)

        option_list = (60,)

        self.fps = fps = tk.IntVar(options, value=30)

        self.fps_label = fps_label = tk.Label(options, text="FPS")
        self.fps_input = fps_input = tk.OptionMenu(options, fps, *option_list)

        self.confirm = confirm = tk.Button(
            buttons,
            text="Confirm",
            command=self._set_params)

        options.pack(fill=tk.BOTH, side=tk.TOP)
        buttons.pack(fill=tk.BOTH, side=tk.TOP)

        fps_label.grid(row=0, column=0)
        fps_input.grid(row=0, column=1)
        confirm.pack()
        frame.pack()

    def _set_params(self):
        self._on_confirm(VideoParams(self.fps.get()))

class LoadRecordView(object):
    def __init__(self, on_confirm):
        self._on_confirm = on_confirm

    def render(self, container):
        pass

class RecordingView(object):
    def __init__(self, controller):
        self.record_button = None

        self._controller = controller

        self.frame = None

    def render(self, container):
        self.frame = frame = tk.Frame(container)

        bar = tk.Frame(frame)

        controller = self._controller

        self.file_mb = file_mb = tk.Menubutton(bar, text="File")

        self.file_menu = file_menu = tk.Menu(file_mb, tearoff=0)

        file_menu.add_command(label="New", command=controller.on_new)
        file_menu.add_command(label="Open", command=controller.on_load)

        file_menu.entryconfig("New", state=tk.DISABLED)
        file_menu.entryconfig("Open", state=tk.DISABLED)

        file_mb.config(menu=file_menu)

        # self.new_button = tk.Menubutton(
        #     bar,
        #     text="New",
        #     state=tk.DISABLED,
        #     command=controller.on_new
        # )
        #
        # self.open_button = tk.Menubutton(
        #     bar,
        #     text="Open",
        #     state=tk.DISABLED,
        #     command = controller.on_open
        # )

        self.record_button = rb = tk.Button(
            frame,
            text="Record",
            state=tk.DISABLED,
            command=controller.on_record
        )

        frame.pack(expand=1, fill=tk.X)
        bar.pack(side=tk.TOP, fill=tk.X, expand=1)
        file_mb.pack(side=tk.LEFT)
        rb.pack()

        return frame

class RecordingController(object):
    def __init__(self, thread_pool, container, callback=None):
        self._container = container

        self._view = RecordingView(self)

        self._top_level = None
        self._new_view = NewRecordView(self.on_new_confirm)
        self._load_view = LoadRecordView(self.on_load_confirm)

        self._looper = ic.CaptureLoop()

        self._recording = False

        self._window_set = False

        self._project = None
        self._window = None

        self._vid_params = None

        self._thread_pool = thread_pool

        self._recorder = None

        self._meta = None

        self._record_observers = []

        def null_callback(event):
            pass

        self._callback = callback if callback else null_callback

    def view(self):
        return self._view

    def on_record(self):
        recording = self._recording
        view = self._view
        looper = self._looper

        if not recording:
            view.record_button["text"] = "Pause"
            looper.start(self._recorder, self._meta.fps)
            self._recording = True
        else:
            view.record_button["text"] = "Resume"
            looper.stop()
            self._recording = False

    def on_new(self):

        def on_abort():
            self._new_abort()
            window.grab_release()
            window.destroy()

        self._top_level = window = tk.Toplevel(self._view.frame)

        window.grab_set()

        window.title("New Record")
        window.geometry("294x150")

        window.resizable(False, False)

        window.wm_attributes("-topmost", 1)
        window.protocol("WM_DELETE_WINDOW", on_abort)

        def alarm(event):
            window.focus_force()
            window.bell()

        window.bind("<FocusOut>", alarm)

        self._new_view.render(window)

    def on_load(self):

        def on_abort():
            self._load_abort()
            window.destroy()
            window.grab_release()

        self._top_level = window = tk.Toplevel(self._view.frame)

        window.grab_set()

        window.title("Load Record")
        window.geometry("294x150")

        window.resizable(False, False)
        window.wm_attributes("-topmost", 1)

        window.protocol("WM_DELETE_WINDOW", on_abort)

        def alarm(event):
            window.focus_force()
            window.bell()

        window.bind("<FocusOut>", alarm)

        self._load_view.render(window)

    def _has_videos(self, project):
        with engine.connect() as connection:
            try:
                next(project.get_video_metadata(connection))
                return True
            except StopIteration:
                return False

    def set_project(self, project):
        self._project = project
        view = self._view

        if self._window:
            view.file_menu.entryconfig("New", state=tk.NORMAL)

            if self._has_videos(project):
                view.file_menu.entryconfig("Open", state=tk.NORMAL)

    def set_window(self, window):
        view = self._view

        self._window = window
        project = self._project

        if project:
            view.file_menu.entryconfig("New", state=tk.NORMAL)

            if self._has_videos(project):
                view.file_menu.entryconfig("Open", state=tk.NORMAL)

    def unbind_window(self):
        view = self._view

        self._window = None

        view.file_menu.entryconfig("New", state=tk.DISABLED)
        view.file_menu.entryconfig("Open", state=tk.DISABLED)

    def on_new_confirm(self, video_params):
        view = self._view
        project = self._project
        window = self._window

        view.record_button["state"] = tk.NORMAL

        self._meta = meta = vds.VideoMetadata(
            project.name,
            uuid4().hex,
            len(ic.capture(window.xywh)),
            video_params.fps)


        self._recorder = vd.VideoRecorder(
            meta,
            window.xywh,
            self._thread_pool,
            _BUFFER_SIZE)

        #save metadata
        with engine.connect() as connection:
            meta.submit(connection)

        self._top_level.destroy()

        #notify observers that there is a new record
        self._callback(meta)

    def _new_abort(self):
        view = self._view

        view.record_button["state"] = tk.DISABLED

    def on_load_confirm(self, video_meta):
        # notify observers that we opened a new record
        self._callback(video_meta)

        self._top_level.destroy()

    def _load_abort(self):
        pass

    def add_record_observer(self, observer):
        self._record_observers.append(observer)

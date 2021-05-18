from uuid import uuid4

import tkinter as tk

from gscrap.image_capture import image_capture as ic
from gscrap.image_capture import video as vd

from gscrap.data.images import videos as vds
from gscrap.data import engine

_BUFFER_SIZE = 10 #10 mb

class NewRecordView(object):
    def __init__(self, controller):
        self._controller = controller

        self.fps_label = None
        self.fps_input = None

    def render(self, container):
        #todo: options are: Uncapped, 30 or 60
        # default is 30 rolling window?
        options = tk.Frame(container)

        controller = self._controller

        self.fps_label = tk.Label(options)
        self.fps_input = tk.Entry(options)

        self.confirm = tk.Button(
            options,
            text="Confirm",
            command=controller.on_new_confirm)

class LoadRecordView(object):
    def __init__(self, controller):
        self._controller = controller

    def render(self, container):
        pass

class RecordingView(object):
    def __init__(self, controller):
        self.record_button = None

        self._controller = controller

    def render(self, container):
        frame = tk.Frame(container)

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

        self._new_view = NewRecordView(self)
        self._load_view = LoadRecordView(self)

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
            view.record_button["text"] = "Play"
            looper.stop()
            self._recording = False

    def on_new(self):
        window = tk.Toplevel(self._container)

        self._new_view.render(window)

    def on_load(self):
        window = tk.Toplevel(self._container)

        self._load_view.render(window)

    def set_project(self, project):
        self._project = project

    def set_window(self, window):
        view = self._view

        self._window = window

        if self._project:
            view.file_menu.entryconfig("New", state=tk.NORMAL)
            view.file_menu.entryconfig("Open", state=tk.NORMAL)

    def unbind_window(self):
        view = self._view

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
            video_params.fps)

        self._recorder = vd.VideoRecorder(
            meta.path,
            window.xywh,
            self._thread_pool,
            _BUFFER_SIZE)

        #save video metadata
        with engine.connect() as connection:
            meta.submit(connection)

        #notify observers that there is a new record
        self._callback(meta)

    def on_new_abort(self):
        view = self._view

        view.record_button["state"] = tk.DISABLED

    def on_load_confirm(self, video_meta):
        # notify observers that we opened a new record
        self._callback(video_meta)

    def on_load_abort(self):
        pass

    def add_record_observer(self, observer):
        self._record_observers.append(observer)

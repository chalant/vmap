import tkinter as tk
from uuid import uuid4

from gscrap.data.images import videos as vds

from gscrap.mapping.tools.capture.records import loading

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
        frame = tk.Frame(container)

        self._canvas = canvas = tk.Canvas(frame)

        canvas.create_window()

        canvas.pack(fill=tk.BOTH)

        return frame

class RecordsView(object):
    def __init__(self, controller):
        self._controller = controller

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

        frame.pack(expand=1, fill=tk.X)
        bar.pack(side=tk.TOP, fill=tk.X, expand=1)

        file_mb.pack(side=tk.LEFT)

        return frame

class RecordsController(object):
    def __init__(self, project, on_new=None, on_load=None):
        self._view = RecordsView(self)

        def null_callback(meta):
            pass

        self._new_view = NewRecordView(self.on_new_confirm)

        self._loading = loading.RecordLoadController(
            self.on_load_confirm,
            294, 300)

        self._scene = None

        self._load_callback = on_load if on_load else null_callback
        self._new_callback = on_new if on_new else null_callback

        self._window = None
        self._project = project

    def view(self):
        return self._view

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

        loader = self._loading

        def on_abort():
            self._load_abort()
            window.grab_release()
            window.destroy()

        self._top_level = window = tk.Toplevel(self._view.frame)

        window.grab_set()

        window.title("Load Record")
        window.geometry("294x350")

        window.resizable(False, False)
        window.wm_attributes("-topmost", 1)

        window.protocol("WM_DELETE_WINDOW", on_abort)

        def alarm(event):
            window.focus_force()
            window.bell()

        window.bind("<FocusOut>", alarm)

        #render window

        loader.load_records(self._scene.project, window)

    def _has_videos(self, project):
        with project.connect() as connection:
            try:
                next(project.get_video_metadata(connection))
                return True
            except StopIteration:
                return False

    def set_window(self, window):
        view = self._view

        self._window = window
        scene = self._scene

        if scene:
            view.file_menu.entryconfig("New", state=tk.NORMAL)

    def unbind_window(self):
        view = self._view

        self._window = None

        view.file_menu.entryconfig("New", state=tk.DISABLED)
        # view.file_menu.entryconfig("Open", state=tk.DISABLED)

    def set_scene(self, scene):
        self._scene = scene
        view = self._view

        if self._window:
            view.file_menu.entryconfig("New", state=tk.NORMAL)

        if self._has_videos(scene.project):
            view.file_menu.entryconfig("Open", state=tk.NORMAL)

    def on_new_confirm(self, video_params):
        scene = self._scene

        self._meta = meta = vds.VideoMetadata(
            uuid4().hex,
            video_params.fps,
            (int(scene.width), int(scene.height)))

        # self._recorder = vd.VideoRecorder(
        #     meta,
        #     window.xywh,
        #     self._thread_pool,
        #     _BUFFER_SIZE)

        #save metadata
        with self._project.connect() as connection:
            meta.submit(connection)

        self._top_level.destroy()

        #notify observers that there is a new record
        self._new_callback(meta)

    def on_load_confirm(self, video_meta):
        self._top_level.destroy()

        # notify observers that we opened a record
        self._load_callback(video_meta)

    def _new_abort(self):
        pass

    def _load_abort(self):
        pass
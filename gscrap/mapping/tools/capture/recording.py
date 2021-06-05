from datetime import datetime, timedelta

import tkinter as tk

from gscrap.image_capture import video_recorder as vd

_BUFFER_SIZE = 10 #10 mb

class VideoParams(object):
    def __init__(self, fps):
        self.fps = fps

class VariableLabel(object):
    def __init__(self, container, name, row, value):
        self.frame = frame = container
        self.var = var = tk.StringVar(frame, value=value)
        self.var_container = vc = tk.Label(frame, textvariable=var, width=15)
        self.label = label = tk.Label(frame, text=name)

        vc.grid(column=0, row=row)
        label.grid(column=1, row=row)

        frame.pack()

    def set(self, value):
        self.var.set(value)

    def get(self):
        return self.var.get()

class RecordingView(object):
    def __init__(self, controller):
        self.record_button = None

        self._controller = controller

        self.frame = None

    def render(self, container):
        self.frame = frame = tk.LabelFrame(container, text="Recorder")


        controller = self._controller

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

        self.record_frame = rf = tk.Frame(frame)

        self.record_button = rb = tk.Button(
            rf,
            text="Record",
            state=tk.DISABLED,
            command=controller.on_record,
            width=5)

        frame.pack(expand=1, fill=tk.X)

        rb.pack()
        rf.pack(side=tk.LEFT)

        self.info_frame = info = tk.Frame(frame)

        self.frames = VariableLabel(info, "Frames", 0, 0.0)
        self.fps = VariableLabel(info, "FPS", 1, 0.0)
        self.size = VariableLabel(info, "Size", 2, "0KB")
        self.time = VariableLabel(info, "Time", 3, "00:00:00.00")

        info.pack()

        return frame

class RecordingController(object):
    def __init__(self, recording_callback=None):
        self._view = RecordingView(self)

        self._readers = []

        self._top_level = None

        self._recording = False

        self._window = None

        self._vid_params = None

        self._recorder = vd.RecordingProcess(self._recording_update)

        self._meta = None

        def null_callback(event):
            pass

        self._callback = recording_callback if recording_callback else null_callback

        self._frames = 0
        self._size = 0
        self._time = datetime.strptime("00:00:00.00","%H:%M:%S.%f")

    def _recording_update(self, data):
        view = self._view

        view.frames.set(self._frames + data["frames"])
        view.fps.set(data["fps"])
        view.size.set("{}{}".format(self._size + data["size"], "KB"))
        dt = data["time"]

        t = self._time + timedelta(
            hours=dt.hour,
            minutes=dt.minute,
            seconds=dt.second,
            microseconds=dt.microsecond)

        view.time.set(t.strftime("%H:%M:%S.%f")[:11])

    def view(self):
        return self._view

    def on_record(self):
        recording = self._recording
        view = self._view
        window = self._window

        recorder = self._recorder

        if not recording:
            view.record_button["text"] = "Pause"
            # looper.start(self._recorder, self._meta.fps)
            recorder.start_recording(
                self._meta,
                window.xywh[0],
                window.xywh[1])

            self._recording = True
        else:
            view = self._view

            self._frames = int(view.frames.get())
            self._size = int(view.size.get()[:4])
            self._time = datetime.strptime(view.time.get(), "%H:%M:%S.%f")

            view.record_button["text"] = "Resume"
            # looper.stop()

            #disable read
            for reader in self._readers:
                reader.disable_read()

            recorder.stop_recording()

            for reader in self._readers:
                reader.enable_read(self._meta)

            self._recording = False

    def add_reader(self, reader):
        self._readers.append(reader)

    def set_record_info(self, video_metadata, window):
        self._meta = video_metadata
        self._view.record_button["state"] = tk.NORMAL
        self._window = window

    def unbind_window(self):
        self._view.record_button["state"] = tk.DISABLED
        self._recorder.stop_recording()
        self._window = None

    def stop(self):
        self._recorder.stop_recording()

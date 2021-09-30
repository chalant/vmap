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
    def __init__(self, project, recording_callback=None):
        self._project = project

        self._view = RecordingView(self)

        self._readers = []

        self._top_level = None

        self._recording = False

        self._window = None

        self._vid_params = None

        self._recorder = vd.Recorder(self._recording_update)

        self._meta = None

        def null_callback(event):
            pass

        self._callback = recording_callback if recording_callback else null_callback

        self._frames = 0
        self._size = 0
        self._time = None

    def _recording_update(self, data):
        view = self._view
        meta = self._meta

        view.frames.set(meta.frames + data["frames"])
        view.fps.set(data["fps"])
        view.size.set("{}{}".format(meta.byte_size + data["size"], "KB"))
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
        meta = self._meta

        if not recording:
            view.record_button["text"] = "Pause"
            # looper.start(self._recorder, self._meta.fps)
            recorder.start_recording(
                meta,
                window.xywh[0],
                window.xywh[1])

            self._recording = True
        else:
            view = self._view

            view.record_button["text"] = "Resume"
            # looper.stop()

            #disable read while we merge the two files...
            for reader in self._readers:
                reader.disable_read()

            recorder.stop_recording()

            size = view.size.get()
            t = view.time.get()

            # params = vd.read_video_params(meta.path)
            #
            # if 'length' in params:
            #     meta.frames = params['length']
            # else:
            meta.frames = int(view.frames.get())

            meta.byte_size = int(view.size.get()[:len(size) - 2])
            meta.time = view.time.get()
            meta.time = t

            with self._project.connect() as connection:
                meta.submit(connection)

            #notify readers with new metadata
            for reader in self._readers:
                reader.enable_read(meta)

            self._recording = False

    def add_reader(self, reader):
        self._readers.append(reader)

    def set_record_info(self, video_metadata):
        if self._window:
            # stop recording
            if self._recording:
                self.on_record()

            self._view.record_button["state"] = tk.NORMAL

        self._time = datetime.strptime(video_metadata.time,"%H:%M:%S.%f")
        self._meta = video_metadata

    def set_window(self, window):
        self._window = window

        meta = self._meta

        if meta:
            #stop recording
            if self._recording:

                self.on_record()

            self._view.record_button["state"] = tk.NORMAL

    def unbind_window(self):
        self._view.record_button["state"] = tk.DISABLED
        self._recorder.stop_recording()
        self._window = None

    def stop(self):
        #stop recording
        if self._recording:
            self.on_record()

        # if self._meta:
        #     #submit changes to video metadata
        #     with engine.connect() as connection:
        #         self._meta.submit(connection)

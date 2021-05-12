from gscrap.image_capture import image_capture as ic
from gscrap.image_capture import video as vd

from gscrap.mapping.tools import tools
from gscrap.windows import windows

class ImageReader(object):
    pass

class CaptureTool(tools.Tool):
    def __init__(self, thread_pool):
        self._looper = ic.CaptureLoop()
        self._video_recorder = None
        self._thread_pool = thread_pool
        self._fps = 30

    def initialize(self, window):
        pass

    def initialize(self, path, window, fps=30, buffer_size=10):
        #todo: frame per second are also bound to the project.
        # project can have multiple footage.

        self._video_recorder = vd.VideoRecorder(
            path,
            window.xywh,
            buffer_size
        )

        self._fps = fps

    def get_view(self):
        return

    def start_tool(self, project):
        pass

    def clear_tool(self):
        pass

    def start_capture(self):
        self._looper.start(
            self._video_recorder,
            self._fps)

    def stop_capture(self):
        self._looper.stop()

from gscrap.image_capture import video_recorder as vd

from gscrap.mapping.tools import tools, navigation
from gscrap.mapping.tools.capture import recording

from gscrap.windows import windows

class CaptureTool(tools.Tool):
    def __init__(
            self,
            main_view,
            main_controller,
            thread_pool):

        """

        Parameters
        ----------
        main_view: gscrap.mapping.view.MainView
        main_controller: gscrap.mapping.controller.MappingController
        thread_pool:
        """

        self._main_controller = main_controller

        self._window_manager = wm = windows.WindowModel(400, 500)
        self._window_controller = wc = windows.WindowController(wm)

        self._container = container = main_view.right_frame

        self._recorder = recorder = recording.RecordingController(
            thread_pool,
            container,
            self._video_update
        )

        #todo: set a video filter
        self._navigator = navigator = navigation.NavigationController(
            main_controller.template_update
        )

        nv = navigation.NavigationView(160, 90)
        navigator.set_view(nv)

        wc.add_window(recorder)
        wc.add_window(navigator)

        def null_callback(event):
            return

        self._callback = null_callback

    def bind_window(self, window):
        self._recorder.set_window(window)

    def _video_update(self, video_metadata):
        self._navigator.set_video_metadata(video_metadata)

        self._callback(video_metadata)

    def on_video_update(self, callback):
        self._callback = callback

    def get_view(self, container):
        return self._window_controller.start(container)

    def start_tool(self, project):
        self._recorder.set_project(project)

    def clear_tool(self):
        #clear data
        pass

    def unbind_window(self):
        self._recorder.unbind_window()

    def stop(self):
        #todo: stop recording loop
        pass

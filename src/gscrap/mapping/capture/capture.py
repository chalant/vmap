from gscrap.mapping.tools import tools, navigation
from gscrap.mapping.capture import recording
from gscrap.mapping.capture.records import records

from gscrap.windows import windows, factory

class CaptureTool(tools.Tool):
    def __init__(
            self,
            main_view,
            main_controller,
            project):

        """

        Parameters
        ----------
        main_view: gscrap.mapping.view.MainView
        main_controller: gscrap.mapping.controller.MappingController
        project: gscrap.projects.projects.Project
        """

        self._main_controller = main_controller

        self._window_manager = wm = windows.DefaultWindowModel(400, 500)
        self._window_controller = wc = windows.WindowController(
            wm,
            factory.WindowFactory()
        )

        self._container = main_view.right_frame

        self._records = rcd = records.RecordsController(
            project,
            self._new_video,
            self._video_open)

        self._recorder = recorder = recording.RecordingController(project)

        #todo: set a video filter
        self._navigator = navigator = navigation.NavigationController(
            main_controller.template_update
        )

        recorder.add_reader(navigator)

        nv = navigation.NavigationView(160, 90)
        navigator.set_view(nv)

        wc.add_window(rcd)
        wc.add_window(recorder)
        wc.add_window(navigator)

        def null_callback(event):
            return

        #for any element that observers capture events etc.
        self._callback = null_callback

    def bind_window(self, window):
        self._records.set_window(window)
        self._recorder.set_window(window)

    def _new_video(self, video_metadata):
        self._recorder.set_record_info(video_metadata)

    def _video_open(self, video_metadata):
        self._recorder.set_record_info(video_metadata)
        self._navigator.set_video_metadata(video_metadata)

        self._callback(video_metadata)

    def _recorder_update(self, video_metadata):
        self._navigator.set_video_metadata(video_metadata)

        self._callback(video_metadata)

    def add_video_reader(self, reader):
        #subscribe video reader
        #the recorder disables or enables a reader
        self._recorder.add_reader(reader)

    def on_video_update(self, callback):
        self._callback = callback

    def get_view(self, container):
        return self._window_controller.start(container)

    def start_tool(self, scene):
        self._records.set_scene(scene)

    def clear_tool(self):
        #todo: clear any loaded data
        #clear data
        pass

    def unbind_window(self):
        self._recorder.unbind_window()
        self._records.unbind_window()

    def stop(self):
        self._recorder.stop()

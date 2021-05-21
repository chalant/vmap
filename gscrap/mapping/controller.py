import tkinter as tk

from concurrent import futures

from PIL import ImageTk

import gscrap.mapping.view as vw

from gscrap.mapping.tools.mapping import mapping
from gscrap.mapping.tools.detection import detection
from gscrap.mapping.tools.capture import capture
from gscrap.mapping.tools import tools

import gscrap.mapping.menu as mn

class MappingController(object):
    def __init__(self, projects, root, window_selector):
        self._thread_pool = pool = futures.ThreadPoolExecutor(10)

        self._view = mv = vw.MainView(root, self)

        mv.mapping_button["state"] = tk.DISABLED

        self._mapping_tool = mapping.MappingTool(root)
        self._projects = projects

        self._menu = menu = mn.MenuBar(root, self, projects)
        self._menu_controller = mn.MenuBarController(menu, projects)

        # main states
        self._window_selector = window_selector

        self._window_selected = False
        self._mapping_active = False

        self._tools = tls = tools.ToolsController(mv.right_frame)
        self._detection_tool = dtc = detection.DetectionTool(mv, pool)
        self._capture_tool = cpt = capture.CaptureTool(mv, self, pool)

        tls.add_tool(dtc, "Detection")
        tls.add_tool(cpt, "Capture")

        # self._detection_view = cpt.get_view(mv.right_frame)

        cpt.on_video_update(self._video_update)

        self._current_project = None

        self._template = None

    def on_mapping(self):
        view = self._view
        menu = self._menu

        def on_close(event):
            # called when mapping tool closes
            self._mapping_active = False

            # enable menu bar
            self._view.mapping_button["state"] = tk.NORMAL
            menu.enable_menu()

            #todo: reload capture zones (tools -> reload)

        if not self._mapping_active:
            view.window_selection["state"] = tk.DISABLED
            view.mapping_button["state"] = tk.DISABLED

            menu.disable_menu()


            self._mapping_tool.start(on_close)
            self._mapping_active = True

    def project_update(self, project):
        """

        Parameters
        ----------
        project: gscrap.projects.Project

        Returns
        -------

        """
        view = self._view
        mapping_tool = self._mapping_tool

        def template_load(image):
            #callback for when a template is loaded

            view.mapping_button["state"] = tk.NORMAL

            self._template = template = ImageTk.PhotoImage(image)

            view.display(template)

            # self._detection_tool.start_tool(project)
            self._tools.set_project(project)
            #initialize mapping tool
            mapping_tool.set_template(template)
            mapping_tool.set_project(project)

            view.window_selection["state"] = tk.NORMAL

        def on_error(error):
            pass

        if project.width: #project has a template
            view.mapping_button["state"] = tk.NORMAL
            #load template image
            project.load_template(template_load, on_error)

        self._current_project = project


    def template_update(self, image):
        self._template.paste(image)

    def _video_update(self, video_meta):
        self._detection_tool.set_video_metadata(video_meta)

    def stop(self):
        #todo save everything before closing...
        #todo: overwrite previous template?
        self._mapping_tool.stop()
        self._capture_tool.stop()
        self._detection_tool.stop()

    def new_project(self):
        # todo:
        #  if there is already an existing project, we need to close it properly
        #  (save it, or create a dialog box to confirm save?)
        #  also, if we're capturing and/or mapping, we need to save and stop everything

        self._menu.new_dialog.start(self.project_update)

    def open_project(self):
        # todo:
        #  if there is already an existing project, we need to close it properly
        #  (save it, or create a dialog box to confirm save?)
        #  also, if we're capturing and/or mapping, we need to save and stop everything
        self._menu.open_dialog.start(self.project_update)

    def window_selection(self):
        #todo: activate image capture tool...

        view = self._view
        window_selector = self._window_selector
        capture_tool = self._capture_tool
        detection_tool = self._detection_tool

        def on_error():
            pass

        def on_abort():
            self._window_selected = False
            # view.container["cursor"] = "arrow"

        def on_selected(event):
            self._window_selected = True

            project = self._current_project

            width = project.width

            if width:
                window_selector.resize_window(
                    event.window_id,
                    width,
                    project.height)
            else:
                #set project width and height to the captured selected window
                project.width = event.width
                project.height = event.height

            #change the values of the window event
            event.width = project.width
            event.height = project.height

            #initialize capture tool
            capture_tool.bind_window(event)

            # view.container["cursor"] = "arrow"

            # view.capture_button["state"] = tk.NORMAL
            # view.capture_button["text"] = "Start Capture"

            view.window_selection["text"] = "Unbind Window"

            view.mapping_button["state"] = tk.NORMAL

        if not self._window_selected:
            # view.container["cursor"] = "target"

            window_selector.start_selection(
                on_selected,
                on_abort,
                on_error)

        else:
            # view.capture_button["state"] = tk.DISABLED
            # view.capture_button["text"] = "Start Capture"

            view.window_selection["text"] = "Select Window"
            view.window_selection["state"] = tk.NORMAL

            capture_tool.unbind_window()

            self._window_selected = False

    #image navigation functions



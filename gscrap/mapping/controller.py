import tkinter as tk

from concurrent import futures

from gscrap.tools import window_selection as ws

from gscrap.mapping import view as vw
from gscrap.mapping.tools.mapping import mapping
from gscrap.mapping.tools.detection import detection
from gscrap.mapping import menu as mn

from gscrap.mapping.tools.capture import capture
from gscrap.mapping.tools import tools


class MappingController(object):
    def __init__(self, projects, root):
        self._thread_pool = pool = futures.ThreadPoolExecutor(10)

        self._view = mv = vw.MainView(root, self)

        projects.add_observer(self) #register to projects

        mv.mapping_button["state"] = tk.DISABLED
        mv.capture_button["state"] = tk.DISABLED

        self._mapping_tool = mapping.MappingTool(root)
        self._projects = projects

        self._menu = menu = mn.MenuBar(root, self, projects)
        self._menu_controller = mn.MenuBarController(menu, projects)

        # main states
        self._window_selector = ws.WindowSelector(root)

        self._window_selected = False
        self._mapping_active = False

        # self.mapping_inactive = states.MappingInactive(self, mv)
        # self.mapping_state = self.mapping_inactive

        self._tools = tls = tools.ToolsController(root)
        self._detection_tool = dtc = detection.DetectionTools(self, mv)
        self._capture_tool = cpt = capture.CaptureTool(pool)

        tls.add_tool(dtc, "Detection")
        tls.add_tool(cpt, "Capture")

        self._current_project = None

        self._template = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        value.update()
        self._state = value

    def on_mapping(self):
        menu = self._menu
        view = self._view

        def on_close():
            # called when mapping tool closes
            self._mapping_active = False

            # enable menu bar
            self._menu.menu_bar["state"] = tk.NORMAL
            self._view.mapping_button["state"] = tk.NORMAL

        if not self._mapping_active:
            menu.menu_bar["state"] = tk.DISABLED
            view.mapping_button["state"] = tk.DISABLED

            self._mapping_tool.start(on_close)
            self._mapping_active = True

    def project_update(self, project):
        view = self._view
        mapping_tool = self._mapping_tool

        def template_load(image):
            #callback for when a template is loaded
            view.mapping_button["state"] = tk.NORMAL

            self._template = template = tk.PhotoImage(image)

            view.display(template)

            self._detection_tool.start_tool(project)

            #initialize mapping tool
            mapping_tool.set_template(template)
            mapping_tool.set_project(project)

            view.window_selection_button["state"] = tk.NORMAL

        if project.width: #project has a template
            view.mapping_button["state"] = tk.NORMAL
            #load template image
            project.load_template(template_load)


    def stop(self):
        #todo save everything before closing...
        pass

    def new_project(self):
        # todo:
        #  if there is already an existing project, we need to close it properly
        #  (save it, or create a dialog box to confirm save?)
        #  also, if we're capturing and/or mapping, we need to save and stop everything

        self._menu.new_dialog.start()

    def open_project(self):
        # todo:
        #  if there is already an existing project, we need to close it properly
        #  (save it, or create a dialog box to confirm save?)
        #  also, if we're capturing and/or mapping, we need to save and stop everything

        self._menu.open_dialog.start()

    def window_selection(self):
        #todo: activate image capture tool...

        view = self._view
        window_selector = self._window_selector
        capture_tool = self._capture_tool

        def on_error():
            pass

        def on_abort():
            self._window_selected = False
            view.container["cursor"] = "arrow"

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
            #todo: a project can have multiple footages
            # we need to add an "video" option in the menu bar, where we can open footages etc.
            capture_tool.initialize(project, event)

            view.container["cursor"] = "arrow"

            view.capture_button["state"] = tk.NORMAL
            view.capture_button["text"] = "Start Capture"

            view.window_selection_button["text"] = "Unbind Window"

            view.mapping_button["state"] = tk.NORMAL

        if not self._window_selected:
            view.container["cursor"] = "target"

            window_selector.start_selection(
                on_selected,
                on_abort,
                on_error)

        else:
            capture_tool.stop_capture()

            self._capturing = False

            view.capture_button["state"] = tk.DISABLED
            view.capture_button["text"] = "Start Capture"

            view.window_selection_button["text"] = "Select Window"
            view.window_selection_button["state"] = tk.NORMAL

            self._window_selected = False

    #image navigation functions

    def start_capture(self):
        view = self._view
        tool = self._capture_tool
        tool.start_capture()

        view.capture_button["text"] = "Stop Capture"

        self._capturing = True

    def stop_capture(self):
        tool = self._capture_tool
        view = self._view
        #stop capture
        tool.stop_capture()

        view.capture_button["text"] = "Start Capture"

        self._capturing = False

    def next_frame(self):
        img = self._capture_tool.next_frame()

    def previous_frame(self):
        img = self._capture_tool.previous_frame()



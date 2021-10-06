import tkinter as tk

from PIL import ImageTk, Image

from gscrap.projects.scenes import scenes

from gscrap.image_capture import capture_loop as cl

import gscrap.mapping.menu as mn
import gscrap.mapping.view as vw

from gscrap.mapping.tools import tools
from gscrap.mapping.tools.capture import capture
from gscrap.mapping.tools.mapping import mapping
from gscrap.mapping.tools.detection import detection
from gscrap.mapping.tools.properties import properties


class MappingController(object):
    def __init__(self, project, root, window_selector):
        self._view = mv = vw.MainView(root, self)

        mv.mapping_button["state"] = tk.DISABLED

        self._mapping_tool = mapping.MappingTool(root)

        self._menu = menu = mn.MenuBar(root, self, project)
        self._menu_controller = mn.MenuBarController(menu, project)

        # main states
        self._window_selector = window_selector

        self._window_selected = False
        self._mapping_active = False

        self._tools = tls = tools.ToolsController(mv.right_frame)
        self._detection_tool = dtc = detection.DetectionTool(mv)
        self._capture_tool = cpt = capture.CaptureTool(mv, self, project)
        self._properties_tool = ppt = properties.Properties(mv)

        tls.add_tool(dtc, "Detection")
        tls.add_tool(ppt, "Properties")
        tls.add_tool(cpt, "Capture")

        # self._detection_view = cpt.get_view(mv.right_frame)

        cpt.on_video_update(self._video_update)

        cpt.add_video_reader(dtc)

        self._scene = None

        self._template = None

    def on_mapping(self):
        view = self._view
        menu = self._menu


        def on_close(event):
            # called when mapping tool closes
            self._mapping_active = False

            # enable menu bar
            self._view.mapping_button["state"] = tk.NORMAL
            self._view.window_selection["state"] = tk.NORMAL

            menu.enable_menu()

            #todo: code smell!
            #todo: instead of reloading everything, we could just pass
            # the mapping dict to the detection tool dict and reload from memory
            # instead of files.
            self._detection_tool.clear_tool()
            self._detection_tool.start_tool(self._scene)



            #todo: reload capture zones (tools -> reload)

        if not self._mapping_active:
            view.window_selection["state"] = tk.DISABLED
            view.mapping_button["state"] = tk.DISABLED

            menu.disable_menu()

            self._mapping_tool.start(on_close)

            self._mapping_active = True


    def scene_update(self, scene):
        """

        Parameters
        ----------
        scene: gscrap.projects.scenes._Scene

        Returns
        -------

        """
        view = self._view
        mapping_tool = self._mapping_tool

        def template_load(image):
            #callback for when a template is loaded
            self._template = template = ImageTk.PhotoImage(image)

            view.display(template)

            # self._detection_tool.start_tool(project)
            self._tools.set_scene(scene)

            #initialize mapping tool
            mapping_tool.set_template(template)

            view.mapping_button["state"] = tk.NORMAL

        def on_error(error):
            pass

        scene.load_template(template_load, on_error)

        self._tools.set_scene(scene)
        mapping_tool.set_scene(scene)

        view.window_selection["state"] = tk.NORMAL

        self._scene = scene

    def template_update(self, image):
        self._template.paste(image)

    def _video_update(self, video_meta):
        self._detection_tool.enable_read(video_meta)

    def stop(self):
        #todo save everything before closing...
        #todo: overwrite previous template?
        self._mapping_tool.stop()
        self._capture_tool.stop()
        self._detection_tool.stop()

    def new_scene(self):
        # todo:
        #  if there is already an existing project, we need to close it properly
        #  (save it, or create a dialog box to confirm save?)
        #  also, if we're capturing and/or mapping, we need to save and stop everything

        self._menu.new_dialog.start(self._reset)

    def open_scene(self):
        # todo:
        #  if there is already an existing project, we need to close it properly
        #  (save it, or create a dialog box to confirm save?)
        #  also, if we're capturing and/or mapping, we need to save and stop everything

        self._menu.open_dialog.start(self._reset)

    def _reset(self, scene):
        template = self._template

        if template:
            view = self._view

            view.window_selection["text"] = "Select Window"
            view.window_selection["state"] = tk.DISABLED

            view.mapping_button["state"] = tk.DISABLED

            self.stop()

            self._view.clear()
            self._template = None

        self.scene_update(scene)

    def window_selection(self):
        #todo: activate image capture tool...

        scene = self._scene

        view = self._view
        window_selector = self._window_selector
        capture_tool = self._capture_tool

        def on_error():
            pass

        def on_abort():
            self._window_selected = False
            # view.container["cursor"] = "arrow"

        def on_selected(event):
            self._window_selected = True

            width = scene.width

            if not width:
                # set project width and height to the captured selected window
                scene.width = event.width
                scene.height = event.height

            #initialize capture tool
            capture_tool.bind_window(event)

            # view.container["cursor"] = "arrow"

            # view.capture_button["state"] = tk.NORMAL
            # view.capture_button["text"] = "Start Capture"

            view.window_selection["text"] = "Unbind Window"

            view.mapping_button["state"] = tk.NORMAL
            #store template.
            image = Image.frombytes(
                "RGB",
                (event.width, event.height),
                cl.capture(event.xywh),
                "raw",
                "BGRX")

            template = self._template

            if template:
                template.paste(image)
            else:

                # template doesn't exist so save it
                # and use dimensions as default dimensions

                template = ImageTk.PhotoImage(image)
                self._template = template

                self._view.display(template)

                with scene.connect() as connection:
                    scenes.set_dimensions(
                        connection,
                        scene,
                        image.width,
                        image.height)

            self._mapping_tool.set_template(template)

            scene.store_template(image)


        if not self._window_selected:
            # view.container["cursor"] = "target"
            width = scene.width

            if width:
                #resize the window after selection
                window_selector.start_selection(
                    on_selected,
                    on_abort,
                    on_error,
                    scene
                )
            else:
                window_selector.start_selection(
                    on_selected,
                    on_abort,
                    on_error)

        else:

            view.window_selection["text"] = "Select Window"
            view.window_selection["state"] = tk.NORMAL

            capture_tool.unbind_window()

            self._window_selected = False



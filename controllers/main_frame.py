from functools import partial

import tkinter as tk

from controllers import display as ds
from tools import image_capture, mapping
from tools.detection import detection
from controllers import states
from controllers import interface as itf

from models import projects as pjt

from data import engine

class MainFrame(object):
    def __init__(self, manager, root):

        r = 4/3
        mf = tk.Frame(manager.container, width=800, height=800*r)
        mf.grid(row=0, column=0, sticky="wens")
        mf.grid_propagate(0)

        self.container = container = mf

        # self.canvas_frame = cfr = tk.Frame(container, height=400, width=700)
        commands = tk.LabelFrame(container, text="Commands")
        self.canvas = editor = tk.Canvas(container, height=400, width=700)

        commands.pack(side=tk.TOP, fill=tk.X)
        # cfr.grid(row=1, column=0, sticky="wens")
        # cfr.grid_propagate(0)

        self.v_scroll_bar = sbarV = tk.Scrollbar(container, orient=tk.VERTICAL)
        self.h_scroll_bar = sbarH = tk.Scrollbar(container, orient=tk.HORIZONTAL)

        sbarV.config(command=self._on_y_scroll)
        sbarH.config(command=self._on_x_scroll)

        editor.config(yscrollcommand=sbarV.set)
        editor.config(xscrollcommand=sbarH.set)

        sbarV.pack(side=tk.RIGHT, fill=tk.Y)
        sbarH.pack(side=tk.BOTTOM, fill=tk.X)
        # editor.pack(fill=tk.BOTH)
        editor.pack()

        right_frame = tk.Frame(manager.container)
        right_frame.grid(row=0, column=1, sticky="wens")

        #main states
        self.initial = states.Initial(self)
        self.window_selected = states.WindowSelected(self)

        self._state = self.initial

        self.mapping_active = states.MappingActive(self)
        self.mapping_inactive = states.MappingInactive(self)

        self.mapping_state = self.mapping_inactive

        self.capturing = states.Capturing(self)
        self.not_capturing = states.NotCapturing(self)

        self.capture_state = self.not_capturing

        # editor.bind("<Configure>", self._on_resize)
        editor.bind("<MouseWheel>", self._on_mouse_wheel)
        editor.bind("<Button-4>", self._on_mouse_wheel)
        editor.bind("<Button-5>", self._on_mouse_wheel)

        self._count = 0

        self.root = root

        self.window_size = None
        self.window_id = None
        self.window_location = None

        self.template_image = None
        self._img = None

        self._interface = interface = itf.Interface(mf, self, pjt.Projects())

        menu = tk.Menu(root, tearoff=False)
        root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New", command=interface.new)
        #todo: disable open button if there is no projects.
        file_menu.add_command(label="Open", command=interface.open)

        self.mapping_tool = None
        self.capture_tool = None

        self._mapping_btn = mb = tk.Button(
            commands,
            text="Mapping",
            command=self._on_mapping,
            state="disabled"
        )

        self._capture_btn = cb = tk.Button(
            commands,
            text="Start Capture",
            command=self._on_capture,
            state="disabled"
        )

        self._win_select_btn = wb = tk.Button(
            commands,
            text="Select Window",
            command=self._on_window_selection,
            state="disabled"
        )

        wb.grid(row=0, column=0)
        cb.grid(row=0, column=1)
        mb.grid(row=0, column=2)

        self._initialized = False
        self.width = None
        self.height = None

        self._instance_mapper = detection.DetectionTools(right_frame, self.canvas)

        root = container.winfo_toplevel()
        root.wm_minsize(800, right_frame.winfo_height()) #set minimum height to toolbar

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        value.update()
        self._state = value

    @property
    def capture_button(self):
        return self._capture_btn

    @property
    def window_selection_button(self):
        return self._win_select_btn

    @property
    def mapping_button(self):
        return self._mapping_btn

    def _on_mapping(self):
        self._state.on_mapping()

    def _on_capture(self):
        self._state.on_capture()

    def _on_window_selection(self):
        self._state.on_window_selection()

    # def _on_resize(self, event):
    #     self._state.on_resize(event)

    def _on_mouse_wheel(self, event):
        # todo: each time we scroll we need to set the cursor offset
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._count -= 1
            self.canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self._count += 1
            self.canvas.yview_scroll(-1, "units")

    def _on_x_scroll(self, *args):
        self.canvas.xview(*args)

    def _on_y_scroll(self, *args):
        self.canvas.yview(*args)

    def initialize(self, project):
        """

        Parameters
        ----------
        project: models.projects.Project

        Returns
        -------

        """

        # if not self._initialized:
        with engine.connect() as con:

            self.mapping_tool = mapping.MappingTool(
                self.container,
                project)

            self.mapping_tool.on_close(self.mapping_tool_close)

            self.capture_tool = image_capture.ImageCaptureTool(
                ds.DisplayFactory(self.canvas), 30)
            # load capture areas (if any)

            # #todo: should only pass project as argument to capture tool.
            # self.capture_tool.add_handlers(project.get_rectangles(con))

            # create image_handlers. each display is bound to a cz
            self._win_select_btn["state"] = "normal"
            self.state = self.initial  # set state to initial
            self.mapping_state = self.mapping_inactive
            self.mapping_state.update()

            project.load_template(partial(self.display, project))  # load template and display it
            project.template_update(partial(self.update_display, project))  # gets notified on new template write
            project.on_update(self.update)

            self.height = project.height
            self.width = project.width

            self._initialized = True

            # else:
            #     pass
                # self.stop()
                #
                # # if self.template_image:
                # #     self.canvas.delete(self.img_item) #delete image
                # #     self.template_image = None
                # self.capture_tool.clear() #remove all image handlers
                #
                # # self._initialized = False
                #
                # self.capture_tool.add_handlers(project.get_rectangles(con))


    def display(self, project, image):
        self.template_image = image
        self._img, self.img_item = ds.display(image, self.canvas)

        self.width = w = image.width
        self.height = h = image.height

        self.mapping_state = self.mapping_active
        self.mapping_state.update()

        self.canvas.config(scrollregion=(0, 0, w, h), height=h, width=w)

        with engine.connect() as connection:
            self._instance_mapper.start(project, connection, self.capture_state, self)

    def update_display(self, project, image):
        if self._img:
            self._img.paste(image)
            self.update(project)
        else:
            self.display(project, image)

    def update(self, project):
        with engine.connect() as con:
            self._instance_mapper.clear()
            self._instance_mapper.start(project, con, self.capture_state, self)

    def mapping_tool_close(self, data):
        self.mapping_state = self.mapping_active
        self.mapping_state.update()

    def on_window_selected(self, width, height, img=None):
        self._interface.on_window_selected(width, height, img)
        self.state = self.window_selected
        # self.capture_tool.initialize(img) #initialize all image handlers

    def stop(self):
        self._state.stop()
        self.capture_state.stop()
        self.mapping_state.stop()
import tkinter as tk

from gscrap.mapping import states

class MainView(object):
    def __init__(self, root, controller):

        self._controller = controller

        r = 4/3
        mf = tk.Frame(root, width=800, height=800*r)
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

        self.right_frame = right_frame = tk.Frame(root)
        right_frame.grid(row=0, column=1, sticky="wens")

        #main states
        self.initial = states.Initial(self)
        self.window_selected = states.WindowSelected(self)

        self._state = self.initial

        # self.mapping_active = states.MappingActive(self)
        # self.mapping_inactive = states.MappingInactive(self)

        # self.mapping_state = self.mapping_inactive

        self.capturing = states.Capturing(self)
        self.not_capturing = states.NotCapturing(self)

        self.capture_state = self.not_capturing

        # editor.bind("<Configure>", self._on_resize)
        editor.bind("<MouseWheel>", self._on_mouse_wheel)
        editor.bind("<Button-4>", self._on_mouse_wheel)
        editor.bind("<Button-5>", self._on_mouse_wheel)

        self.root = root

        self.window_size = None
        self.window_id = None
        self.window_location = None

        self.template_image = None
        self._img = None


        # self.file_menu = file_menu

        self.mapping_tool = None
        self.capture_tool = None

        self.mapping_button = mb = tk.Button(
            commands,
            text="Mapping",
            command=self._on_mapping,
            state="disabled"
        )

        self.capture_button = cb = tk.Button(
            commands,
            text="Start Capture",
            command=self._on_capture,
            state="disabled"
        )

        self.window_selection_button = wb = tk.Button(
            commands,
            text="Select Window",
            command=self._on_window_selection,
            state="disabled"
        )

        self.update_button = ub = tk.Button(
            commands,
            text="Update",
            command=self._on_update,
            state="disabled"
        )

        wb.grid(row=0, column=0)
        cb.grid(row=0, column=1)
        mb.grid(row=0, column=2)
        ub.grid(row=0, column=3)

        self._initialized = False
        self.width = None
        self.height = None

        root = container.winfo_toplevel()
        root.wm_minsize(800, right_frame.winfo_height()) #set minimum height to toolbar

    def _on_mapping(self):
        self._state.on_mapping()

    def _on_capture(self):
        self._state.on_capture()

    def _on_window_selection(self):
        self._state.on_window_selection()

    # def _on_resize(self, event):
    #     self._state.on_resize(event)

    def _on_mouse_wheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def _on_x_scroll(self, *args):
        self.canvas.xview(*args)

    def _on_y_scroll(self, *args):
        self.canvas.yview(*args)

    # def _on_update(self):
    #     img = self.capture_tool.capture()
    #     self._interface.update_template(self.width, self.height, img)

    # def initialize(self, project):
    #     """
    #
    #     Parameters
    #     ----------
    #     project: models.projects.Project
    #
    #     Returns
    #     -------
    #
    #     """
    #
    #     # if not self._initialized:
    #     with engine.connect() as con:
    #
    #         self.mapping_tool = mapping.MappingTool(
    #             self.container,
    #             project)
    #
    #         self.mapping_tool.on_close(self.mapping_tool_close)
    #
    #         self.capture_tool = image_capture.CaptureLoop(30)
    #         # load capture areas (if any)
    #
    #         # #todo: should only pass project as argument to capture tool.
    #         # self.capture_tool.add_handlers(project.get_rectangles(con))
    #
    #         # create image_handlers. each display is bound to a cz
    #         self.window_selection_button["state"] = "normal"
    #         self.state = self.initial  # set state to initial
    #         self.mapping_state.update()
    #
    #         project.load_template(partial(self.display, project))  # load template and display it
    #         project.template_update(partial(self.update_display, project))  # gets notified on new template write
    #         project.on_update(self.update)
    #
    #         self.height = project.height
    #         self.width = project.width
    #
    #         self._initialized = True
    #
    #         # else:
    #         #     pass
    #             # self.stop()
    #             #
    #             # # if self.template_image:
    #             # #     self.canvas.delete(self.img_item) #delete image
    #             # #     self.template_image = None
    #             # self.capture_tool.clear() #remove all image handlers
    #             #
    #             # # self._initialized = False
    #             #
    #             # self.capture_tool.add_handlers(project.get_rectangles(con))

    def display(self, image):
        self.template_image = image

        canvas = self.canvas

        self.img_item = canvas.create_image(0, 0, image=image, anchor=tk.NW)

        self.width = w = image.width()
        self.height = h = image.height()

        canvas.config(scrollregion=(0, 0, w, h), height=h, width=w)
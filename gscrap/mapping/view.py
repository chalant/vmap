import tkinter as tk

class MainView(object):
    def __init__(self, root, controller):
        """

        Parameters
        ----------
        root
        controller: gscrap.mapping.controller.MappingController
        """

        self._controller = controller

        r = 4/3

        mf = tk.Frame(root, width=800, height=800*r)

        mf.grid(row=0, column=0, sticky="wens")

        mf.grid_propagate(False)

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

        mf.rowconfigure(0, weight=1)
        mf.columnconfigure(1, weight=1)

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

        self.mapping_button = mb = tk.Button(
            commands,
            text="Mapping",
            command=controller.on_mapping,
            state="disabled"
        )

        # self.capture_button = cb = tk.Button(
        #     commands,
        #     text="Start Capture",
        #     command=self._on_capture,
        #     state="disabled"
        # )

        self.window_selection = wb = tk.Button(
            commands,
            text="Select Window",
            command=controller.window_selection,
            state="disabled"
        )

        # self.update_button = ub = tk.Button(
        #     commands,
        #     text="Update",
        #     command=self._on_update,
        #     state="disabled"
        # )

        wb.grid(row=0, column=0)
        # cb.grid(row=0, column=1)
        mb.grid(row=0, column=1)
        # ub.grid(row=0, column=3)

        self.width = None
        self.height = None

        self.img_item = None

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

    def clear(self):
        if self.img_item:
            self.canvas.delete(self.img_item)

    def display(self, image):
        canvas = self.canvas

        self.img_item = canvas.create_image(0, 0, image=image, anchor=tk.NW)

        self.width = w = image.width()
        self.height = h = image.height()

        canvas.config(scrollregion=(0, 0, w, h), height=h, width=w)
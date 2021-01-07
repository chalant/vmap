import tkinter as tk

from controllers import display as ds
from controllers.tools import mapping
from controllers.tools import image_capture
from controllers import states
from controllers import interface as itf

from models import projects as pjt

class MainFrame(object):
    """
    Used for editing elements and performing image capture

    We capture sequences from a window
    captures are made using a thread (or a process) that loops forever and takes
    screenshots. Note: We have to watch for events where the window is minimized, or is not
    on the foreground... capture must be paused on these events and resumed anytime the window
    appears... Also, when window is displaced we should track it if possible...
    """
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

        sbarV.config(command=editor.yview)
        sbarH.config(command=editor.xview)

        editor.config(yscrollcommand=sbarV.set)
        editor.config(xscrollcommand=sbarH.set)

        sbarV.pack(side=tk.RIGHT, fill=tk.Y)
        sbarH.pack(side=tk.BOTTOM, fill=tk.X)
        # editor.pack(fill=tk.BOTH)
        editor.pack()

        right_frame = tk.LabelFrame(manager.container, text="Project")
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

        self.interface = itf.Interface(right_frame, self, pjt.Projects())

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
        self.width = 0
        self.height = 0

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
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._count -= 1
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self._count += 1
            self.canvas.yview_scroll(-1, "units")

    def initialize(self, project):
        if not self._initialized:
            # todo: load template image if it exists
            self.mapping_tool = mapping.MappingTool(
                self.container,
                project.rectangles)

            self.capture_tool = image_capture.ImageCaptureTool(
                ds.DisplayFactory(self.canvas), 30)
            # load capture areas (if any)
            self.capture_tool.add_handlers(project.rectangles.get_rectangles())
            # create image_handlers. each display is bound to a rectangle
            self._win_select_btn["state"] = "normal"

        else:
            self.stop()

            if self.template_image:
                self.canvas.delete(self.img_item) #delete image
                self.template_image = None
            self.capture_tool.clear() #remove all image handlers

            self._initialized = False

            self.capture_tool.add_handlers(project.rectangles.get_rectangles())

        self.state = self.initial  # set state to initial

        project.load_template(self.display) #load template and display it
        project.template_update(self.display) #gets notified on new template write

    def display(self, image):
        self.template_image, self.img_item = ds.display(image, self.canvas)

        self.width = w = image.width
        self.height = h = image.height

        self.canvas.config(scrollregion=(0, 0, w, h), height=h, width=w)

    def update(self, rectangles):
        # todo: add new rectangles to the capture_tool
        pass

    def stop(self):
        self._state.stop()
        self.capture_state.stop()
        self.mapping_state.stop()






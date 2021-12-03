import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

class Preview(object):
    def __init__(self, width, height):
        self.canvas = None

        self.width = int(width)
        self.height = int(height)

        self._controller = None
        self._photo_image = None

    def render(self, container):
        frame = tk.Frame(container)

        width = self.width
        height = self.height

        self.canvas = canvas = tk.Canvas(
            frame,
            width=width,
            height=height,
            bg="white"
        )

        frame.pack()
        canvas.pack()

        return frame

    def initialize(self, dimensions):
        self._dimensions = dimensions
        self._photo_image = im = ImageTk.PhotoImage(
            Image.new("RGB", dimensions, color="black")
        )

        self._item = self.canvas.create_image(
            (int(self.width / 2), int(self.height / 2)),
            image=im,
            anchor=tk.CENTER)

    def display(self, image):
        self._photo_image.paste(Image.frombuffer(
            "RGB",
            self._dimensions,
            image))

    def clear(self):
        if self._item:
            self.canvas.delete(self._item)
            self._item = None

    def set_controller(self, controller):
        self._controller = controller

class PreviewController(object):
    def __init__(self):
        self._view = None

    def view(self):
        return self._view

    def display(self, image):
        self._view.display(image)

    def initialize(self, dimensions):
        self._view.initialize(dimensions)

    def clear(self):
        self._view.clear()

    def set_view(self, view):
        self._view = view

        view.set_controller(self)


class SamplingView(object):
    def __init__(self, controller, image_grid):
        """

        Parameters
        ----------
        controller: SamplingController
        """
        self._controller = controller

        self._frame = None
        self._canvas_frame = None
        self._menu_frame = None

        self._sampling_frame = None
        self._label_frame = None
        self._label = None
        self._label_options = None

        self._label_type = None
        self._label_class = None
        self._label_instance = None

        self.label_type = None
        self.label_class = None
        self.label_instance = None

        self.label_instance_options = None
        self.label_type_options = None
        self.label_class_options = None

        self.save_button = None
        self.detect_button = None

        self.preview = Preview(80, 80)

        self._image_grid = image_grid
        self._form_row = 0

        self.max_threshold = 0

    def render(self, container):
        controller = self._controller

        self._frame = frame = tk.Frame(container)

        self._sampling_frame = sampling_frame = tk.Frame(frame)
        self._menu_frame = menu_frame = tk.Frame(sampling_frame, width=300)
        self._navigation_frame = navigation_frame = tk.LabelFrame(sampling_frame, text="Navigation")

        self._canvas_frame = canvas_frame = tk.Frame(sampling_frame)

        nav = self.preview.render(canvas_frame)

        self._label_frame = label_frame = tk.Frame(canvas_frame)
        self._label_type = label_type = tk.Label(label_frame, text="Type")
        self._label_class = label_class = tk.Label(label_frame, text="Class")
        self._label_instance = label_instance = tk.Label(label_frame, text="Label")

        self.label_type = label_type_var = tk.StringVar(label_frame, "N/A")
        self.label_class = label_class_var = tk.StringVar(label_frame, "N/A")
        self.label_instance = label_instance_var = tk.StringVar(label_frame, "")

        self.label_instance_options = lio = ttk.Combobox(
            label_frame, values=("N/A",),
            textvariable=label_instance_var,
            state='readonly')

        self.label_type_options = lto = ttk.Combobox(
            label_frame, values=("N/A",),
            textvariable=label_type_var,
            state='readonly')

        self.label_class_options = lco = ttk.Combobox(
            label_frame, values=("N/A",),
            textvariable=label_class_var,
            state='readonly')

        label_class_var.trace("w", controller.set_label_class)
        label_instance_var.trace("w", controller.set_label)
        label_type_var.trace("w", controller.set_label_type)

        self._filtering = flt = tk.Label(label_frame, text="Filters")
        self._toggles = tlg = tk.Frame(label_frame)

        self._filtering_on = flt_on = tk.Radiobutton(
            tlg, text="On",
            command=controller.enable_filters,
            value=1)

        self._filtering_off = flt_off = tk.Radiobutton(
            tlg, text="Off",
            command=controller.disable_filters,
            value=2)

        lio["state"] = tk.DISABLED
        lto["state"] = tk.DISABLED
        lco["state"] = tk.DISABLED

        self.save_button = save_button = tk.Button(
            menu_frame,
            text="Save",
            command=controller.save,
            bd=0)

        # self.detect_button = detect_button = tk.Button(
        #     menu_frame,
        #     text="Detect",
        #     command=controller.detect,
        #     bd=0)

        self.clear_button = clear_button = tk.Button(
            menu_frame,
            text="Clear",
            command=controller.clear_sample,
            bd=0
        )

        self.bin_button = bin_button = tk.Button(
            menu_frame,
            text = "Bin",
            command=controller.display_sample_bin,
            bd=0
        )

        self.filters_button = filters_button = tk.Button(
            menu_frame,
            text = "Filters",
            command=controller.display_filters,
            bd=0
        )

        save_button["state"] = tk.DISABLED
        # detect_button["state"] = tk.DISABLED
        clear_button["state"] = tk.DISABLED
        bin_button["state"] = tk.DISABLED
        filters_button["state"] = tk.DISABLED

        self._threshold_label = tlb = tk.Label(label_frame, text="Threshold")

        self.threshold = tsb = ttk.Spinbox(
            label_frame,
            from_=0,
            command=self._set_threshold)

        tsb["state"] = tk.DISABLED

        self.previous_button = prev_button = tk.Button(
            navigation_frame,
            text="Prev",
            command=controller.load_previous_batch
        )

        self.next_button = next_button = tk.Button(
            navigation_frame,
            text="Next",
            command=controller.load_next_batch
        )

        prev_button.pack(side=tk.LEFT)
        next_button.pack(side=tk.LEFT)

        prev_button["state"] = tk.DISABLED
        next_button["state"] = tk.DISABLED

        # menu.add_command(label="Save", command=controller.save)
        # menu.add_command(label="Detect", command=controller.detect)
        #
        # menu.entryconfig("Save", state=tk.DISABLED)
        # menu.entryconfig("Detect", state=tk.DISABLED)
        # menu.entryconfig("Update", state=tk.DISABLED)

        sampling_frame.grid(row=0, column=0)
        canvas_frame.grid(row=1, column=0)

        # cv.grid(row=0, column=0)
        nav.grid(row=0, column=0, sticky=tk.NW)

        label_frame.grid(row=0, column=1, sticky=tk.NW)

        # image.grid(row=0, column=0)
        # cmd.grid(row=0, column=0, sticky=tk.NW)

        # self._add_form_row(image, cmd)

        save_button.grid(row=0, column=0)
        # detect_button.grid(row=0, column=1)
        clear_button.grid(row=0, column=2)
        bin_button.grid(row=0, column=3)
        filters_button.grid(row=0, column=4)

        # save_button.config(menu=menu)

        self._add_form_row(flt, tlg)

        flt_on.grid(row=0, column=0)
        flt_off.grid(row=0, column=1)

        self._add_form_row(tlb, tsb)
        #label type
        self._add_form_row(label_type, lto)
        #label class
        self._add_form_row(label_class, lco)
        #label instance
        self._add_form_row(label_instance, lio)

        # samples image grid
        samples = tk.LabelFrame(sampling_frame, text="Samples")

        self._image_grid.render(samples)

        menu_frame.grid(row=0, sticky=tk.NW)

        navigation_frame.grid(row=2, column=0)
        samples.grid(row=3, column=0)

        return frame

    def _add_form_row(self, label, command):
        row = self._form_row

        label.grid(row=row, column=0)
        command.grid(row=row, column=1)

        row += 1

        self._form_row = row

    def _set_threshold(self):
        self._controller.set_threshold(self.threshold.get())


    def close(self):
        self._sampling_frame.destroy()
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk

class SamplingView(object):
    def __init__(self, controller, model):
        """

        Parameters
        ----------
        controller: SamplingController
        model: tools.detection.samples.SamplesModel
        """
        self._controller = controller
        self._model = model

        self._frame = None
        self._label_frame = None
        self._label = None
        self._label_options = None
        self.canvas = None

        self._commands = None
        self.update_button = None
        self.save = None
        self.menu = None

        self.label_value = None


    def capture_zone_update(self, connection, capture_zone):
        """

        Parameters
        ----------
        capture_zone: tools.detection.capture.CaptureZone

        Returns
        -------

        """
        ops = self.label_options
        # menu = ops["menu"]
        # controller = self._controller


        ops["values"] = tuple([label for label in capture_zone.get_labels(connection)])
            # menu.add_command(label=label, command=controller.set_label)

    def render(self, container):
        controller = self._controller

        self._frame = frame = tk.Frame(container)

        self._canvas_frame = cf = tk.Frame(frame)
        self.canvas = cv = tk.Canvas(cf, width=80, height=80, bg="white")

        self._label_frame = lf = tk.Frame(frame)
        self._label = lb = tk.Label(lf, text="Label")
        self.label_value = label = tk.StringVar(lf, "N/A")
        self.label_options = ops = ttk.Combobox(lf, values=("N/A",), textvariable=label)

        label.trace("w", controller.set_label)

        self._filtering = flt = tk.Label(lf, text="Filters")
        self._toggles = tlg = tk.Frame(lf)

        self._filtering_on = flt_on = tk.Radiobutton(tlg, text="On", command=controller.enable_filters, value=1)
        self._filtering__off = flt_off = tk.Radiobutton(tlg, text="Off", command=controller.disable_filters, value=2)

        ops["state"] = tk.DISABLED

        self._commands = cmd = tk.Frame(frame)
        self._image_options = image = tk.Label(lf, text="Image")
        self._menu_button = mb = tk.Menubutton(lf, text="Commands")
        self.menu = menu = tk.Menu(mb, tearoff=0)

        menu.add_command(label="Update", command=controller.update)
        menu.add_command(label="Save", command=controller.save)
        menu.add_command(label="Detect", command=controller.detect)
        # self.update_button = ub = tk.Button(cmd, text="Update", command=controller.update)  # update thumbnail
        # self.save = save = tk.Button(cmd, text="Save", command=controller.save)  # save sample
        # self.detect = detect = tk.Button(cmd, text="Detect", command=controller.detect)

        menu.entryconfig("Save", state=tk.DISABLED)
        menu.entryconfig("Detect", state=tk.DISABLED)
        menu.entryconfig("Update", state=tk.DISABLED)


        frame.grid(row=0, column=0)
        cf.grid(row=1, column=0)

        cv.grid(row=0, column=0)
        lf.grid(row=1, column=1, sticky=tk.NW)
        cmd.grid(row=0, column=0, sticky=tk.NW)

        # mb.grid(row=0, column=0)


        # lf.pack()
        tlg.grid(row=1, column=1)
        lb.grid(row=2, column=0)
        ops.grid(row=2, column=1)
        flt.grid(row=1, column=0)
        flt_on.grid(row=0, column=0)
        flt_off.grid(row=0, column=1)
        image.grid(row=0, column=0)

        mb.grid(row=0, column=1)
        mb.config(menu=menu)

        return frame

    def filter_update(self, filters):
        # todo: apply filter on image
        pass

    def update_thumbnail(self, img):
        self._thumbnail.paste(img)

    def create_thumbnail(self, image):
        self._thumbnail = tn = ImageTk.PhotoImage(image)
        controller = self._controller

        controller.set_image(image)
        canvas = self.canvas

        return canvas.create_image(
            canvas.winfo_width() / 2,
            canvas.winfo_height() / 2,
            anchor=tk.CENTER,
            image=tn)


    def close(self):
        self._frame.destroy()

class SamplingController(object):
    def __init__(self, model, filtering_model):
        """

        Parameters
        ----------
        controller: SamplingController
        model: tools.detection.samples.SamplesModel
        filtering_model: tools.detection.filtering.filtering.FilteringModel
        """

        self._model = model
        self._filtering_model = filtering_model
        self._sampling_view = SamplingView(self, model)


        self._image = None

        self._label_set = False
        self._thumbnail_set = False

        self._label = None

        self._capture_zone = None
        self._item = None

        self._filters_on = False

    def view(self):
        return self._sampling_view

    def set_image(self, image):
        self._image = image

    def update(self):
        self._image = image = self._capture_zone.capture()
        self._sampling_view.update_thumbnail(image)

    def close(self):
        self._sampling_view.close()

    def save(self):
        image = self._image
        if image:
            self._model.add_sample(image, self._label)

    def set_label(self, *args):
        if self._thumbnail_set:
            view = self._sampling_view
            view.menu.entryconfig("Save", state=tk.ACTIVE)
            # todo: set sample value
            self._label = view.label_value.get()

    def detect(self):
        #todo: detect label and display it in the label field
        #todo:
        pass

    def enable_filters(self):
        self._filtering_model.enable_filtering()

    def disable_filters(self):
        self._filtering_model.disable_filtering()

    def create_thumbnail(self, view, capture_zone):
        sv = self._sampling_view
        cz = self._capture_zone
        item = self._item

        if item and cz:
            view.canvas.delete(item)

        self._capture_zone = capture_zone
        self._image = image = capture_zone.capture()
        self._item = sv.create_thumbnail(image)
        self._thumbnail_set = True

        sv.menu.entryconfig("Update", state=tk.ACTIVE)

        view.label_options["state"] = tk.ACTIVE

        if self._label:
            sv.menu.entryconfig("Save", state=tk.ACTIVE)

    def capture_zone_update(self, connection, capture_zone):
        sv = self._sampling_view

        # can't save non-classifiable elements

        #todo: load detection model (matching if classifiable and tesseract if not)

        if not capture_zone.classifiable:
            sv.menu.entryconfig("Save", state=tk.DISABLED)

        sv.capture_zone_update(connection, capture_zone)

        self.create_thumbnail(sv, capture_zone)

    def filters_update(self, filters):
        """

        Parameters
        ----------
        filters: tools.detection.filtering.filtering.FilteringModel

        Returns
        -------

        """
        view = self._sampling_view
        image = self._image

        if image:
            if filters.filters_enabled:
                # if not self._filters_on:
                view.update_thumbnail(filters.filter_image(image))
                self._filters_on = True
            else:
                if self._filters_on:
                    view.update_thumbnail(image)
                    self._filters_on = False
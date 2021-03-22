import tkinter as tk

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
        menu = ops["menu"]
        controller = self._controller

        for label in capture_zone.get_labels(connection):
            menu.add_command(label=label, command=controller.set_label)

        controller.create_thumbnail(self, capture_zone)

    def render(self, container):
        controller = self._controller

        self._frame = frame = tk.Frame(container)

        self._canvas_frame = cf = tk.Frame(frame)
        self.canvas = cv = tk.Canvas(cf, width=80, height=80, bg="white")

        # self._label_frame = lf = tk.Frame(container)
        self._label = lb = tk.Label(cf, text="Label")
        self.label_value = label = tk.StringVar(cf, "N/A")
        self.label_options = ops = tk.OptionMenu(cf, label, "N/A")

        ops["state"] = tk.DISABLED

        self._commands = cmd = tk.Frame(cf)
        self.update_button = ub = tk.Button(cmd, text="Update", command=controller.update)  # update thumbnail
        self.save = save = tk.Button(cmd, text="Save", command=controller.save)  # save sample

        save["state"] = tk.DISABLED
        ub["state"] = tk.DISABLED

        frame.grid(row=0, column=0)
        cf.grid(row=0, column=0)

        cv.grid(row=0, column=0)
        cmd.grid(row=0, column=1)
        ub.grid(row=0, column=0)
        save.grid(row=1, column=0)
        # lf.pack()
        lb.grid(row=1, column=0)
        ops.grid(row=1, column=1)

        return frame

    def filter_update(self, filters):
        # todo: update images
        pass

    def disable_filters(self):
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
    def __init__(self, model):
        """

        Parameters
        ----------
        controller: SamplingController
        model: tools.detection.samples.SamplesModel
        """

        self._model = model
        self._sampling_view = view = SamplingView(self, model)

        self._image = None

        self._label_set = False
        self._thumbnail_set = False

        self._label = None

        self._capture_zone = None
        self._item = None

        model.add_capture_zone_observer(view)

    def view(self):
        return self._sampling_view

    def set_image(self, image):
        self._image = image

    def update(self):
        self._sampling_view.update_thumbnail(self._capture_zone.capture())

    def close(self):
        self._sampling_view.close()

    def save(self):
        image = self._image
        if image:
            self._model.add_sample(image, self._label)

    def set_label(self, value):
        if self._thumbnail_set:
            view = self._sampling_view
            view.save["state"] = tk.ACTIVE
            view.label_value.set(value) #set label value
            self._label = True

    def create_thumbnail(self, view, capture_zone):
        cz = self._capture_zone
        item = self._item

        if item and cz:
            view.canvas.delete(item)

        self._capture_zone = capture_zone
        self._item = self._sampling_view.create_thumbnail(capture_zone.capture())
        self._thumbnail_set = True

        view.label_options["state"] = tk.ACTIVE
        view.update_button["state"] = tk.ACTIVE

        if self._label:
            self._sampling_view.save["state"] = tk.ACTIVE
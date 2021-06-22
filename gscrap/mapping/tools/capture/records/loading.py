import tkinter as tk

from PIL import Image, ImageTk

from gscrap.rectangles import rectangles

from gscrap.data.images import videos
from gscrap.data import engine

from gscrap.windows import windows
from gscrap.windows import factory as fct

from gscrap.image_capture import video_reader as vr



class Info(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, container):
        info = tk.Frame(container)

        value = tk.Label(container, text=self.value)
        name = tk.Label(container, text=self.name)

        value.grid(row=0, column=0)
        name.grid(row=1, column=0)

        return info


class RecordRowView(object):
    def __init__(self, video_metadata, id_):
        self._video_metadata = video_metadata
        self.thumbnail = None
        self._image = None
        self._id = id_

    def render(self, container):
        frame = tk.Frame(container, name=self._id)
        meta = self._video_metadata

        dims = meta.dimensions

        ratio = dims[1]/dims[0]

        t_dims = (100, int(100 * ratio))

        self._image = image = ImageTk.PhotoImage(
            Image.frombytes(
                "RGB",
                t_dims,
                vr.get_thumbnail(meta, t_dims)))

        thumbnail = tk.Label(frame, image=image)
        thumbnail.pack(side=tk.LEFT)

        meta = self._video_metadata

        infos = tk.Frame(frame)

        duration = Info("Duration", meta.time).render(infos)
        # frames = Info("Frames", meta.frames).render(infos)


        duration.grid(row=0, column=0)
        # frames.grid(row=0, column=1)

        infos.pack(side=tk.LEFT)

        tags = (container,)
        #disable events on this element
        thumbnail.bindtags(tags)
        frame.bindtags(tags)
        infos.bindtags(tags)

        return frame

class RecordRow(object):
    def __init__(self, window_element, video_metadata):
        self.rid = window_element[0]
        self.bbox = bbox = window_element[1]
        self.video_metadata = video_metadata
        self.top_left = (bbox[0], bbox[1])
        self.bottom_left = (bbox[2], bbox[3])

class LoadRecordView(object):
    def __init__(self, on_confirm, window_view):
        self._on_confirm = on_confirm
        self._window_view = window_view

        self.confirm_button = None

    def render(self, container):
        frame = tk.Frame(container)

        records = tk.Frame(frame)
        buttons = tk.Frame(frame)

        rows = self._window_view.render(records)
        rows.pack(fill=tk.BOTH)

        self.confirm_button = confirm = tk.Button(
            buttons,
            text="Confirm",
            command=self._on_confirm
        )

        records.pack(fill=tk.BOTH)
        buttons.pack()
        confirm.pack(fill=tk.BOTH)

        confirm["state"] = tk.DISABLED

        return frame

class RecordLoadController(object):
    def __init__(self, on_confirm, width, height):
        self._model = model = windows.DefaultWindowModel(width, height)
        self._video_list = vl = windows.WindowRows(self, model)

        self._view = LoadRecordView(self._on_confirm, vl)

        self._items = {}

        self._callback = on_confirm

        self._rid = None
        self._selected_row = None

        self._views = []

        self._container = None

    def view(self):
        return self._view

    def load_records(self, project_name, container):
        self._container = container

        items = self._items

        factory = fct.WindowFactory()

        video_list = self._video_list
        views = self._views

        video_list.clear()
        items.clear()
        views.clear()

        index = 0

        self._view.render(container).pack()

        with engine.connect() as connection:
            for record in videos.get_metadata(connection, project_name):
                rv = RecordRowView(record, "record_row:{}".format(index))
                views.append(rv)

                element = video_list.add_item(factory, rv)
                items[index] = RecordRow(element, record)

                index += 1

        video_list.on_motion(self._on_motion)
        video_list.on_left_click(self._on_left_click)

    def _on_motion(self, event):
        # items = self._items

        # res = rectangles.find_closest_enclosing(
        #     items,
        #     event.x,
        #     event.y)

        #hack for detecting the selected window...

        widget = str(event.widget)
        idx = widget.find("record_row:")

        container = self._container

        #extract widget id
        if idx != -1:
            sl = widget[idx:len(widget)]
            lr = len("record_row:")
            self._rid = int(sl[lr:lr+1])
            container["cursor"] = "hand2"
        else:
            self._rid = None
            container["cursor"] = "arrow"

    def _on_left_click(self, event):
        if self._rid != None:
            self._selected_row = self._items[self._rid]
            self._view.confirm_button["state"] = tk.NORMAL

    def _on_confirm(self):
        self._callback(self._selected_row.video_metadata)
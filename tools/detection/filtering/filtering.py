from functools import partial

import tkinter as tk
from tkinter import ttk

from PIL import Image
import numpy as np

from data import engine
from controllers.rectangles import rectangles as rt
from tools.detection.filtering import filters

class ImageWrapper(object):
    def __init__(self, image):
        self.array = np.asarray(image)
        self.mode = image.mode

    def image(self):
        Image.from_array(self.array)

class Rectangle(object):
    def __init__(self, rid, tid, rct_idx, txt_idx, bbox, filter_):
        """

        Parameters
        ----------
        rid
        tid
        rct_idx
        txt_idx
        bbox
        filter_: filters.Filter
        """
        self._rid = rid
        self._bbox = bbox
        self._filter = filter_
        self._tid = tid
        self._rct_idx = rct_idx
        self._txt_idx = txt_idx

        self._item = None
        self._canvas = None

    @property
    def rid(self):
        return self._rid

    @property
    def tid(self):
        return self._tid

    @property
    def text_idx(self):
        return self._txt_idx

    @property
    def rectangle_idx(self):
        return self._rct_idx

    @property
    def bbox(self):
        return self._bbox

    def move(self, dx, dy):
        x0, y0, x1, y1 = self._bbox

        x0 += dx
        y0 += dy
        x1 += dx
        y1 += dy

        self._bbox = (x0, y0, x1, y1)

    @bbox.setter
    def bbox(self, value):
        self._bbox = value

    @property
    def position(self):
        return self._filter.position

    @position.setter
    def position(self, value):
        self._filter.position = value

    @property
    def top_left(self):
        bbox = self._bbox
        return bbox[0], bbox[1]

    def delete(self, connection, group):
        self._filter.delete(connection, group)

    def apply(self, img):
        self._filter.apply(img)

    def on_data_update(self, callback):
        self._filter.on_data_update(callback)

    def clear_callbacks(self):
        self._filter.clear_callbacks()

    def render(self, canvas):
        self._canvas = canvas
        frame = self._filter.render(canvas)
        self._item = canvas.create_window(0, 0, window=frame, anchor=tk.NW)

    def close(self, canvas):
        if self._item:
            canvas.delete(self._item)
        # self._filter.close()

class FilteringModel(object):
    def __init__(self):
        self._filters = filters.Filters()
        self._import_observers = []

        self._filters_observers = []
        self._filter_pipeline = []

        self._data_observers = []

        self._enabled = False

        self._to_delete = []

    def get_groups(self, connection):
        return filters.get_groups(connection)

    def add_group(self, connection, group_name, committed):
        filters.store_filter_group(connection, group_name, committed)

    def filter_image(self, img):
        im = ImageWrapper(img)

        for p in self._filter_pipeline:
            im = p.apply(im)

        return im.image()

    def create_filter(self, filter_type, filter_name, position):
        return self._filters.create_filter(filter_type, filter_name, position)

    def get_filter_types(self):
        return self._filters.get_filter_types()

    def get_filter_names(self, filter_type):
        return self._filters.get_filters(filter_type)

    def enable_filtering(self):
        # notify observers to apply filters
        for obs in self._filters_observers:
            obs.filters_update(self)

        self._enabled = True

    def disable_filtering(self):
        for obs in self._filters_observers:
            obs.disable_filters(self)

        self._enabled = False

    def import_filters(self, connection, group):
        filters = list(self._load_filters(connection, group["name"]))

        #load filter parameters
        for flt in filters:
            flt.load_parameters(connection, group)

        for obs in self._import_observers:
            obs.on_filters_import(filters)
            #the samples view observes this as-well and will update if filters are enabled

        if self._enabled: #notify observers if filters are enabled
            for obs in self._filters_observers:
                obs.filters_update(self)

        self._filters = filters
        self._data_changed = False

    def add_filter(self, filter_):
        filters = self._filter_pipeline
        filters.append(filter_)

        filter_.on_data_update(self._on_filter_change)

        for obs in self._data_observers:
            obs.data_update(self)

        if self._enabled:
            for obs in self._filters_observers:
                obs.filters_update(self)

    def add_filter_observer(self, observer):
        self._filters_observers.append(observer)

    def add_filters_import_observer(self, observer):
        self._import_observers.append(observer)

    def add_data_observers(self, observer):
        self._data_observers.append(observer)

    def remove_filter(self, position):
        filter_ = self._filter_pipeline.pop(position)
        filter_.clear_callbacks()

        self._to_delete.append(filter_)

        for obs in self._data_observers:
            obs.data_update(self)

        if self._enabled:
            for obs in self._filters_observers:
                obs.filters_update(self)

    def store_filters(self, connection, group_name):
        for flt in self._filter_pipeline:
            flt.store(connection, group_name)

    def delete_filters(self, connection):
        for flt in self._to_delete:
            flt.delete(connection)

    def get_filter(self, position):
        return self._filter_pipeline[position]

    def get_filters(self):
        return self._filter_pipeline

    def _load_filters(self, connection, group_name):
        factory = self._filters

        for res in filters.get_filters(connection, group_name):
            type_ = res["type"]
            name = res["name"]
            position = res["position"]

            flt = factory.create_filter(type_, name, position)
            flt._load_parameters(connection, group_name)

            yield flt

    def _on_filter_change(self, filter_):
        for obs in self._data_observers:
            obs.data_update(self)

class FilteringController(object):
    def __init__(self, model):
        """

        Parameters
        ----------
        model: FilteringModel
        """
        self._model = model
        self._view = FilteringView(self, model)

        self._group = None
        self._prev_group = None

        self._capture_zone = None
        self._data_changed = False

        self._i = 0

        model.add_data_observers(self)

    def view(self):
        return self._view

    def capture_zone_update(self, connection, capture_zone):
        """

                Parameters
                ----------
                connection
                capture_zone: tools.detection.capture.CaptureZone

                Returns
                -------

                """

        #todo: disable save and commit button

        # if we already have a capture zone, we need to save the filters
        cz = self._capture_zone
        view = self._view

        if cz:
            if self._data_changed:
               self.save()

        self._capture_zone = capture_zone

        try:
            self._group = group = filters.get_filter_group(
                connection,
                capture_zone.label_name,
                capture_zone.label_type)

            if group["committed"] == True:
                self._set_command_state("Save", view.file_menu, tk.DISABLED)
                self._set_command_state("Commit", view.file_menu, tk.DISABLED)

            # todo: we need to display a warning box, if there are unsaved filters.
            self._model.import_filters(connection, group)

        except:
            pass


    def _disable_command(self, name, menu):
        menu.entryconfig(name, state=tk.DISABLED)

    def _set_command_state(self, name, menu, state):
        menu.entryconfig(name, state=state)

    def data_update(self, model):
        self._i += 1
        #called any time a filter is created or modified

        self._data_changed = True

        view = self._view

        self._set_command_state("Save", view.file_menu, tk.ACTIVE)
        self._set_command_state("Commit", view.file_menu, tk.ACTIVE)

        print("Data Changed!", self._i)

    def commit(self):
        group = self._group
        model = self._model
        view = self._view
        cz = self._capture_zone

        if group:
            self._save(group["name"], True, model, cz.label_type, cz.label_name)
            group["committed"] = True
        else:
            view.new_group_popup(self._commit_callback)

        self._set_command_state("Save", view.file_menu, tk.DISABLED)
        self._set_command_state("Commit", view.file_menu, tk.DISABLED)

    def save(self):
        group = self._group
        model = self._model
        cz = self._capture_zone
        view = self._view

        if group:
            if group["committed"] == True:
                view.new_group_popup(self._replace_callback)
            else:
                self._save(group["name"], False, model, cz.label_type, cz.label_name)

        else:
            view.new_group_popup(self._save_callback)

        self._set_command_state("Save", view.file_menu, tk.DISABLED)

    def on_import(self):
        #
        self._view.import_popup(self._import_callback)

    def _commit_callback(self, group_name):
        cz = self._capture_zone
        self._save(group_name, True, self._model, cz.label_type, cz.label_name)

    def _save_callback(self, group_name):
        cz = self._capture_zone
        self._save(group_name, False, self._model, cz.label_type, cz.label_name)

    def _replace_callback(self, group_name):
        cz = self._capture_zone
        self._delete_filter_label(cz.label_type, cz.label_name)
        self._save(group_name, False, self._model, cz.label_type, cz.label_name)

    def _delete_filter_label(self, label_type, label_name):
        with engine.connect() as connection:
            filters.remove_label_from_group(
                connection,
                label_name,
                label_type)

    def _import_callback(self, group_name):
        # todo
        pass

    def _save(self, name, committed, model, label_type, label_name):

        with engine.connect() as connection:
            filters.store_filter_group(
                connection,
                name,
                committed)

            filters.store_filter_labels(
                connection,
                label_type,
                label_name)

            model.store_filters(connection, name)

        with engine.connect() as connection:
            model.delete_filters(connection)


class FilteringView(object):
    def __init__(self, controller, model):
        """

        Parameters
        ----------
        controller: FilteringController
        model: FilteringModel
        """
        self._model = model
        self._controller = controller

        self._frame = None
        self._filter_canvas = None

        self.import_button = None
        self.add_button = None

        self._rectangles = {}
        self._items = []

        self._position = 0
        self._x = 0
        self._y = 0
        self._item_idx = 0

        self._rid = None
        self._prev = None

        self._param_window = None
        self._param_item = None

    def render(self, container):
        self._frame = frame = tk.LabelFrame(container, text="Filters")
        self._menu_bar = menu = tk.Frame(frame)

        self.add_button = add = tk.Menubutton(menu, text="Add")
        self._file_mb = file_mb = tk.Menubutton(menu, text="File")
        self.file_menu = file_menu = tk.Menu(file_mb, tearoff=0)

        self._filter_menu = fm = tk.Menu(add, tearoff=0)

        controller = self._controller

        model = self._model

        file_menu.add_command(label="Import", command=controller.on_import)
        file_menu.add_command(label="Save", command=controller.save)
        file_menu.add_command(label="Commit", command=controller.commit)

        file_mb.config(menu=file_menu)

        file_menu.entryconfig("Save", state=tk.DISABLED)
        file_menu.entryconfig("Commit", state=tk.DISABLED)
        file_menu.entryconfig("Import", state=tk.DISABLED)

        #set import button state
        with engine.connect() as connection:
            for gr in model.get_groups(connection):
                if gr["committed"] == True:
                    file_menu.entryconfig("Import", state=tk.ACTIVE)
                    break


        for ft in model.get_filter_types():
            sub = tk.Menu(fm, tearoff=0)
            fm.add_cascade(label=ft, menu=sub)

            for fn in model.get_filter_names(ft):
                sub.add_command(
                    label=fn,
                    command=partial(self._add_filter, filter_type=ft, filter_name=fn))

        add.config(menu=fm)
        # todo: import filters cascade with scrollbar we need a menu with scrollbar
        self._filter_canvas = cv = tk.Canvas(frame, width=150)
        self._param_canvas = pv = tk.Canvas(frame, width=240)

        frame.pack()
        # m.pack()
        menu.pack(anchor=tk.NW)

        file_mb.grid(column=0, row=0)
        add.grid(column=2, row=0)

        cv.pack(side=tk.LEFT)
        pv.pack(side=tk.LEFT)

        cv.bind("<Button-1>", self._on_left_click)
        cv.bind("<Button-3>", self._on_right_click)
        cv.bind("<Motion>", self._on_motion) # track mouse motion

        return frame

    def on_filters_import(self, filters):
        canvas = self._filter_canvas
        items = self._items
        rectangles = self._rectangles

        self._clear(canvas, items)

        x = 0
        y = 0
        position = 0

        for filter_ in filters:
            x, y, self._add_filter_inner(
                filter_, x, y, canvas, rectangles, canvas.winfo_width())

            position += 1

        self._position = position
        self._x = x
        self._y = y

    def _create_popup(self, container):
        window = tk.Toplevel(container)
        window.geometry("+%d+%d" % (container.winfo_rootx() + 5, container.winfo_rooty() + 20))
        window.resizable(False, False)
        window.attributes('-topmost', True)

        def alarm(event):
            window.focus_force()
            window.bell()

        window.bind("<FocusOut>", alarm)

        return window

    def new_group_popup(self, callback):
        model = self._model

        with engine.connect() as connection:
            groups = set(g["name"] for g in model.get_groups(connection))

        window = self._create_popup(self._frame)

        input_ = tk.StringVar(window)

        # def alarm(event):
        #     window.focus_force()
        #     window.bell()
        #
        # window.bind("<FocusOut>", alarm)

        def execute_callback():
            callback(input_.get())
            window.destroy() # destroy window after executing callback

        def check_input(var, indx, mode):
            v = input_.get()
            if v in groups:
                ok["state"] = tk.DISABLED
                msg_var.set("Group name already exists")
                msg.config(fg="red")
            elif not v:
                msg_var.set("Please enter group name")
                msg.config(fg="black")
                ok["state"] = tk.DISABLED
            else:
                ok["state"] = tk.ACTIVE
                msg.config(fg="black")
                msg_var.set("")

        def on_close():
            if ok["state"] == tk.DISABLED:
                msg_var.set("Please enter group name")
                msg.config(fg="red")
            else:
                callback(input_.get())
                window.destroy()

        ipt_frame = tk.Frame(window)
        btn_frame = tk.Frame(window)
        msg_frame = tk.Frame(window)

        name = tk.Label(ipt_frame, text="Name")
        entry = tk.Entry(ipt_frame, textvariable=input_)

        msg_var = tk.StringVar(msg_frame, "Enter group name")
        msg = tk.Label(msg_frame, textvariable=msg_var)

        ok = tk.Button(btn_frame, text="OK", command=execute_callback)
        ok["state"] = tk.DISABLED

        ok.pack(pady=5)

        name.grid(column=0, row=0)
        entry.grid(column=1, row=0)
        msg.pack(fill=tk.BOTH, padx=5, pady=5)


        input_.trace_add("write", check_input)
        window.protocol("WM_DELETE_WINDOW", on_close)

        ipt_frame.pack(padx=5, pady=2)
        msg_frame.pack(padx=5, pady=2)
        btn_frame.pack()

    def _clear(self, canvas, items):
        for item in items:
            canvas.delete(item)

    def add_filter(self, filter_):
        pass

    def import_popup(self, callback):

        window = self._create_popup(self._frame)
        input_ = tk.StringVar(window)


        def check_input(var, indx, mode):
            v = input_.get()
            if v:
                if v in groups:
                    callback(v)
                else:
                    msg_var.set("Invalid group name")



        with engine.connect() as connection:
            groups = set([gr["name"] for gr in self._model.get_groups(connection) if gr["committed"] == True])

        msg_var = tk.StringVar(window, "Select or enter group name")
        msg = ttk.Label(window, textvariable=msg_var)
        menu = ttk.Combobox(window, values=tuple(groups), textvariable=input_, state="readonly")

        #todo: display a list box of groups that match the input at the text cursor location
        # set to readonly for now...

        input_.trace_add("write", check_input)

        menu.pack(padx=5, pady=5)
        msg.pack(padx=5, pady=2)

    def _add_filter_inner(
            self, filter_, x, y, canvas, rectangles, width):

        mw = width

        tid = canvas.create_text(x + 3, y + 2, text=filter_.type, anchor=tk.NW)
        # items.append(tid)
        # txt_idx = item_idx
        #
        # item_idx += 1

        x0, y0, x1, y1 = canvas.bbox(tid)
        x = x1 + 2

        if x >= mw:
            y = y1 + 2
            canvas.delete(tid)
            tid = canvas.create_text(3, y + 2, text=filter_.type, anchor=tk.NW)
            x0, y0, x1, y1 = canvas.bbox(tid)
            x = x1 + 2

        bbox = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)

        rid = canvas.create_rectangle(*bbox)

        # items.append(rid)

        # rct_idx = item_idx
        #
        # item_idx += 1

        rectangles[rid] = rct = Rectangle(rid, tid, 0, 0, bbox, filter_)

        self._model.add_filter(rct)

        return x, y

    def _add_filter(self, filter_type, filter_name):
        model = self._model
        position = self._position

        filter_ = model.create_filter(filter_type, filter_name, position)

        x = self._x
        y = self._y
        # item_idx = self._item_idx
        # items = self._items
        canvas = self._filter_canvas
        rectangles = self._rectangles

        x, y = self._add_filter_inner(
            filter_, x, y,
            canvas, rectangles, canvas.winfo_width())

        self._x = x
        self._y = y

        position += 1

        self._position = position

    def _on_left_click(self, event):
        # todo: display the filter parameters etc.
        if self._rid:
            canvas = self._param_canvas

            if self._param_window:
                self._param_window.close(canvas)

            filter_ = self._rectangles[self._rid]
            filter_.render(canvas)
            # self._param_item = canvas.create_window(0, 0, window=frame, anchor=tk.NW)
            self._param_window = filter_

    def _on_motion(self, event):
        filters = self._rectangles
        canvas = self._filter_canvas

        res = rt.find_closest_enclosing(filters, event.x, event.y)

        if res:
            self._rid = rid = res[0]
            self._unbind(canvas)

            canvas.itemconfigure(rid, outline="red")
            self._prev = rid
        else:
            self._unbind(canvas)
            self._rid = None

    def _on_right_click(self, event):
        if self._rid:
            menu = tk.Menu(self._frame, tearoff=0)
            menu.add_command(label="Delete", command=self._on_delete)
            menu.tk_popup(event.x_root, event.y_root)

    def _unbind(self, canvas):
        prev = self._prev
        if prev:
            canvas.itemconfigure(prev, outline="black")

    def _on_delete(self):
        self._delete_filter(self._rid)

    def _delete_filter(self, rid):
        canvas = self._filter_canvas
        filter_ = self._rectangles.pop(rid)
        model = self._model

        pipeline = model.get_filters()

        canvas.delete(filter_.rid)
        canvas.delete(filter_.tid)  # remove text

        filter_.close(self._param_canvas) #close filter parameters if opened

        # replace deleted rectangle with rectangle on the right

        pos = filter_.position

        if len(pipeline) > pos + 1:

            flt0 = pipeline[pos + 1]

            flt0.position = pos

            pr = pipeline[pos]

            bbox1 = flt0.bbox
            bbox2 = pr.bbox

            dx = bbox2[0] - bbox1[0]
            dy = bbox2[1] - bbox1[1]

            # move drawing
            flt0.move(dx, dy)
            canvas.move(flt0.rid, dx, dy)
            canvas.move(flt0.tid, dx, dy)

            # shift all positions

            try:
                mw = canvas.winfo_width()
                for flt in pipeline[pos + 2::]:
                    bbox0 = flt0.bbox
                    bbox = flt.bbox

                    x = bbox0[2]
                    y = bbox0[1]

                    dx = x - bbox[0]
                    dy = y - bbox[1]

                    # if the rectangle might exceed the canvas width, just move it to the first column and
                    # stay on the same row.

                    if bbox[2] + dx >= mw:
                        dx = -bbox[0]
                        dy = 0

                    flt.position = flt0.position + 1

                    flt.move(dx, dy)
                    canvas.move(flt.rid, dx, dy)
                    canvas.move(flt.tid, dx, dy)


                    flt0 = flt

            except IndexError:
                pass

        model.remove_filter(pos)

        if len(pipeline) == 0:
            self._x = 0
            self._y = 0
            self._position = 0

        else:
            flt = pipeline[-1]

            self._x = flt.bbox[2] + 3
            self._y = flt.bbox[1] - 1

            self._position = flt.position
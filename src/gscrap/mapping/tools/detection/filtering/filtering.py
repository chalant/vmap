from functools import partial

import tkinter as tk

import cv2

from gscrap.projects import projects
from gscrap.data.filters import filters as flt

from gscrap.rectangles import rectangles as rt


# todo: use image grid to display filter rectangles

class FilterRectangle(object):
    def __init__(self, rid, tid, bbox, filter_):
        """

        Parameters
        ----------
        rid
        tid
        bbox
        filter_: filters.Filter
        """
        self.rid = rid
        self.bbox = bbox
        self._filter = filter_
        self.tid = tid

        self._item = None
        self._canvas = None

        def null_callback(filter_):
            pass

        self._on_error = null_callback

    @property
    def type(self):
        return self._filter.type

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

    @property
    def filter_id(self):
        return self._filter.filter_id

    @property
    def group_id(self):
        return self._filter.group_id

    def get_parameters_sequence(self):
        return self._filter.get_parameters_sequence()

    def delete(self, connection, group_id, parameter_id):
        self._filter.delete(connection, group_id, parameter_id)

    def apply(self, img):
        try:
            return self._filter.apply(img)
        except cv2.error:
            self._on_error(self)
            return img

    def on_data_update(self, callback):
        self._filter.on_data_update(callback)

    def on_error(self, callback):
        self._on_error = callback

    def clear_callbacks(self):
        self._filter.clear_callbacks()

    def render(self, canvas):
        self._canvas = canvas
        frame = self._filter.render(canvas)
        self._item = canvas.create_window(0, 0, window=frame, anchor=tk.NW)

    def store(self, connection, group_id, parameter_id):
        self._filter.store(connection, group_id, parameter_id)

    def close(self, canvas):
        if self._item:
            canvas.delete(self._item)
        # self._filter.close()

    def __str__(self):
        return self._filter.__str__()


class FRFactory(object):
    def create_filter_rectangle(self, model, rid, tid, bbox, filter_):
        rct = FilterRectangle(rid, tid, bbox, filter_)
        model.add_filter(rct)
        return rct


class FRUpdateFactory(object):
    def create_filter_rectangle(self, model, rid, tid, bbox, filter_):
        filter_.rid = rid
        filter_.tid = tid
        filter_.bbox = bbox

        return filter_

class FilteringModel(object):
    def __init__(self):
        self._import_observers = []

        self._filters_observers = []
        self._filter_pipeline = []

        self._data_observers = []

        self._enabled = False

        self._to_delete = []

        self._group = None

    @property
    def filter_pipeline(self):
        return self._filter_pipeline

    @property
    def parameter_id(self):
        return flt.create_parameter_id(
            self._filter_pipeline)

    @property
    def group_id(self):
        return flt.create_group_id(self._filter_pipeline)

    @property
    def filters_enabled(self):
        return self._enabled

    def apply(self, img):
        im = img

        for p in self._filter_pipeline:
            im = p.apply(im)

        return im

    def enable_filtering(self):
        self._enabled = True

        # notify observers to apply filters
        for obs in self._filters_observers:
            obs.filters_update(self)

    def disable_filtering(self):
        self._enabled = False

        for obs in self._filters_observers:
            obs.filters_update(self)

    def import_filters(self, connection, group):
        self._group = group

        pipeline = self._filter_pipeline

        pipeline.clear()

        def loader(connection, group):
            for filter_ in self._load_filters(
                connection,
                group['group_id'],
                group['parameter_id']):
                yield filter_

        for obs in self._import_observers:
            obs.on_filters_import(self, loader(connection, group))
            # the samples view observes this as-well and will update if filters are enabled

        if self._enabled:  # notify observers if filters are enabled
            for obs in self._filters_observers:
                obs.filters_update(self)

        # self._filter_pipeline = filters

    def add_filter(self, filter_):
        pipeline = self._filter_pipeline
        pipeline.append(filter_)

        # register a call back when parameters of the filter have changed.
        filter_.on_data_update(self._on_filter_change)

        for obs in self._data_observers:
            obs.data_update(self)

        # notify when filters are updated
        for obs in self._filters_observers:
            obs.filters_update(self)

        return filter_

    def add_filter_observer(self, observer):
        self._filters_observers.append(observer)

    def add_filters_import_observer(self, observer):
        self._import_observers.append(observer)

    def add_data_observers(self, observer):
        self._data_observers.append(observer)

    def remove_filter(self, position):
        pipeline = self._filter_pipeline

        filter_ = pipeline.pop(position)

        filter_.clear_callbacks()

        self._to_delete.append(filter_)

        p = 0

        for f in pipeline:
            f.position = p
            p += 1

        for obs in self._data_observers:
            obs.data_update(self)

        for obs in self._filters_observers:
            obs.filters_update(self)

    def store_filters(self, connection, group_id, parameter_id):
        for flt in self._filter_pipeline:
            flt.store(connection, group_id, parameter_id)

    def delete_filters(self, connection, group_id, parameter_id):
        to_delete = self._to_delete

        for flt in self._to_delete:
            flt.delete(connection, group_id, parameter_id)

        to_delete.clear()

    def get_filter(self, position):
        return self._filter_pipeline[position]

    def get_filters(self):
        return self._filter_pipeline

    def _load_filters(self, connection, group_id, parameter_id):
        for res in flt.load_filters(connection, group_id, parameter_id):
            type_ = res["type"]
            name = res["name"]
            position = res["position"]

            filter_ = flt.create_filter(type_, name, position)
            filter_.load_parameters(connection, group_id, parameter_id)

            yield filter_

    def _on_filter_change(self, filter_):
        for obs in self._data_observers:
            obs.data_update(self)

        if self._enabled:
            for obs in self._filters_observers:
                obs.filters_update(self)

    def __iter__(self):
        return iter(tuple(self._filter_pipeline))

class FilteringController(object):
    def __init__(self, model):
        """

        Parameters
        ----------
        model: FilteringModel
        """
        self._model = model
        self._view = FilteringView(self, model)

        self._samples = None
        self._data_changed = False

        model.add_data_observers(self)
        model.add_filters_import_observer(self)

        self._group_id = ''
        self._parameter_id = ''

        self._scene = None

    def view(self):
        return self._view

    def on_filters_import(self, filters, loader):
        '''

        Parameters
        ----------
        filters: FilteringModel

        Returns
        -------

        '''

        #store previous group id and parameter id.

        self._group_id = filters.group_id
        self._parameter_id = filters.parameter_id


        self._view.save_button["state"] = tk.DISABLED

    def set_scene(self, scene):
        self._scene = scene

    def data_update(self, model):
        # called any time a filter is created or modified

        self._view.save_button["state"] = tk.NORMAL

    def save(self):
        self._save(self._model)

    def _save(self, filters):
        parameter_id = filters.parameter_id
        group_id = filters.group_id

        ppid = self._parameter_id
        pgid = self._group_id

        #save if parameter_id and group_id are not null
        if parameter_id and group_id:
            #only save when filters have changed.
            if parameter_id != ppid or group_id != pgid:
                with self._scene.connect() as connection:
                    #only store when the either filter group or parameter does not exist.
                    #if it exists then the filter pipeline already exists.

                    group_exists = flt.filter_group_exists(connection, group_id)
                    parameter_exists = flt.parameters_exists(connection, parameter_id)

                    if not group_exists:
                        flt.store_filter_group(
                            connection,
                            group_id)

                    if not parameter_exists:
                        flt.add_parameter_id(
                            connection,
                            parameter_id)

                    # todo: delete previously stored values
                    filters.delete_filters(
                        connection,
                        group_id,
                        parameter_id
                    )

                    if not group_exists or not parameter_exists:
                        filters.store_filters(
                            connection,
                            group_id,
                            parameter_id
                        )

        self._view.save_button["state"] = tk.DISABLED


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

        self._rectangles = {}

        self._position = 0
        self._x = 0
        self._y = 0
        self._item_idx = 0

        self._rid = None
        self._prev = None

        self._param_window = None
        self._param_item = None

        self._fr_update = FRUpdateFactory()
        self._fr_create = FRFactory()

    def render(self, container):
        self._frame = frame = tk.LabelFrame(container, text="Filters")
        self._menu_bar = menu = tk.Frame(frame)

        self.add_button = add = tk.Menubutton(menu, text="Add")

        self.save_button = save = tk.Button(
            menu,
            text="Save",
            command=self._controller.save,
            bd=0
        )

        save["state"] = tk.DISABLED

        self._filter_menu = fm = tk.Menu(add, tearoff=0)

        for ft in flt.get_filter_types():
            sub = tk.Menu(fm, tearoff=0)
            fm.add_cascade(label=ft, menu=sub)

            for fn in flt.get_filter_classes(ft):
                sub.add_command(
                    label=fn,
                    command=partial(
                        self._add_filter,
                        filter_type=ft,
                        filter_name=fn))

        add.config(menu=fm)
        # save.config(menu=fm)

        self._filter_canvas = cv = tk.Canvas(frame, width=150)
        self._param_canvas = pv = tk.Canvas(frame, width=220)

        frame.pack()
        # m.pack()
        menu.pack(anchor=tk.NW)

        # file_mb.grid(column=0, row=0)
        save.grid(column=0, row=0)
        add.grid(column=1, row=0)

        cv.pack(side=tk.LEFT)
        pv.pack(side=tk.LEFT)

        cv.bind("<Button-1>", self._on_left_click)
        cv.bind("<Button-3>", self._on_right_click)
        cv.bind("<Motion>", self._on_motion)  # track mouse motion

        return frame

    def on_filters_import(self, filters, loader):
        '''

        Parameters
        ----------
        filters: FilteringModel

        Returns
        -------

        '''
        canvas = self._filter_canvas
        rectangles = self._rectangles

        self._clear(canvas, rectangles)

        self._draw_filters(loader, canvas, rectangles, self._fr_create)

    def on_filters_clear(self):
        self._clear(self._filter_canvas, self._rectangles)

    def _draw_filters(self, filters, canvas, rectangles, factory):
        x = 0
        y = 0
        position = 0
        model = self._model

        for filter_ in filters:
            x, y = self._add_filter_inner(
                model,
                filter_,
                x, y,
                canvas,
                rectangles,
                canvas.winfo_width(),
                factory)
            position += 1

        self._position = position
        self._x = x
        self._y = y

    def _clear(self, canvas, items):
        for item in items.values():
            canvas.delete(item.rid)
            canvas.delete(item.tid)

        items.clear()

    def _add_filter_inner(
            self,
            model,
            filter_,
            x, y,
            canvas,
            rectangles,
            width,
            factory):

        mw = width

        tid = canvas.create_text(
            x + 3,
            y + 2,
            text=filter_.type,
            anchor=tk.NW)

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
        rct = factory.create_filter_rectangle(model, rid, tid, bbox, filter_)

        rct.on_error(self._on_error)

        rectangles[rid] = rct

        return x, y

    def _on_error(self, filter_):
        self._delete_filter(filter_.rid)

    def _add_filter(self, filter_type, filter_name):
        model = self._model
        position = self._position

        filter_ = flt.create_filter(filter_type, filter_name, position)

        x = self._x
        y = self._y

        canvas = self._filter_canvas
        rectangles = self._rectangles

        x, y = self._add_filter_inner(
            model, filter_, x, y,
            canvas,
            rectangles,
            canvas.winfo_width(),
            self._fr_create)

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
        # todo: clear and redraw everything

        rectangles = self._rectangles
        canvas = self._filter_canvas
        filter_ = rectangles.pop(rid)
        rectangles.clear()
        model = self._model

        canvas.unbind("<Motion>")

        self._unbind(canvas)

        self._prev = None

        pipeline = model.get_filters()

        # canvas.delete(filter_.rid)
        # canvas.delete(filter_.tid)  # remove text

        filter_.close(self._param_canvas)  # close filter parameters if opened

        # replace deleted rectangle with rectangle on the right

        pos = filter_.position
        k = pos

        # update positions
        for flt in pipeline[pos + 1::]:
            flt.position = pos
            pos += 1

        for flt in pipeline:
            canvas.delete(flt.rid)
            canvas.delete(flt.tid)

        model.remove_filter(k)

        self._draw_filters(pipeline, canvas, rectangles, self._fr_update)

        if len(pipeline) == 0:
            self._x = 0
            self._y = 0
            self._position = 0

        else:
            flt = pipeline[-1]

            self._x = flt.bbox[2] + 3
            self._y = flt.bbox[1] - 1

            self._position = flt.position + 1

        canvas.bind("<Motion>", self._on_motion)

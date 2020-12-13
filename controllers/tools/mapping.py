from functools import partial

import tkinter as tk

class RectDrawer(object):
    def __init__(self, manager, rectangles):
        self._rectangles = rectangles
        self.item = None
        self._entry = None

        # self._menus = []
        self._btn1_id = None
        self._mtn_id = None
        self._rel_id = None

        self._start = None

        self._manager = manager

    def _draw(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(start + end), **opts)

    def start(self, canvas, **opts):
        self.canvas = canvas
        self._start = None
        self._btn1_id = canvas.bind("<Button-1>", self._update, '+')
        self._mtn_id =  canvas.bind("<B1-Motion>", self._update, '+')
        self._rel_id =  canvas.bind("<ButtonRelease-1>", self._stop, '+')

        self._command = opts.pop('command', lambda *args: None)
        self.rectopts = opts

    def stop(self, canvas):
        canvas.unbind("<Button-1>", self._btn1_id)
        canvas.unbind("<B1-Motion>", self._mtn_id)
        canvas.unbind("<ButtonRelease-1>", self._rel_id)
        # self._menus.clear()

    def _update(self, event):

        if not self._start:
            self._start = (event.x, event.y)
            return
        # if self.item is not None:
        #     self.canvas.delete(self.item)
        self.item = self._draw(self._start, (event.x, event.y), **self.rectopts)
        self._command(self.start, (event.x, event.y))

    def _stop(self, event):
        self._start = None
        # self.canvas.delete(self.item)
        #todo: add rectangle to requests collection, specifying coordinates
        # and item_id

        coords = self.canvas.coords(self.item)
        # todo: add other option buttons to the rectangle, like add child etc.
        # todo: add drag capabilities

        self._entry = types = tk.Menu(self.canvas)
        clicked = tk.StringVar(self.canvas)

        for lt in self._rectangles.get_label_types():
            lbm = tk.Menu(self.canvas)

            types.add_cascade(label=lt, menu=lbm)

            for lb in self._rectangles.get_labels_of_type(lt):
                lbm.add_radiobutton(variable=clicked, label=lb["label_name"])

            # self._menus.append(lbm)

        #selected label


        self._manager.add_rectangle(self.item,  tuple(map(int, coords)))
        # e1.pack()
        w = self.canvas.create_window(coords[0], coords[1], window=types)
        #todo: place window such that it is within the canvas
        #todo: need a place for grabbing the rectangle so that we can drag the rectangle

class Drawing(object):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: MappingTool
        """
        self._drawer = RectDrawer(self, manager.rectangles)
        self._manager = manager

        self._options = menu = tk.Menu(self._manager.canvas)

        self._item = None
        self._root = None

        self._rectangles = []

        menu.add_command(label="Set Label", command=self._on_set_label)
        menu.add_command(label="Transform", command=self._on_transform)
        menu.add_command(label="Delete", command=self._on_delete)
        menu.add_separator()
        menu.add_command(label="Cancel", command=self._on_cancel)
        menu.add_command(label="Done", command=self._on_done)

        menu.entryconfig("Transform", state="disabled")
        menu.entryconfig("Delete", state="disabled")
        menu.entryconfig("Set Label", state="disabled")

    def on_right_click(self, event):
        self._item = self._manager.canvas.create_window(event.x, event.y, self._options)

        options = self._options

        res = self._manager.select_rectangle(event.x, event.y)
        if res:
            options.entryconfig("Set Label", state="normal")
            options.entryconfig("Transform", state="normal")
            options.entryconfig("Delete", state="normal")
            self._manager.rectangle = res #selected rectangle

    def _on_transform(self):
        self._manager.canvas.delete(self._item)
        self._manager.previous_state = self._manager.drawing
        self._manager.state = self._manager.editing

    def _on_delete(self):
        self._manager.remove_rectangle()

    def _on_done(self):
        self._manager.canvas.delete(self._item)
        for id_, coords in self._rectangles:
            self._manager.add_rectangle(id_, coords)

        self._on_cancel()

    def _on_cancel(self):
        canv = self._manager.canvas
        canv.unbind('<Motion>')

        self._drawer.stop(canv)
        self._manager.state = self._manager.initial
        self._rectangles.clear()

    def _on_close(self):
        self._root.destroy()

    def _selected_label(self, label_id):
        # set label id
        self._manager.rectangle.label_id = label_id

    def _on_set_label(self):
        self._root = root = tk.Toplevel(self._manager.canvas)
        root.wm_title("Set Label")

        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._label_menu = types = tk.Menu(root)
        self._selected = selected = tk.Label(root)

        lbt = tk.Menu(root)

        types.add_cascade(label="Label Types", menu=lbt)

        rectangles = self._manager.rectangles

        for lt in rectangles.get_label_types():
            lbm = tk.Menu(root)
            lbt.add_cascade(label=lt, menu=lbm)

            for lb in rectangles.get_labels_of_type(lt):
                lbm.add_command(
                    label=lb["label_name"],
                    command=partial(self._selected_label, lb["label_id"]))

        selected.grid(column=0, row=0)
        types.grid(column=1, row=0)

    def add_rectangle(self, id_, coords):
        self._rectangles.append((id_, coords))

    def update(self):
        options = self._options

        options.entryconfig("Transform", state="disabled")
        options.entryconfig("Delete", state="disabled")
        options.entryconfig("Set Label", state="disabled")

        canv = self._manager.canvas

        def cool_design(event):
            kill_xy()

            dashes = [3, 2]
            x = canv.create_line(event.x, 0, event.x, 1000, dash=dashes, tags='no')
            y = canv.create_line(0, event.y, 1000, event.y, dash=dashes, tags='no')

        def kill_xy(event=None):
            canv.delete('no')

        canv.bind('<Motion>', cool_design, '+')

        self._drawer.start(canv, fill="", width=1)


class Cloning(object):
    def __init__(self, manager):
        self._manager = manager

        self._options = m = tk.Menu(self._manager.canvas)
        m.add_command(label="Done", command=self._on_done)

    def on_right_click(self, event):
        self._manager.canvas.create_window(event.x, event.y, self._options)

    def _on_done(self):
        self._manager.state = self._manager.initial

class Editing(object):
    # when a rectangle is selected, we can modify its dimensions, or drag it
    # when changing its dimensions, the all instances of the base triangle are
    # updated and redrawn. Also, all instances of the base are highlighted as-well.

    # if we click outside a rectangle, we move back to drawing state

    # todo: need an editor (draw squares at each corner of the rectangle and the center)
    #  the center is for dragging an the corners are for resizing
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: MappingTool
        """
        self._manager = manager

        self._item = None

        self._options = m = tk.Menu(self._manager.canvas)
        self._click_point = None

        m.add_command(label="Reset", command=self._on_reset)
        m.add_separator()
        m.add_command(label="Cancel", command=self._on_cancel)
        m.add_command(label="Done", command=self._on_done)

        m.entryconfig("Reset", state="disabled")

    def on_right_click(self, event):
        self._manager.menu = self._manager.canvas.create_window(event.x, event.y, self._options)
        self._click_point = (event.x, event.y)
        res = self._manager.select_rectangle(event.x, event.y)
        options = self._options

        if res:
            options.entryconfig("Reset", state="normal")

    def _on_cancel(self):
        # todo: clear everything
        if self._manager.previous_state:
            # go back to previous state if any
            self._manager.state = self._manager.previous_state
        else:
            self._manager.state = self._manager.initial

    def _on_done(self):
        # todo update the selected rectangle coordinates
        self._on_cancel()

    def _on_reset(self):
        # todo: move back to initial rectangle dimensions and location
        #  and stay in edit state
        pass

    def update(self):
        self._options.entryconfig("Reset", state="disabled")

class Initial(object):
    def __init__(self, manager):
        self._manager = manager

        self._options = m = tk.Menu(self._manager.canvas)

        self._rectangle = None

        m.add_command(label="Edit", command=self._on_edit)
        m.add_command(label="Clone", command=self._on_clone)
        m.add_command(label="Delete", command=self._on_delete)
        m.add_separator()
        m.add_command(label="Draw", command=self._on_draw)

        m.entryconfig("Delete", state="disabled")
        m.entryconfig("Clone", state="disabled")
        m.entryconfig("Edit", state="disabled")

    def on_right_click(self, event):
        #todo:
        # when we clone a rectangle, we also clone its components.
        # components positions can be updated
        res = self._manager.select_rectangle(event.x, event.y)
        options = self._options

        if res:
            options.entryconfig("Clone", state="normal")
            options.entryconfig("Edit", state="normal")
            options.entryconfig("Delete", state="normal")

        self._manager.canvas.create_window(event.x, event.y, options)

    def _on_draw(self):
        self._manager.state = self._manager.drawing

    def _on_edit(self):
        self._manager.state = self._manager.editing

    def _on_clone(self):
        self._manager.state = self._manager.clone

    def _on_delete(self):
        self._manager.remove_rectangle()

    def update(self):
        # self._manager.canvas.bind("Button-1")
        options = self._options
        options.entryconfig("Delete", state="disabled")
        options.entryconfig("Clone", state="disabled")
        options.entryconfig("Edit", state="disabled")

class MappingTool(object):
    # area capture state (use for capturing positional rectangle)
    def __init__(self, container, rectangles):
        """

        Parameters
        ----------
        container
        rectangles: models.rectangles.Rectangles
        """
        self._img = None
        self._container = container
        self.rectangles = rectangles
        self._img_item = None
        self.canvas = None
        self._root = None
        self._position = [0, 0]
        self._height = 0
        self._width = 0
        self._aborted = False

        self.editing = Editing(self)
        self.cloning = Cloning(self)
        self.drawing = Drawing(self)
        self.initial = Initial(self)

        self._state = self.initial
        self.previous_state = None

        self.menu = None

        self._rectangles = {}

        self.rectangle = None
        self._rid = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        value.update()

    @property
    def position(self):
        return tuple(self._position)

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    def select_rectangle(self, x, y):
        #returns the smallest rectangle that encloses a point
        res = self._canvas.find_closest(x, y)

        found = None
        id_ = None

        if res:
            p = 0
            for r in res:
                id_, rect = self.get_rectangle(r)
                x0, y0, x1, y1 = rect.coordinates
                if x0 < x and y0 < y and x1 > x and y1 > y:
                    per = rect.perimeter
                    if per <= p:
                        p = per
                        found = rect

        self.rectangle = found
        self._rid = id_

        return found

    def add_rectangle(self, id_, bbox):
        self._rectangles[id_] = (id_, self.rectangles.add_rectangle(bbox))

    def update_rectangle(self, rectangle, coordinates):
        pass

    def get_rectangle(self, id_):
        return self._rectangles[id_]

    def start(self, image):
        self.rectangles.load()
        # todo: need absolute coordinates of the main window...

        # todo: re-draw previously created rectangles on the canvas
        # todo: highlight un-labeled rectangles

        self._root = root = tk.Toplevel(self._container)
        # root = self._manager._main_frame
        self._canvas = canv = tk.Canvas(root, width=500, height=500)
        root.resizable(False, False)
        # canv.create_rectangle(50, 50, 250, 150, fill='red')
        canv.pack(fill=tk.BOTH, expand=tk.YES)
        root.update()
        print("ABS", root.winfo_rootx(), root.winfo_rooty())

        root.bind("<Configure>", self._on_drag)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        canv.bind("<Button-1", self._on_left_click)
        canv.bind("<Button-3>", self._on_right_click)

        self._img_item = canv.create_image(0, 0, image=image, anchor=tk.NW)
        canv.config(width=image.width(), height=image.height())

        # command
        def onDrag(start, end):
            # global x, y
            # items = rect.hit_test(start, end)
            # for x in rect.items:
            #     if x not in items:
            #         canv.itemconfig(x, fill='grey')
            #     else:
            #         canv.itemconfig(x, fill='blue')
            pass

    def stop(self):
        self._aborted = True

    def remove_rectangle(self):
        # todo: two deletes: instance or all instances
        if self._rid:
            self.canvas.delete(self._rid)
            self.rectangles.delete(self.rectangle.id)

    def unselect_rectangle(self):
        self._rid = None
        self.rectangle = None

    def _on_left_click(self, event):
        if self.menu:
            self._canvas.delete(self.menu)

    def _on_right_click(self, event):
        if self.menu:
            self._canvas.delete(self.menu)
        self._state.on_right_click(event)

    def _on_close(self):
        self._root.destroy()
        self._root = None
        self._canvas = None
        #submit all added rectangles
        if not self._aborted:
            #todo: check if all rectangles have been label
            # note: we can resume a mapping session from where we left off
            self.rectangles.submit()
        self.rectangles.clear()

    def _on_drag(self, event):
        self._position[0] = self._root.winfo_rootx()
        self._position[1] = self._root.winfo_rooty()
        self._width = self._root.winfo_width()
        self._height = self._root.winfo_height()

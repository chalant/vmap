import tkinter as tk

from PIL import ImageTk

class RectSelected(object):
    # when a rectangle is selected, we can modify its dimensions, or drag it
    # when changing its dimensions, the all instances of the base triangle are
    # updated and redrawn. Also, all instances of the base are highlighted as-well.

    # if we click outside a rectangle, we move back to drawing state
    pass

class RectDrawer(object):
    def __init__(self, rectangles):
        self._rectangles = rectangles
        self.item = None
        self._entry = None

    def _draw(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(start + end), **opts)

    def start(self, canvas, **opts):
        self.canvas = canvas
        self.start = None
        self.canvas.bind("<Button-1>", self._update, '+')
        self.canvas.bind("<B1-Motion>", self._update, '+')
        self.canvas.bind("<ButtonRelease-1>", self._stop, '+')

        self._command = opts.pop('command', lambda *args: None)
        self.rectopts = opts

    def stop(self, canvas):
        canvas.unbind("<Button-1>")
        canvas.unbind("<B1-Motion>")
        canvas.unbind("<ButtonRelease-1>")

    def _update(self, event):

        if not self.start:
            self.start = (event.x, event.y)
            return
        # if self.item is not None:
        #     self.canvas.delete(self.item)
        # todo: keep a dictionary of items (requests)
        self.item = self._draw(self.start, (event.x, event.y), **self.rectopts)
        self._command(self.start, (event.x, event.y))

    def _stop(self, event):
        self.start = None
        # self.canvas.delete(self.item)
        #todo: add rectangle to requests collection, specifying coordinates
        # and item_id
        coords = self.canvas.coords(self.item)
        clicked = tk.StringVar()
        # todo: add other option buttons to the rectangle, like add child etc.
        # todo: add drag capabilities
        self._rectangles.add_rectangle(self.item, tuple(map(int, coords)))
        self._entry = e1 = tk.OptionMenu(self.canvas, clicked, *self._rectangles.get_label_types())
        # e1.pack()
        w = self.canvas.create_window(coords[0], coords[1], window=e1)
        #todo: place window such that it is within the canvas
        #todo: need a place for grabbing the rectangle so that we can drag the rectangle
        print("Bounds", self.canvas.bbox(self.item))

class Editing(object):
    def __init__(self, manager):
        self._manager = manager

        self._options = m = tk.Menu(self._manager.canvas)
        m.add_command(label="Done", command=self._on_done)

    def on_right_click(self, event):
        self._manager.canvas.create_window(event.x, event.y, self._options)

    def _on_done(self):
        self._manager.state = self._manager.initial

    def update(self):
        pass

class Drawing(object):
    def __init__(self, manager):
        self._drawer = RectDrawer(manager.rectangles)
        self._manager = manager

        self._options = m = tk.Menu(self._manager.canvas)
        m.add_command(label="Done", command=self._on_done)

    def on_right_click(self, event):
        self._manager.canvas.create_window(event.x, event.y, self._options)

    def _on_done(self):
        canv = self._manager.canvas

        canv.unbind('<Motion>')
        self._drawer.stop(canv)
        self._manager.state = self._manager.initial

    def update(self):
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

class Initial(object):
    def __init__(self, manager):
        self._manager = manager

        self._options = m = tk.Menu(self._manager.canvas)

        m.add_command(label="Draw", command=self._on_draw)
        m.add_command(label="Edit", command=self._on_edit)

    def on_right_click(self, event):
        self._manager.canvas.create_window(event.x, event.y, self._options)

    def _on_draw(self):
        self._manager.state = self._manager.drawing

    def _on_edit(self):
        self._manager.state = self._manager.editing

    def update(self):
        pass

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

        self.modifying = Editing(self)
        self.drawing = Drawing(self)
        self.initial = Initial(self)

        self._state = self.initial

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

    def start(self, image):
        # todo: need absolute coordinates of the main window...
        self._root = root = tk.Toplevel(self._container)
        # root = self._manager.main_frame
        self._canvas = canv = tk.Canvas(root, width=500, height=500)
        root.resizable(False, False)
        # canv.create_rectangle(50, 50, 250, 150, fill='red')
        canv.pack(fill=tk.BOTH, expand=tk.YES)
        root.update()
        print("ABS", root.winfo_rootx(), root.winfo_rooty())

        root.bind("<Configure>", self._on_drag)
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        # # draw some base requests
        # rect.draw([50, 50], [250, 150], fill='red', tags=('red', 'box'))
        # rect.draw([300, 300], [400, 450], fill='green', tags=('gre', 'box'))

        # put gif image on canvas
        # pic's upper left corner (NW) on the canvas is at x=50 y=10
        # img = ImageTk.PhotoImage(image)
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

    def _on_close(self):
        self._root.destroy()
        self._root = None
        self._canvas = None
        #submit all added rectangles
        if not self._aborted:
            self.rectangles.submit()

    def _on_drag(self, event):
        self._position[0] = self._root.winfo_rootx()
        self._position[1] = self._root.winfo_rooty()
        self._width = self._root.winfo_width()
        self._height = self._root.winfo_height()

import tkinter as tk

from PIL import ImageTk

from controllers import controller

class RectTracker:
    def __init__(self, rectangles):
        self._rectangles = rectangles
        self.item = None
        self._entry = None

    def draw(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(start + end), **opts)

    def autodraw(self, canvas, **opts):
        """Setup automatic drawing; supports command option"""
        self.canvas = canvas
        self.start = None
        self.canvas.bind("<Button-1>", self._update, '+')
        self.canvas.bind("<B1-Motion>", self._update, '+')
        self.canvas.bind("<ButtonRelease-1>", self._stop, '+')

        self._command = opts.pop('command', lambda *args: None)
        self.rectopts = opts

    def _update(self, event):

        if not self.start:
            self.start = (event.x, event.y)
            return
        if self.item is not None:
            self.canvas.delete(self.item)
        # todo: keep a dictionary of items (rectangles)
        self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
        self._command(self.start, (event.x, event.y))

    def _stop(self, event):
        self.start = None
        # self.canvas.delete(self.item)
        #todo: add rectangle to rectangles collection, specifying coordinates
        # and item_id
        coords = self.canvas.coords(self.item)
        print("Coords", coords)
        clicked = tk.StringVar()
        # todo: retrieve label types from rectangles class, and populate option menu
        # todo: add other option buttons to the rectangle, like add child etc.
        self._rectangles.add_rectangle(self.item, coords)
        self._entry = e1 = tk.OptionMenu(self.canvas, clicked, *self._rectangles.get_label_types())
        # e1.pack()
        w = self.canvas.create_window(coords[0], coords[1], window=e1)
        print("Bounds", self.canvas.bbox(w))

class MappingTool(controller.Controller):
    # area capture state (use for capturing positional data)
    def __init__(self, id_, container, rectangles):
        """

        Parameters
        ----------
        container
        rectangles: models.rectangles.Rectangles
        """
        super(MappingTool, self).__init__(id_)
        self._img = None
        self._container = container
        self._rectangles = rectangles
        self._img_item = None
        self._canvas = None
        self._root = None

        self._tracker = RectTracker(rectangles)

    def start(self, image):
        self._root = root = tk.Toplevel(self._container)
        # root = self._manager.main_frame
        self._canvas = canv = tk.Canvas(root, width=500, height=500)
        root.resizable(False, False)
        # canv.create_rectangle(50, 50, 250, 150, fill='red')
        canv.pack(fill=tk.BOTH, expand=tk.YES)
        root.update()
        print("ABS", root.winfo_rootx(), root.winfo_rooty())

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        rect = self._tracker
        # # draw some base rectangles
        # rect.draw([50, 50], [250, 150], fill='red', tags=('red', 'box'))
        # rect.draw([300, 300], [400, 450], fill='green', tags=('gre', 'box'))

        # put gif image on canvas
        # pic's upper left corner (NW) on the canvas is at x=50 y=10
        img = ImageTk.PhotoImage(image)
        self._img_item = canv.create_image(0, 0, image=img, anchor=tk.NW)
        canv.config(width=img.width(), height=img.height())

        # just for fun
        x, y = None, None

        def cool_design(event):
            kill_xy()

            dashes = [3, 2]
            x = canv.create_line(event.x, 0, event.x, 1000, dash=dashes, tags='no')
            y = canv.create_line(0, event.y, 1000, event.y, dash=dashes, tags='no')

        def kill_xy(event=None):
            canv.delete('no')

        canv.bind('<Motion>', cool_design, '+')

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

        rect.autodraw(canv, fill="", width=1, command=onDrag)

    def _on_close(self):
        self._root.destroy()
        self._root = None
        self._canvas = None

    def handle_data(self, data, emitter):
        if self._canvas:
            if self._img_item:
                self._canvas.delete(self._img_item)
            self._img_item = self._canvas.create_image(0, 0, tk.PhotoImage(data), anchor=tk.NW)
import tkinter as tk

class RectDrawer(object):
    def __init__(self, manager, rectangles, collision):
        self._rectangles = rectangles
        self.item = None
        self._entry = None

        self._btn1_id = None
        self._mtn_id = None
        self._rel_id = None

        self._start = None

        self._manager = manager
        self._mapper = None

        self._container = None
        self._cid = None

        self._prev = None

        self._rid = None
        self._rct = None
        self._line = None
        self._point = None

        self._lines = []
        self._points = []

        self._nry = 0
        self._nrx = 0

        self._collision = collision

    def _draw(self, start, end, container, **opts):
        """Draw the rectangle"""
        x0, y0 = start
        x1, y1 = end

        collision = self._collision

        if container:
            cx0, cy0, cx1, cy1 = container.bbox
            # if cx0 < x1 and cy0 < y1 and cx1 > x1 and cy1 > y1:
            #     pass
            # else:
            # cx1 - x1
            if x1 < cx0:
                x1 += (cx0 - x1) + 2
            if x1 > cx1:
                x1 -= (x1 - cx1) + 2
            if y1 > cy1:
                y1 -= (y1 - cy1) + 2
            if y1 < cy0:
                y1 += (cy0 - y1) + 2

        if not self._prev:
            self._prev = x0, y0

        px, py = self._prev

        dx = x1 - px
        dy = y1 - py

        # get the closest rectangle that intersects with he line
        if self._line:
            self.canvas.delete(self._line)
        self._line = self.canvas.create_line(px, py, px + 25*dx, py + 25*dy, dash=(6,4))

        lines = self._lines
        points = self._points

        if lines:
            for l in lines:
                self.canvas.delete(l)
            lines.clear()

        if points:
            for p in points:
                self.canvas.delete(p)
            points.clear()


        for r in self._mapper.get_rectangles(container):
            rx0, ry0, rx1, ry1 = r.bbox

            t, nrx, nry = collision.collision_info(px, py, dx, dy, r.bbox)
                # print(nx, "NX", ny, "NY")
            col_ptx, col_pty = collision.collision_point(px, py, dx, dy, t)

            if nrx is None:
                nrx = self._nrx

            if nry is None:
                nry = self._nry

            if t <= 1:
                if collision.overlapping((x0, y0, x1, y1), r.bbox):
                    if nrx < 0:
                        x1 = rx0 - 2
                    elif nrx > 0:
                        x1 = rx1 + 2
                    elif nry < 0:
                        y1 = ry0 - 2
                    elif nry > 0:
                        y1 = ry1 + 2
                    elif nrx == 0 and nry == 0:
                        x1 = px
                        y1 = py
                    
                if collision.overlapping((x0, y0, x1, y1), r.bbox):
                    x1 = px
                    y1 = py

            points.append(self.canvas.create_oval(col_ptx - 3, col_pty - 3, col_ptx + 3, col_pty + 3, fill="blue"))
            lines.append(self.canvas.create_line(col_ptx, col_pty, col_ptx+nrx*15, col_pty + nry*15, fill="red"))

        self._prev = x1, y1

        return self.canvas.create_rectangle(x0, y0, x1, y1, **opts)

    def start(self, canvas, mapper, **opts):
        self._prev_col = None
        self.canvas = canvas
        self._start = None
        self._mapper = mapper

        self._btn1_id = canvas.bind("<Button-1>", self._update, '+')
        self._mtn_id =  canvas.bind("<B1-Motion>", self._update, '+')
        self._rel_id =  canvas.bind("<ButtonRelease-1>", self._stop, '+')

        self._command = opts.pop('command', lambda *args: None)
        self.rectopts = opts

    def stop(self, canvas):
        canvas.unbind("<Button-1>")
        canvas.unbind("<B1-Motion>")
        canvas.unbind("<ButtonRelease-1>")
        # self._menus.clear()

    def _update(self, event):
        if not self._start:
            self._cid = None
            self._container = None

            self._start = (event.x, event.y)
            self._prev = (event.x, event.y)

            #check if we're within a box
            rid = self._mapper.select_rectangle(event.x, event.y)
            if rid:
                self._container = self._mapper.get_rectangle(rid)
                self._cid = rid

        if self.item is not None:
            self.canvas.delete(self.item)

        self.item = self._draw(
            self._start,
            (event.x, event.y),
            self._container,
            **self.rectopts)

        self._command(self.start, (event.x, event.y))

    def _stop(self, event):
        self._start = None

        coords = self.canvas.coords(self.item)

        #selected label
        self.canvas.delete(self.item)
        rid = self._manager.add_rectangle(tuple(map(int, coords)))

        if self._cid:
            # add component if the rectangle is in the container
            self._mapper.add_component(self._cid, rid)

        self.item = None
        self._prev_col = None

        self.canvas.delete(self._line)

        for l in self._lines:
            self.canvas.delete(l)

        for p in self._points:
            self.canvas.delete(p)

        self._lines.clear()
        self._points.clear()

class Drawing(object):
    def __init__(self, manager, collision):
        """

        Parameters
        ----------
        manager: controllers.tools.mapping.MappingTool
        """
        self._drawer = RectDrawer(self, manager.rectangles, collision)
        self._manager = manager

        self._options = menu = tk.Menu(self._manager.canvas, tearoff=False)

        self._rectangles = []

        menu.add_command(label="Delete", command=self._on_delete)
        menu.add_separator()
        menu.add_command(label="Cancel", command=self._on_cancel)
        menu.add_command(label="Done", command=self._on_done)

        menu.entryconfig("Delete", state="disabled")

        self._rid = None

    def on_right_click(self, event):
        res = self._manager.select_rectangle(event.x, event.y)
        opt = self._options

        if res:
            opt.entryconfig("Delete", state="normal")
        else:
            opt.entryconfig("Delete", state="disabled")

        self._rid = res

        opt.tk_popup(event.x_root, event.y_root)

    def _on_delete(self):
        self._manager.remove_rectangle(self._rid)

    def _on_done(self):
        cnv = self._manager.canvas
        cnv.unbind('<Motion>')

        self._drawer.stop(cnv)
        self._manager.canvas.delete('no')
        self._manager.state = self._manager.initial
        self._rectangles.clear()

    def _on_cancel(self):
        for rid in self._rectangles:
            self._manager.remove_rectangle(rid)

        self._on_done()

    def add_rectangle(self, bbox):
        rid = self._manager.add_rectangle(bbox)
        self._rectangles.append(rid)
        return rid

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

        self._drawer.start(canv, self._manager, fill="", width=1)
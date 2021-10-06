import tkinter as tk

from gscrap.rectangles import rectangles


class Editing(object):
    # todo: should be able to resize the cz
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.tools.mapping.MappingTool
        """
        self._mapper = manager

        self._root = None

        self._options = m = tk.Menu(self._mapper.canvas, tearoff=False)

        m.add_command(label="Cancel", command=self._on_cancel)
        m.add_command(label="Done", command=self._on_done)

        self._item = None
        self._clicked = None

        self._container = None

        self._prev_rect = None

        self._prev_pos = None

        self._container = None
        self._rectangle = None

        self._nrx = 0
        self._nry = 0

        self._lc = False
        self._cursor_pos = None

        self._rid = None
        self._text = None

    def on_right_click(self, event):
        self._options.tk_popup(event.x_root, event.y_root)

    def _unbind(self):
        prev = self._rid

        if prev:
            canvas = self._mapper.canvas

            canvas.unbind("<Button-1>")
            canvas.unbind("<B1-Motion>")
            canvas.unbind("<ButtonRelease-1>")

            canvas["cursor"] = "arrow"
            canvas.itemconfigure(prev, outline="black")

            self._rid = None

    def on_motion(self, event):
        canvas = self._mapper.canvas
        res = self._mapper.select_rectangle(event.x, event.y)

        if res:
            if res != self._rid:
                self._unbind()

            self._rid = res

            canvas.bind("<Button-1>", self._on_click, "+")
            canvas.bind("<B1-Motion>", self._on_drag, "+")
            canvas.bind("<ButtonRelease-1>", self._on_release, "+")

            canvas["cursor"] = "hand2"

            canvas.itemconfigure(res, outline="red")

            # rct = self._mapper.get_rectangle(res)

            # if self._text:
            #     canvas.delete(self._text)

            # x0, y0, x1, y1 = rct.bbox
            #
            # x, y = round((x1 + x0) / 2), y0

            #todo: we need to display all the label names

            # self._text = canvas.create_text(x, y, text=rct.label_name)

        else:
            self._unbind()

    def _on_cancel(self):
        pass

    def _on_done(self):
        self._unbind()
        self._on_cancel()
        self._mapper.state = self._mapper.initial

        if self._text:
            self._mapper.canvas.delete(self._text)

    def _on_click(self, event):
        if not self._lc:
            rid = self._rid
            rct = self._mapper.get_rectangle(rid)
            self._container = self._mapper.get_rectangle(rct.container)
            self._rectangle = rct
            self._prev_pos = rct.center
            self._cursor_pos = event.x, event.y
            self._lc = True

            # for rct in mapping_utils.tree_iterator(self._mapper, rid):
            #     x, y = rct.bbox[0], rct.bbox[1]
            #     self._mapper.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill = "blue")

    def _update_draw(self, r, dx, dy):
        x0, y0, x1, y1 = r.bbox

        self._mapper.move(r.rid, dx, dy)

        bbox = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)

        r.bbox = bbox

    def _on_drag(self, event):

        if self._text:
            self._mapper.canvas.delete(self._text)

        px, py = self._prev_pos
        cx, cy = self._cursor_pos
        rid = self._rid

        x = event.x
        y = event.y

        dx = x - cx
        dy = y - cy

        mx = dx
        my = dy

        if mx != 0 or my != 0:
            container = self._container
            # collision = self._collision
            # controller = self._mapper

            # self._view.clear()
            # self._view.ray(px, py, mx, my)

            x0, y0, x1, y1 = self._rectangle.bbox

            # w = self._cz.width/2
            # h = self._cz.height/2

            fx0 = x0 + mx
            fy0 = y0 + my
            fx1 = x1 + mx
            fy1 = y1 + my

            if container:
                cx0, cy0, cx1, cy1 = container.bbox

                if cx0 >= fx0:
                    mx = cx0 - x0 + 2
                elif fx1 >= cx1:
                    mx = cx1 - x1 - 2

                if cy0 >= fy0:
                    my = cy0 - y0 + 2
                elif cy1 <= fy1:
                    my = cy1 - y1 - 2

            else:
                wd = self._mapper.width
                hg = self._mapper.height

                if 0 >= fx0:
                    mx = 2 - x0
                elif fx1 >= wd:
                    mx = wd - x1 - 2

                if 0 >= fy0:
                    my = 2 - y0
                elif hg <= fy1:
                    my = hg - y1 - 2
        #
        #         for r in controller.get_rectangles(container):
        #             if r.rid != rid:
        #                 rx0, ry0, rx1, ry1 = r.bbox
        #
        #                 col, t, nrx, nry = collision.collision_info(
        #                     px, py, mx, my,
        #                     (rx0 - w, ry0 - h, rx1 + w, ry1 + h))
        #
        #                 # col_ptx, col_pty = cl.collision_point(px, py, mx, my, t)
        #
        #                 if nrx is None:
        #                     nrx = self._nrx
        #
        #                 if nry is None:
        #                     nry = self._nry
        #
        #                 # self._view.point(col_ptx, col_pty)
        #                 # self._view.normal(col_ptx, col_pty, nrx, nry)
        #
        #                 if col:
        #                     if nrx < 0:
        #                         if fx1 >= rx0:
        #                             mx = (rx0 - 2) - x1
        #                     elif nrx > 0:
        #                         if fx0 <= rx1:
        #                             mx = (rx1 + 2) - x0
        #                     elif nry < 0:
        #                         if fy1 >= ry0:
        #                             my = (ry0 - 2) - y1
        #                     elif nry > 0:
        #                         if fy0 <= ry1:
        #                             my = (ry1 + 2) - y0

        for rct in rectangles.tree_iterator(self._mapper.instances, rid):
            self._update_draw(rct, mx, my)

            # x, y = rct.bbox[0], rct.bbox[1]
            # self._mapper.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill = "blue")

        self._prev_pos = px + mx, py + my
        self._cursor_pos = x, y

    def _on_release(self, event):
        self._lc = False
        self._container = None
        self._rectangle = None

    def update(self):
        # self._options.entryconfig("Reset", state="disabled")
        pass
import tkinter as tk

from controllers.tools import mapping_utils
from controllers.tools import collision as cl

class Cloning(object):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: controllers.tools.mapping.MappingTool
        """
        self._mapper = manager

        self._options = m = tk.Menu(self._mapper.canvas, tearoff=False)

        m.add_command(label="Paste", command=self._on_paste)
        m.add_command(label="Delete", command=self._on_delete)
        m.add_separator()
        m.add_command(label="Cancel", command=self._on_cancel)
        m.add_command(label="Done", command=self._on_done)

        self._rectangles = []

        self._item = None
        self._clicked = None

        self._container = None

        self._prev_rect = None

        self._prev_pos = None

        self._instances = []
        self._collision = cl.BoxCollision()

        self._container = None
        self._rectangle = None

        self._nrx = 0
        self._nry = 0

        self._view = cl.CollisionView(self._mapper)
        self._lc = False
        self._cursor_pos = None

        self._rid = None

    def on_right_click(self, event):
        options = self._options
        options.tk_popup(event.x_root, event.y_root)

        self._clicked = (event.x, event.y)

    def update(self):
        pass

    def _on_delete(self):
        pass

    def _on_cancel(self):
        for rid in self._rectangles:
            self._mapper.remove_rectangle(rid)
        self._rectangles.clear()

    def _draw_copy(self, dx, dy, rct):
        a, b = rct.top_left

        return self._mapper.add_instance(rct.rid, a + dx, b + dy)

    def _copy(self, rectangle, x, y):
        rectangles = self._rectangles

        rct = self._mapper.get_rectangle(rectangle)
        x1, y1 = rct.top_left

        x, y = self._mapper.adjust_point(
            round(x - rct.width / 2),
            round(y - rct.height / 2),
            rct.width,
            rct.height)

        dx, dy = x - x1, y - y1

        stack = [rectangle]
        ls = 1

        instances = self._instances
        container = rct.container

        while ls != 0:
            rct = self._mapper.get_rectangle(stack[-1])
            try:
                stack.append(next(rct))
                ls += 1
            except StopIteration:
                rid = self._draw_copy(dx, dy, rct)

                rectangles.append(rid)

                stack.pop()

                for _ in range(len(rct.components)):
                    self._mapper.add_component(rid, instances.pop())

                instances.append(rid)
                ls -= 1

                if ls == 0 and container:
                    self._mapper.add_component(container, rid)


    def _on_done(self):
        self._rectangles.clear()
        self._mapper.state = self._mapper.initial

    def _on_paste(self):
        #draw all components of the container
        rct = self._mapper.selected_rectangle
        container = self._mapper.get_root_container(rct)

        self._container = container
        self._rid = rct

        x, y = self._clicked

        #copy the rectangle and draw it
        self._copy(rct, x, y)

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

        if res and res != self._mapper.cloned:
            if res != self._rid:
                self._unbind()

            self._rid = res

            canvas.bind("<Button-1>", self._on_click, "+")
            canvas.bind("<B1-Motion>", self._on_drag, "+")
            canvas.bind("<ButtonRelease-1>", self._on_release, "+")

            canvas["cursor"] = "hand2"

            canvas.itemconfigure(res, outline="red")

        else:
            self._unbind()


    def _on_click(self, event):
        if not self._lc:
            rid = self._rid
            rct = self._mapper.get_rectangle(rid)
            self._container = self._mapper.get_rectangle(rct.container)
            self._rectangle = rct
            self._prev_pos = rct.center
            self._cursor_pos = event.x, event.y
            self._lc = True

    def _update_draw(self, r, dx, dy):
        x0, y0, x1, y1 = r.bbox

        self._mapper.move(r.rid, dx, dy)

        bbox = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)

        r.bbox = bbox

    def _on_drag(self, event):
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
            # mapper = self._mapper

            # self._view.clear()
            # self._view.ray(px, py, mx, my)

            x0, y0, x1, y1 = self._rectangle.bbox

            # w = self._rectangle.width/2
            # h = self._rectangle.height/2

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
        #         for r in mapper.get_rectangles(container):
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

        for rct in mapping_utils.tree_iterator(self._mapper, rid):
            self._update_draw(rct, mx, my)

        self._prev_pos = px + mx, py + my
        self._cursor_pos = x, y

    def _on_release(self, event):
        self._lc = False
        self._container = None
        self._rectangle = None
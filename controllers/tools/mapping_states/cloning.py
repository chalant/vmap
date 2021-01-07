import tkinter as tk

from controllers.tools import mapping_utils

class Cloning(object):
    def __init__(self, manager, collision):
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

    def on_right_click(self, event):
        options = self._options
        options.tk_popup(event.x_root, event.y_root)

        self._clicked = (event.x, event.y)

        #todo: activate dragging => create center nodes with tag "drag" and bind them to motion
        # and left click button events. Redraw rectangle on each motion if the left click button
        # is not released, also, the mouse pointer must be switched to pointing hand

    def update(self):
        pass

    def _on_delete(self):
        pass

    def _on_cancel(self):
        for rid in self._rectangles:
            self._mapper.remove_rectangle(rid)
        self._rectangles.clear()
        self._mapper.canvas.unbind("<Motion>")

    def _draw_copy(self, dx, dy, rct):
        a, b = rct.top_left

        return self._mapper.add_instance(rct.rid, a + dx, b + dy)

    def _copy(self, rectangle, x, y):
        rectangles = self._rectangles

        rct = self._mapper.get_rectangle(rectangle)
        x1, y1 = rct.top_left

        x, y = self._mapper.adjust_point(x - rct.width / 2, y - rct.height / 2, rct.width, rct.height)

        dx, dy = x - x1, y - y1

        stack = [rectangle]
        ls = len(stack)

        instances = []

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

    def _on_done(self):
        self._rectangles.clear()
        self._mapper.canvas.unbind("<Motion>")
        self._mapper.state = self._mapper.initial

    def _on_paste(self):
        canvas = self._mapper.canvas
        #draw all components of the container
        rct = self._mapper.selected_rectangle()
        container = self._mapper.get_root_container(rct)

        self._container = container
        self._rect = container

        x, y = self._clicked

        #copy the rectangle and draw it
        self._copy(container, x, y)

        canvas.bind("<Motion>", self._on_motion)


    def _unbind(self):
        prev = self._rect

        if prev:
            canvas = self._mapper.canvas

            canvas.unbind("<Button-1>")
            canvas.unbind("<B1-Motion>")
            canvas.unbind("<ButtonRelease-1>")

            canvas["cursor"] = "arrow"
            canvas.itemconfigure(prev, outline="black")

    def _on_motion(self, event):
        canvas = self._mapper.canvas
        res = self._mapper.select_rectangle(event.x, event.y)

        if res and res != self._mapper.cloned:
            if res != self._rect:
                self._unbind()

            self._rect = res

            canvas.bind("<Button-1>", self._on_click, "+")
            canvas.bind("<B1-Motion>", self._on_drag, "+")
            canvas.bind("<ButtonRelease-1>", self._on_release, "+")

            canvas["cursor"] = "hand2"

            canvas.itemconfigure(res, outline="red")

        else:
            self._unbind()


    def _on_click(self, event):
        self._prev_pos = (event.x, event.y)

    def _update_draw(self, r, dx, dy, container):
        x0, y0, x1, y1 = r.bbox

        x0 = x0 + dx
        y0 = y0 + dy
        x1 = x1 + dx
        y1 = y1 + dy

        bbox = (x0, y0, x1, y1)

        if container:
            cx0, cy0, cx1, cy1 = self._mapper.get_rectangle(container).bbox

        #only draw within the container
            # if cx0 < x0 and cx1 > x1 and cy0 < y0 and cy1 > y1:
            #     # return self._mapper.update_rectangle(r.rid, bbox), bbox
            self._mapper.move(r.rid, dx, dy)

            # return r.rid, r.bbox
        else:
            self._mapper.move(r.rid, dx, dy)

        r.bbox = bbox
        r.top_left = x0, y0
        # self._mapper.update_rectangle(r.rid, bbox)
        # return self._mapper.update_rectangle(r.rid , bbox), bbox

    def _on_drag(self, event):
        px, py = self._prev_pos
        rect = self._rect

        dx = event.x - px
        dy = event.y - py

        container = self._mapper.get_rectangle(rect).container

        #todo: implement collision

        for rct in mapping_utils.tree_iterator(self._mapper, rect):
            self._update_draw(rct, dx, dy, container)

        self._prev_pos = (event.x, event.y)

    def _on_release(self, event):
        pass
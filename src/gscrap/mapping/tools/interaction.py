from gscrap.rectangles import rectangles as rt

class Interaction(object):
    def __init__(self, canvas, width, height):

        self._canvas = canvas
        self.width = width
        self.height = height
        self._instances = {}

        def null_callback(rid):
            pass

        self._left_click_callback = null_callback
        self._rid = None

        self._instances_base_color = None


    def start(self, instances):

        canvas = self._canvas

        self._instances = instances

        canvas.bind("<Motion>", self._on_motion)
        canvas.bind("<Button-1>", self._on_left_click)

    def set_base_outline(self, instance):
        outline = "blue"

        instance.base_outline = outline

        if self._rid:
            if instance.rid != self._rid:
                self._canvas.itemconfigure(instance.rid, outline=outline)
        else:
            self._canvas.itemconfigure(instance.rid, outline=outline)

    def reset_base_outline(self, instance):
        instance.base_outline = "black"

        self._canvas.itemconfigure(instance.rid, outline="black")

    def unbind(self):
        canvas = self._canvas

        self._unbind(self._instances, canvas)

        canvas.unbind("<Motion>")
        canvas.unbind("<Button-1>")

    def on_left_click(self, callback):
        self._left_click_callback = callback

    def _on_left_click(self, event):
        rid = self._rid

        if rid:
            self._left_click_callback(rt.get_rectangle(self._instances, rid))

    def _on_motion(self, event):
        self.highlight_outline(self._instances, event)

    def highlight_outline(self, instances, mouse_event):

        canvas = self._canvas

        x = mouse_event.x + canvas.xview()[0] * self.width
        y = mouse_event.y + canvas.yview()[0] * self.height

        res = rt.find_closest_enclosing(instances, x, y)

        if res:
            rid = res[0]

            if rid != self._rid:
                self._unbind(instances, canvas)
            # rct = rt.get_rectangle(instances, rid)
            # print(rid)
            canvas.itemconfigure(rid, outline="red")

            self._rid = rid
            return rid

        else:
            self._unbind(instances, canvas)
            return

    def _unbind(self, instances, canvas):
        prev = self._rid

        if prev:
            canvas.itemconfigure(prev, outline=instances[prev].base_outline)

            self._rid = None
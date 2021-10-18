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
        self._prev = None

    def start(self, instances):
        canvas = self._canvas

        self._instances = instances

        canvas.bind("<Motion>", self._on_motion)
        canvas.bind("<Button-1>", self._on_left_click)

    def unbind(self):
        canvas = self._canvas

        canvas.unbind("<Motion>")
        canvas.unbind("<Button-1>")

    def on_left_click(self, callback):
        self._left_click_callback = callback

    def _on_left_click(self, event):
        rid = self._rid

        if rid:
            self._left_click_callback(rt.get_rectangle(self._instances, rid))

    def _on_motion(self, event):
        canvas = self._canvas

        x = event.x + canvas.xview()[0] * self.width
        y = event.y + canvas.yview()[0] * self.height

        instances = self._instances

        res = rt.find_closest_enclosing(instances, x, y)

        if res:
            rid = res[0]
            if res != self._prev:
                self._unbind(canvas)

            rct = rt.get_rectangle(instances, rid)
            canvas.itemconfigure(rct.id, outline="red")
            self._prev = rct.id
            self._rid = rid
        else:
            self._unbind(canvas)
            self._rid = None

    def _unbind(self, canvas):
        prev = self._prev

        if prev:
            canvas.itemconfigure(prev, outline="black")
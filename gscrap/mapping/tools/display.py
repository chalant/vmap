from abc import ABC

class DisplayItem(ABC):
    def __init__(self, id_, rectangle_instance):
        """

        Parameters
        ----------
        id_
        rectangle_instance:gscrap.data.rectangles.rectangles.RectangleInstance
        """

        self.rid = id_
        self.rectangle_instance = rectangle_instance

    @property
    def bbox(self):
        return self.rectangle_instance.bbox

    @property
    def top_left(self):
        return self.rectangle_instance.top_left

class RectangleDisplay(object):
    def __init__(self, canvas):
        self._items = []
        self._canvas = canvas

    def draw(self, item, instance_factory):
        canvas = self._canvas

        x0, y0, x1, y1 = item.bbox

        rid = canvas.create_rectangle(
            x0, y0,
            x1, y1,
            width=1,
            dash=(4, 1))

        return instance_factory.create_instance(rid, item)

    def delete(self, item):
        self._canvas.delete(item)

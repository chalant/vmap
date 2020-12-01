from uuid import uuid4

from sqlalchemy import text

from models import models

_SELECT_LABELS_OF_TYPE = text(
    """
    SELECT *
    FROM labels
    WHERE label_type =:label_type
    """
)

_SELECT_LABEL_TYPES = text(
    """
    SELECT *
    FROM label_types
    """
)

_SELECT_RECTANGLES = text(
    """
    SELECT *
    FROM requests
    """
)

#todo
_ADD_LABEL = text(
    """
    INSERT
    """
)

class Rectangle(object):
    def __init__(self, coordinates, id_, canvas_id=None):
        self._coordinates = coordinates
        self._canvas_id = canvas_id
        self._id = id_
        x1, y1, x2, y2 = coordinates
        self._center = ((x1 + x2)/2, y2), (x1, (y1 + y2)/2)

    @property
    def id(self):
        return self._id

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @property
    def canvas_id(self):
        return self._canvas_id

    @canvas_id.setter
    def canvas_id(self, value):
        self._canvas_id = value

    @property
    def center(self):
        return self._center

    def set_label_instance(self, instance):
        pass

    def submit(self, connection):
        pass

class Rectangles(models.Model):
    def __init__(self):
        super(Rectangles, self).__init__()
        # self._engine = engine
        self._updated = False
        # todo: load requests from database
        self._rectangles = []
        self._new_rectangles = {}
        self._updated_rectangles = {}

    def add_rectangle(self, canvas_id, coordinates):
        rect = Rectangle(coordinates, uuid4().hex, canvas_id)
        self._new_rectangles[canvas_id] = rect
        self._rectangles.append(rect)
        self._updated = True
        return rect

    #we can change the position of a rectangle within the canvas
    def update_rectangle(self, canvas_id, coordinates):
        self._updated_rectangles[canvas_id].coordinates = coordinates
        self._updated = True

    def get_rectangle(self, x, y):
        # todo: return the rectangle that encloses the given point
        return

    def get_labels_of_type(self, label_type):
        pass

    def get_label_types(self):
        """returns a list of label types"""
        return ["Container", "Button", "Text Box"]

    def get_rectangles(self):
        return self._rectangles
        # todo: load rectangles from database
        # return self._rectangles.values()

    def new_rectangles(self):
        return self._new_rectangles.values()

    def submit(self):
        # todo: save new rectangles and updated rectangles
        # and notify the display

        if self._updated == True:
            evt = "update"
            for obs in self.get_observers(evt):
                obs.update(evt, self)
        self._new_rectangles.clear()

    def _events(self):
        return ["new", "load", "write", "update"]
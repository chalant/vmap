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
    FROM rectangles
    """
)

#todo
_ADD_LABEL = text(
    """
    INSERT
    """
)

class Rectangle(object):
    def __init__(self, coordinates, canvas_id=None):
        self._coordinates = coordinates
        self._canvas_id = canvas_id
        x1, y1, x2, y2 = coordinates
        self._center = ((x1 + x2)/2, y2), (x1, (y1 + y2)/2)

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def canvas_id(self):
        return self._canvas_id

    @canvas_id.setter
    def canvas_id(self, value):
        self._canvas_id = value

    @property
    def center(self):
        return self._center

    def add_label(self, label_name, label_type):
        pass

    def submit(self, connection):
        pass

class Rectangles(models.Model):
    def __init__(self):
        super(Rectangles, self).__init__()
        # todo: load rectangles from database
        self._rectangles = []
        # self._engine = engine

    def add_rectangle(self, canvas_id, coordinates):
        # todo: notify observers
        rect = Rectangle(coordinates, canvas_id)
        self._rectangles.append(rect)
        return rect

    def get_rectangle(self, x, y):
        # todo: return the rectangle that encloses the given point
        pass

    def get_labels_of_type(self, label_type):
        pass

    def get_label_types(self):
        """returns a list of label types"""
        return ["Container", "Button", "Text Box"]

    def get_rectangles(self):
        # todo: load rectangle
        return self._rectangles

    def submit(self):
        # todo: submit all rectangle instances to disk
        pass

    def _events(self):
        return ["new", "load", "write"]
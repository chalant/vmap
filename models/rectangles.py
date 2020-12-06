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
    FROM rectangles
    """
)

_ADD_RECTANGLE = text(
    """
    INSERT INTO rectangles(rectangle_id, height, width, project_name, label_id)
    VALUES (:rectangle_id, :height, :width, :project_name, :label_id)
    """
)

_ADD_RECTANGLE_INSTANCE = text(
    """
    INSERT INTO rectangles_instances(rectangle_id, left, top)
    VALUES (:rectangle_id, :left, :top)
    """
)

_GET_LABEL_TYPES = text(
    """
    SELECT *
    FROM label_types
    """
)

class RectangleInstance(object):
    def __init__(self, rectangle, left, top):
        """

        Parameters
        ----------
        rectangle: Rectangle
        left: Int
        top: Int
        """

        self._left = left
        self._top = top

        self._rectangle = rectangle

    @property
    def coordinates(self):
        x1 = self._left
        y1 = self._top
        r = self._rectangle
        return (x1, y1, x1 + r.width, y1 + r.height)

    @coordinates.setter
    def coordinates(self, value):
        self._left = value[0]
        self._top = value[1]

    def submit(self, connection):
        connection.execute(
            _ADD_RECTANGLE_INSTANCE,
            rectangle_id=self._rectangle.id,
            left=self._left,
            top=self._top)

class Rectangle(object):
    def __init__(self, coordinates, id_, label_id, canvas_id=None):
        self._coordinates = coordinates
        self._canvas_id = canvas_id
        self._id = id_
        self._project_name = "test"

        self._label_id = label_id

        x1, y1, x2, y2 = coordinates

        self._center = ((x1 + x2)/2, y2), (x1, (y1 + y2)/2)

        self._width = x2 - x1
        self._height = y2 - y1

        self._instances = []

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
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        for instance in self._instances:
            instance.width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        for instance in self._instances:
            instance.height = value

    @property
    def canvas_id(self):
        return self._canvas_id

    @canvas_id.setter
    def canvas_id(self, value):
        self._canvas_id = value

    @property
    def center(self):
        return self._center

    def add_instance(self, x, y):
        instance = RectangleInstance(self._id, x, y)
        self._instances.append(instance)
        return instance

    def submit(self, connection):
        connection.execute(
            _ADD_RECTANGLE,
            rectangle_id=self._id,
            height=self._height,
            width=self._width,
            project_name=self._project_name,
            label_id=self._label_id)

        for instance in self._instances:
            instance.submit(connection)

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

    def get_rectangle_by_label(self, label):
        pass

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
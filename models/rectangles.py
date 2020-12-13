from uuid import uuid4

from sqlalchemy import text

from models import models

from data import engine

_SELECT_RECTANGLES = text(
    """
    SELECT *
    FROM rectangles
    WHERE project_name=:project_name;
    """
)

_ADD_RECTANGLE = text(
    """
    INSERT INTO rectangles(rectangle_id, height, width, project_name, label_id)
    VALUES (:rectangle_id, :height, :width, :project_name, :label_id);
    """
)

_ADD_RECTANGLE_INSTANCE = text(
    """
    INSERT INTO rectangles_instances(rectangle_id, left, top)
    VALUES (:rectangle_id, :left, :top);
    """
)

class RectangleInstance(object):
    def __init__(self, id_, rectangle, left, top):
        """

        Parameters
        ----------
        rectangle: Rectangle
        left: Int
        top: Int
        """
        self._id = id_
        self._left = left
        self._top = top

        x1, y1, x2, y2 = self.coordinates

        self._center = ((x1 + x2) / 2, y2), (x1, (y1 + y2) / 2)

        self._rectangle = rectangle

    @property
    def label_id(self):
        return self._rectangle.label_id

    @label_id.setter
    def label_id(self, value):
        self._rectangle.label_id = value

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

    @property
    def width(self):
        return self._rectangle.width

    @property
    def height(self):
        return self._rectangle.height

    @property
    def center(self):
        return self._center

    @property
    def perimeter(self):
        return self._rectangle.perimeter

    @property
    def area(self):
        return self._rectangle.area

    @property
    def siblings(self):
        return self._rectangle.get_instances()

    def submit(self, connection):
        connection.execute(
            _ADD_RECTANGLE_INSTANCE,
            r_instance_id=self._id,
            rectangle_id=self._rectangle.id,
            left=self._left,
            top=self._top)

class Rectangle(object):
    def __init__(self, id_, project_name, height, width):
        self._id = id_
        self._project_name = project_name

        self._label_id = None

        self._width = height
        self._height = width

        self._instances = []

    @property
    def id(self):
        return self._id

    @property
    def label_id(self):
        return self._label_id

    @label_id.setter
    def label_id(self, value):
        for instance in self._instances:
            instance.label_id = value
        self._label_id = value

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

    def add_instance(self, x, y):
        instance = RectangleInstance(uuid4().hex, self, x, y)
        self._instances.append(instance)
        return instance

    def get_instances(self):
        pass

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

    @property
    def perimeter(self):
        return 2 * (self._width + self._height)

    @property
    def area(self):
        return (self._width * self._height)/2

class Rectangles(models.Model):
    def __init__(self):

        super(Rectangles, self).__init__()
        # self._engine = engine
        self._updated = False

        self._rectangles = {}
        self._new_rectangles = {}

        self.project = None

    def add_rectangle(self, coordinates):
        x0, y0, x1, y1 = coordinates

        h = y1 - y0
        w = x1 - x0

        rect = Rectangle(uuid4().hex, self.project.name, h, w)

        rect.label_id = "n/a"

        self._new_rectangles[rect] = rect
        self._rectangles[rect] = rect
        self._updated = True

        return rect.add_instance(x0, y0)

    def delete(self, rectangle):
        # todo: delete rectangle from database or from buffer
        pass

    def get_rectangle_by_label(self, label):
        pass

    def get_labels_of_type(self, label_type):
        self.project.get_labels(label_type)

    def get_label(self, rectangle_instance):
        return self.project.get_label(rectangle_instance.rectangle.label_id)

    def get_label_types(self):
        return self.project.get_label_types()

    def get_rectangles(self):
        rectangles = self._rectangles
        with engine.connect() as con:
            for row in con.execute(_SELECT_RECTANGLES, project_name=self.project.name):
                r = Rectangle(
                    row["rectangle_id"],
                    row["project_name"],
                    row["height"],
                    row["width"]
                )
                r.label_id = row["label_id"]
                rectangles[r.id] = r
        return rectangles.values()

    def new_rectangles(self):
        return self._new_rectangles

    def submit(self):
        # todo: save new rectangles and updated rectangles
        # and notify the display

        if self._updated == True:
            evt = "update"
            for obs in self.get_observers(evt):
                obs.update(evt, self)
        self._new_rectangles.clear()

    def load(self):
        self.project.load()

    def clear(self):
        self.project.clear()

    def _events(self):
        return ["new", "load", "write", "update"]
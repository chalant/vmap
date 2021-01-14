from uuid import uuid4

from sqlalchemy import text

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
    INSERT OR REPLACE INTO rectangles(rectangle_id, height, width, project_name, label_id)
    VALUES (:rectangle_id, :height, :width, :project_name, :label_id);
    """
)

_ADD_RECTANGLE_INSTANCE = text(
    """
    INSERT INTO rectangle_instances(r_instance_id, rectangle_id, left, top)
    VALUES (:r_instance_id, :rectangle_id, :left, :top);
    """
)

_GET_RECTANGLE_INSTANCES = text(
    """
    SELECT *
    FROM rectangle_instances
    WHERE rectangle_id=:rectangle_id
    """
)

_GET_RECTANGLE_COMPONENTS = text(
    """
    SELECT *
    FROM rectangle_components
    WHERE r_instance_id=:r_instance_id
    """
)

_GET_RECTANGLE_CONTAINER = text(
    """
    SELECT *
    FROM rectangle_components
    WHERE r_component_id=:r_component_id
    """
)

_ADD_RECTANGLE_COMPONENT = text(
    """
    INSERT INTO rectangle_components(r_instance_id, r_component_id)
    VALUES (:r_instance_id, :r_component_id);
    """
)

_DELETE_RECTANGLE = text(
    """
    DELETE FROM rectangles WHERE rectangle_id=:rectangle_id
    """
)

_DELETE_RECTANGLE_INSTANCE = text(
    """
    DELETE FROM rectangle_instances WHERE r_instance_id=:r_instance_id
    """
)

_DELETE_RECTANGLE_COMPONENT = text(
    """
    DELETE FROM rectangle_components WHERE r_instance_id=:r_instance_id
    """
)

class RectangleInstance(object):
    def __init__(self, id_, rectangle, left, top, container_id=None):
        """

        Parameters
        ----------
        rectangle: Rectangle
        left: Int
        top: Int
        container_id: String
        """
        self._id = id_
        self._left = left
        self._top = top

        self._rectangle = rectangle
        self._container_id = container_id

        x1, y1, x2, y2 = self.bbox

        self._center = ((x2 + x1) / 2, (y2 + y1) / 2)

    @property
    def id(self):
        return self._id

    @property
    def rectangle(self):
        return self._rectangle

    @property
    def container_id(self):
        # returns the container rectangle if this rectangle instance
        # todo: if none, load it from data-base, (can be none)
        return self._container_id

    @container_id.setter
    def container_id(self, value):
        self._container_id = value

    @property
    def label_id(self):
        return self._rectangle.label_id

    @label_id.setter
    def label_id(self, value):
        self._rectangle.label_id = value

    @property
    def bbox(self):
        x1 = self._left
        y1 = self._top
        r = self._rectangle
        return (x1, y1, x1 + r.width, y1 + r.height)

    @bbox.setter
    def bbox(self, value):
        self._left = x = value[0]
        self._top = y = value[1]

        r = self._rectangle

        self._center = (x + r.width/2, y + r.height/2)

    @property
    def top_left(self):
        return (self._left, self._top)

    @property
    def bottom_right(self):
        r = self._rectangle
        return (self._left + r.width, self._top + r.height)

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

    def get_components(self):
        components = []

        with engine.connect() as con:
            for row in con.execute(_GET_RECTANGLE_COMPONENTS, r_instance_id=self._id):
                components.append(row["r_component_id"])

        return components

    def delete(self, connection):
        connection.execute(
            _DELETE_RECTANGLE_INSTANCE,
            r_instance_id=self._id
        )

        # remove components
        connection.execute(
            _DELETE_RECTANGLE_COMPONENT,
            r_instance_id=self._id
        )

        self._rectangle.delete(connection)

    def create_instance(self, x, y):
        return self._rectangle.create_instance(x, y)

    def submit(self, connection):
        connection.execute(
            _ADD_RECTANGLE_INSTANCE,
            r_instance_id=self._id,
            rectangle_id=self._rectangle.id,
            left=self._left,
            top=self._top)

        if self._container_id:
            connection.execute(
                _ADD_RECTANGLE_COMPONENT,
                r_instance_id=self._container_id,
                r_component_id=self._id)

        # self._rectangle.submit(connection)

class Rectangle(object):
    def __init__(self, id_, project_name, width, height):
        self._id = id_
        self._project_name = project_name

        self._label_id = None

        self._width = width
        self._height = height

        self._num_instances = 0

    @property
    def id(self):
        return self._id

    @property
    def label_id(self):
        return self._label_id

    @label_id.setter
    def label_id(self, value):
        self._label_id = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    def get_instances(self):
        instances = []
        with engine.connect() as connection:
            for row in connection.execute(
                _GET_RECTANGLE_INSTANCES, rectangle_id=self._id):
                instance_id = row["r_instance_id"]
                container_id = None
                try:
                    container_id = connection.execute(
                        _GET_RECTANGLE_CONTAINER,
                        r_component_id=instance_id).first()["r_instance_id"]
                except:
                    pass

                instances.append(RectangleInstance(
                    instance_id,
                    self,
                    row["left"],
                    row["top"],
                    container_id))

        return instances

    def create_instance(self, x, y, container=None):
        self._num_instances += 1
        return RectangleInstance(uuid4().hex, self, x, y, container)

    def delete(self, connection):
        self._num_instances -= 1

        #delete rectangle if there is no more instance
        if self._num_instances == 0:
            connection.execute(
                _DELETE_RECTANGLE,
                rectangle_id=self._id)

    def submit(self, connection):
        # if self._num_instances == 1:
        connection.execute(
            _ADD_RECTANGLE,
            rectangle_id=self._id,
            height=self._height,
            width=self._width,
            project_name=self._project_name,
            label_id=self._label_id)

    @property
    def perimeter(self):
        return 2 * (self._width + self._height)

    @property
    def area(self):
        return (self._width * self._height)/2

class Rectangles(object):
    def __init__(self, project):

        super(Rectangles, self).__init__()
        # self._engine = engine
        self._updated = False

        self._rectangles = {}
        self._new_rectangles = {}

        self.project = project

    def add_rectangle(self, rectangle):
        self._new_rectangles[rectangle] = rectangle
        self._rectangles[rectangle] = rectangle
        self._updated = True

    def create_rectangle(self, w, h):
        rect = Rectangle(uuid4().hex, self.project.name, w, h)

        rect.label_id = "n/a"

        return rect

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
        instances = []
        with engine.connect() as con:
            for row in con.execute(_SELECT_RECTANGLES, project_name=self.project.name):
                r = Rectangle(
                    row["rectangle_id"],
                    row["project_name"],
                    row["width"],
                    row["height"]
                )
                r.label_id = row["label_id"]
                instances.append(r)
                # for ist in r.get_instances():
                #     instances.append(ist)
        return instances
        # return self._rectangles.values()

    def new_rectangles(self):
        return self._new_rectangles

    def submit(self):
        # todo: save new rectangles and updated rectangles
        # and notify the display

        if self._new_rectangles:
            self.project.update()
        self._new_rectangles.clear()

    def save(self, connection):
        #todo: add all rectangles to database
        pass
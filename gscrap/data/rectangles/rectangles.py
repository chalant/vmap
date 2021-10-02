from uuid import uuid4

from sqlalchemy import text

from gscrap.projects import scenes

from gscrap.data.rectangles import rectangle_labels as rct_lbl
from gscrap.data.rectangles import rectangle_images as rct_img
from gscrap.data.rectangles import rectangle_instances as rct_ist

_SELECT_RECTANGLES = text(
    """
    SELECT * FROM rectangles;
    """
)

_SELECT_CAPTURE_RECTANGLES = text(
    """
    SELECT * FROM rectangles
    LEFT JOIN labels 
        ON rectangles.label_name = labels.label_name AND rectangles.label_type = labels.label_type
    WHERE capture = 1
    """
)

_ADD_RECTANGLE = text(
    """
    INSERT OR REPLACE INTO rectangles(rectangle_id, height, width, project_name)
    VALUES (:rectangle_id, :height, :width, :project_name);
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
    SELECT * FROM rectangle_instances
    WHERE rectangle_id=:rectangle_id
    """
)

_GET_RECTANGLE_COMPONENTS = text(
    """
    SELECT * FROM rectangle_components
    WHERE r_instance_id=:r_instance_id
    """
)

_GET_RECTANGLE_CONTAINER = text(
    """
    SELECT * FROM rectangle_components
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
    DELETE FROM rectangles 
    WHERE rectangle_id=:rectangle_id
    """
)

_DELETE_RECTANGLE_INSTANCE = text(
    """
    DELETE FROM rectangle_instances 
    WHERE r_instance_id=:r_instance_id
    """
)

_DELETE_RECTANGLE_COMPONENT = text(
    """
    DELETE FROM rectangle_components 
    WHERE r_instance_id=:r_instance_id
    """
)

class RectangleInstance(object):
    __slots__ = ['_id', '_left', '_top', '_rectangle', '_container_id', '_center']

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
        return self._container_id

    @container_id.setter
    def container_id(self, value):
        self._container_id = value

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

    def get_components(self):
        components = []

        with scenes.connect(self.rectangle.scene) as con:
            for row in con.execute(_GET_RECTANGLE_COMPONENTS, r_instance_id=self._id):
                components.append(row["r_component_id"])

        return components

    def delete(self, connection):
        id_ = self._id

        connection.execute(
            _DELETE_RECTANGLE_INSTANCE,
            r_instance_id=id_
        )

        # remove components
        connection.execute(
            _DELETE_RECTANGLE_COMPONENT,
            r_instance_id=id_
        )

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

class Rectangle(object):
    __slots__ = [
        '_id',
        '_scene',
        '_width',
        '_height'
    ]

    def __init__(self, id_, scene, width, height):
        self._id = id_
        self._scene = scene

        self._width = width
        self._height = height

    @property
    def scene_name(self):
        return self._scene.name

    @property
    def scene(self):
        return self._scene

    @property
    def id(self):
        return self._id

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

    def get_instances(self, connection):
        return get_rectangle_instances(connection, self)

    def create_instance(self, x, y, container=None):
        return RectangleInstance(uuid4().hex, self, x, y, container)

    def delete(self, connection):
        # deletes instances and components
        for instance in get_rectangle_instances(connection, self):
            instance.delete(connection)

        connection.execute(
            _DELETE_RECTANGLE,
            rectangle_id=self._id)


    def submit(self, connection):
        # if self._num_instances == 1:

        connection.execute(
            _ADD_RECTANGLE,
            rectangle_id=self._id,
            height=self._height,
            width=self._width
        )

    @property
    def perimeter(self):
        return 2 * (self._width + self._height)

    @property
    def area(self):
        return (self._width * self._height)/2

    def __eq__(self, other):
        return other.id == self._id

    def __hash__(self):
        return self._id

def get_rectangles(connection):
    for row in connection.execute(_SELECT_RECTANGLES):
        yield Rectangle(
            row["rectangle_id"],
            row["project_name"],
            row["width"],
            row["height"])

def create_rectangle(width, height, project_name):
    return Rectangle(uuid4().hex, project_name, width, height)

def number_of_instances(connection, rectangle_id):
    total = 0

    for _ in connection.execute(_GET_RECTANGLE_INSTANCES, rectangle_id=rectangle_id):
        total += 1

    return total

def delete_rectangle(connection, rectangle):
    #delete all elements that references the rectangle first

    for instance in get_rectangle_instances(connection, rectangle):
        rct_ist.delete_rectangle_instance(connection, instance)

    rct_lbl.delete_all_rectangle_labels(connection, rectangle)
    rct_img.delete_rectangle_images(connection, rectangle)

    connection.execute(
        _DELETE_RECTANGLE,
        rectangle_id=rectangle.id)


def get_rectangle_instances(connection, rectangle):
    for res in connection.execute(
            _GET_RECTANGLE_INSTANCES, rectangle_id = rectangle.id):

        instance_id = res["r_instance_id"]
        container_id = None
        try:
            container_id = connection.execute(
                _GET_RECTANGLE_CONTAINER,
                r_component_id=instance_id).first()["r_instance_id"]
        except:
            pass

        yield RectangleInstance(
            instance_id,
            rectangle,
            res['left'],
            res['top'],
            container_id
        )

def delete_for_scene(connection):
    for rectangle in get_rectangles(connection):
        rectangle.delete(connection)

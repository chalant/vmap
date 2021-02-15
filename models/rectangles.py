from uuid import uuid4

from sqlalchemy import text

from models import images
from data import engine

_SELECT_RECTANGLES = text(
    """
    SELECT *
    FROM rectangles
    WHERE project_name=:project_name;
    """
)

_SELECT_CAPTURE_RECTANGLES = text(
    """
    SELECT *
    FROM rectangles
    LEFT JOIN labels 
        ON rectangles.label_name = labels.label_name AND rectangles.label_type = labels.label_type
    WHERE capture = 1
    """
)

_ADD_RECTANGLE = text(
    """
    INSERT OR REPLACE INTO rectangles(rectangle_id, height, width, project_name, label_name, label_type)
    VALUES (:rectangle_id, :height, :width, :project_name, :label_name, :label_type);
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

_GET_LABEL = text(
    """
    SELECT *
    FROM labels
    WHERE label_name=:label_name AND label_type=:label_type
    """
)

_GET_IMAGE = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name AND r_instance_id=:r_instance_id
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
    def capture(self):
        return self._rectangle.capture

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
    def label_type(self):
        return self._rectangle.label_type

    @property
    def label_name(self):
        return self._rectangle.label_name

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

    def get_images(self, connection):
        for element in connection.execute(
            _GET_IMAGE,
            project_name=self._rectangle.project_name,
            r_instance_id=self._id):

            yield images.ImageMetadata(
                element['image_id'],
                self._rectangle.project_name,
                self._id,
                element["hash_key"],
                element["position"],
                element["label_instance_name"]
            )

    def create_image_meta(self, id_, hash_key, position):
        return images.ImageMetadata(
            id_, self._rectangle.project_name, self._id, hash_key, position)

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
    __slots__ = ['_id', '_project_name', '_width', '_height', '_capture', '_label_type', '_label_name', '_num_instances']

    def __init__(self, id_, project_name, width, height, capture=False):
        self._id = id_
        self._project_name = project_name

        self._label_name = None
        self._label_type = None

        self._width = width
        self._height = height

        self._num_instances = 0

        self._capture = capture

    @property
    def project_name(self):
        return self._project_name

    @property
    def id(self):
        return self._id

    @property
    def capture(self):
        return self._capture

    @property
    def label_name(self):
        return self._label_name

    @label_name.setter
    def label_name(self, value):
        self._label_name = value

    @property
    def label_type(self):
        return self._label_type

    @label_type.setter
    def label_type(self, value):
        self._label_type = value

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

            yield RectangleInstance(
                instance_id,
                self,
                row["left"],
                row["top"],
                container_id)

    def create_instance(self, x, y, container=None):
        self._num_instances += 1
        return RectangleInstance(uuid4().hex, self, x, y, container)

    def delete(self, connection):
        self._num_instances -= 1

        #delete cz if there is no more instance
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
            label_type=self._label_type,
            label_name=self._label_name
        )

    @property
    def perimeter(self):
        return 2 * (self._width + self._height)

    @property
    def area(self):
        return (self._width * self._height)/2

class Rectangles(object):
    def __init__(self, project):
        super(Rectangles, self).__init__()

        self.project = project

    def create_rectangle(self, w, h, project_name):
        rect = Rectangle(uuid4().hex, project_name, w, h)

        rect.label_name = "n/a"
        rect.label_type = "n/a"

        return rect

    def get_label(self, rectangle_instance):
        return self.project.get_label(rectangle_instance.rectangle.label_id)

    def get_rectangles(self, connection, project_name):
        for row in connection.execute(_SELECT_RECTANGLES, project_name=project_name):
            ln = row["label_name"]
            lt = row["label_type"]

            label = connection.execute(_GET_LABEL, label_name=ln, label_type=lt).fetchone()

            r = Rectangle(
                row["rectangle_id"],
                row["project_name"],
                row["width"],
                row["height"],
                label["capture"] if label is not None else False)

            r.label_name = ln
            r.label_type = lt

            yield r
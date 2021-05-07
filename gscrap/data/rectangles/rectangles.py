from uuid import uuid4

from sqlalchemy import text

from gscrap.data import images
from gscrap.data import engine

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
    INNER JOIN rectangle_labels 
        ON rectangle_labels.label_name=images.label_name 
        AND rectangle_labels.label_type=images.label_type
    WHERE project_name=:project_name AND label_name=:label_name AND label_type=:label_type
    ORDER BY position ASC
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
        return self._rectangle.get_images(connection)

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
        '_project_name',
        '_width',
        '_height',
        '_num_instances',
    ]

    def __init__(self, id_, project_name, width, height):
        self._id = id_
        self._project_name = project_name

        self._width = width
        self._height = height

        self._num_instances = 0

    @property
    def project_name(self):
        return self._project_name

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

    def get_images(self, connection):
        rectangle = self

        for element in connection.execute(
                _GET_IMAGE,
                project_name=rectangle.project_name,
                rectangle_id=rectangle.id):
            yield images.ImageMetadata(
                element['image_id'],
                rectangle.project_name,
                rectangle,
                element["hash_key"],
                element["position"],
                element["label_instance_name"]
            )

    def create_image_meta(self, id_, hash_key, position, label):
        rct = self
        return images.ImageMetadata(
            id_, rct.project_name, rct.id, hash_key, position, label)

    def submit(self, connection):
        # if self._num_instances == 1:

        connection.execute(
            _ADD_RECTANGLE,
            rectangle_id=self._id,
            height=self._height,
            width=self._width,
            project_name=self._project_name
        )

    @property
    def perimeter(self):
        return 2 * (self._width + self._height)

    @property
    def area(self):
        return (self._width * self._height)/2

    def __eq__(self, other):
        return other.id == self._id

class Rectangles(object):
    def __init__(self, project):
        super(Rectangles, self).__init__()

        self.project = project

    def create_rectangle(self, w, h, project_name):
        return Rectangle(uuid4().hex, project_name, w, h)

    def get_rectangles(self, connection, project_name):
        for row in connection.execute(_SELECT_RECTANGLES, project_name=project_name):
            yield Rectangle(
                row["rectangle_id"],
                row["project_name"],
                row["width"],
                row["height"])
from os import path
from functools import partial

from PIL import Image

from sqlalchemy import text

from data import engine
from data import data
from data import paths
from data import io

from models import rectangles

data.build() #populate database

_GET_LEAF_PROJECT_TYPES = text(
    """
    SELECT * 
    FROM project_types
    WHERE has_child=0;
    """
)

_DELETE_PROJECT = text(
    """
    DELETE FROM projects
    WHERE project_name=:project_name
    """
)

_ADD_PROJECT = text(
    """
    INSERT OR REPLACE INTO projects(project_type, project_name, height, width)
    VALUES (:project_type, :project_name, :height, :width);
    """
)

_GET_PROJECTS = text(
    """
    SELECT *
    FROM projects
    """
)

_GET_PROJECT = text(
    """
    SELECT *
    FROM projects
    WHERE project_name=:project_name;
    """
)

_GET_LABEL = text(
    """
    SELECT *
    FROM labels
    WHERE project_type=:project_type;
    """
)

_GET_LABEL_TYPES = text(
    """
    SELECT *
    FROM label_types
    """
)

_GET_PROJECT_TYPE = text(
    """
    SELECT * 
    FROM project_types
    WHERE project_type = :project_type;
    """
)

_GET_PROJECT_TYPE_COMPONENTS = text(
    """
    SELECT *
    FROM project_types
    INNER JOIN project_type_components 
        ON project_type_components.project_type = project_types.project_type
    WHERE project_types.project_type = :project_type;
    """
)

class Project(object):
    def __init__(self, name, type_, width=None, height=None, is_new=True):
        self._name = name
        self._type = type_

        self._width = width
        self._height = height

        self._update = False
        self._is_new = is_new

        self._labels = {}

        self._rectangles = rectangles.Rectangles(self)

        self._template_path = path.join(paths.global_path(paths.templates()), name)

        def null_callback(data):
            pass

        self._update_callback = null_callback
        self._template_callback = null_callback

    @property
    def rectangles(self):
        return self._rectangles

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._update = True

    @property
    def project_type(self):
        return self._type

    @project_type.setter
    def project_type(self, value):
        self._type = value
        self._update = True

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

    def _get_labels(self, connection, project_type, label_type):
        row = connection.execute(_GET_PROJECT_TYPE, project_type=project_type).fetchone()

        parent = row["parent_project_type"]

        for lt in connection.execute(_GET_LABEL, project_type=project_type):
            if lt["label_type"] == label_type:
                yield lt

        for cmp in connection.execute(_GET_PROJECT_TYPE_COMPONENTS, project_type=project_type):
            for element in self._get_labels(connection, cmp["component_project_type"], label_type):
                yield element

        while parent != None:
            for element in self._get_labels(connection, parent, label_type):
                yield element

            parent = connection.execute(_GET_PROJECT_TYPE, project_type=parent).fetchone()["parent_project_type"]

    def get_rectangles(self, connection):
        return self._rectangles.get_rectangles(connection, self.name)

    def create_rectangle(self, width, height):
        return self._rectangles.create_rectangle(width, height, self.name)

    def get_label_types(self, connection):
        for row in connection.execute(_GET_LABEL_TYPES):
            yield row["label_type"]

    def get_labels_of_type(self, connection, label_type):
        for element in self._get_labels(connection, self.project_type, label_type):
            yield element

    def get_label_instances(self, connection, label_id):
        pass

    def get_label_components(self, connection, label_id):
        pass

    def save(self, connection):
        connection.execute(
            _ADD_PROJECT,
            project_name=self.name,
            project_type=self.project_type,
            width=self.width,
            height=self.height)

    def delete(self, connection):
        connection.execute(
            _DELETE_PROJECT,
            project_name=self.name)

    def store_template(self, image):
        io.execute(partial(self._store_template, image=image))

    def load_template(self, callback):
        io.execute(partial(self._load_image, callback=callback))

    def template_update(self, callback):
        self._template_callback = callback

    def _load_image(self, callback):
        try:
            # with open(self._template_path) as f:
            callback(Image.open(self._template_path, formats=("PNG",)))
        except FileNotFoundError:
            pass

    def _store_template(self, image):
        image.save(self._template_path, "PNG")
        self._template_callback(image)

    def clear(self):
        self._labels.clear()

    def on_update(self, callback):
        self._update_callback = callback

    def update(self):
        self._update_callback(self)

class Projects(object):
    def create_project(self, name, type_):
        return Project(name, type_)

    def open_project(self, project_name):
        with engine.connect() as con:
            row = con.execute(_GET_PROJECT, project_name=project_name).fetchone()
            return Project(
                row["project_name"],
                row["project_type"],
                row["width"],
                row["height"],
                False)

    def get_project_names(self, connection):
        for row in connection.execute(_GET_PROJECTS):
            yield row["project_name"]

    def get_project_types(self, connection):
        for row in connection.execute(_GET_LEAF_PROJECT_TYPES):
            yield row["project_type"]


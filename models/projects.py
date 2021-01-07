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

_ADD_PROJECT = text(
    """
    INSERT INTO projects (project_name, project_type, project_path)
    VALUES (:name, :type_, :width, :height);
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
    WHERE project_name = :name;
    """
)

_GET_LABELS = text(
    """
    SELECT *
    FROM labels
    WHERE project_type=:project_type;
    """
)

_GET_PROJECT_TYPE = text(
    """
    SELECT * 
    FROM project_types
    WHERE project_type = :type_;
    """
)

_GET_PROJECT_TYPE_COMPONENTS = text(
    """
    SELECT *
    FROM project_types
    INNER JOIN project_type_components 
        ON project_type_components.project_type = project_types.project_type
    WHERE project_type = :project_type;
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

    def _get_labels(self, project_type, labels, con):
        row = con.execute(_GET_PROJECT_TYPE, project_type=project_type).fetchone()
        label_row = con.execute(_GET_LABELS, project_type=project_type).fetchone()
        labels[label_row["label_id"]] = label_row

        components = con.execute(_GET_PROJECT_TYPE_COMPONENTS, project_type=project_type)

        for c in components:
            t = c["component_project_type"]
            component_label = con.execute(
                _GET_LABELS, project_type=t).fetchone()

            # add components hierarchy labels
            self._get_labels_inner(t, labels, con)

        return row["parent"]

    def _get_labels_inner(self, project_type, labels, con):
        label = self._get_labels(project_type, labels, con)

        # loop until there is no parent (we've reached root)
        while label != None:
            label = self._get_labels(label, labels, con)

    def get_labels(self, label_type):
        return [l for l in self._labels.values() if l["label_type"] == label_type]

    def get_label_types(self):
        return [l["label_type"] for l in self._labels.values()]

    def get_label(self, label_id):
        return self._labels[label_id]

    def load(self):
        # retrieve all labels by climbing up the tree. (multiple joins)
        # and retrieving components at each level as-well

        labels = self._labels

        if not labels:
            with engine.connect() as con:
                label = self._get_labels(self._type, labels, con)

                # loop until there is no parent (we've reached root)
                while label != None:
                    label = self._get_labels(label, labels, con)

    def save(self):
        if self._is_new:
            with engine.connect() as con:
                con.execute(
                    _ADD_PROJECT,
                    name=self.name,
                    type_=self.project_type,
                    width=self.width,
                    height=self.height)

    def _save(self):
        # todo: update project name if not new
        if self._is_new:
            with engine.connect() as con:
                con.execute(
                    _ADD_PROJECT,
                    name=self.name,
                    type_=self.project_type,
                    width=self.width,
                    height=self.height)

    def store_template(self, image):
        io.execute(partial(self._store_template, image=image))

    def load_template(self, callback):
        io.execute(partial(self._load_image, callback=callback))

    def template_update(self, callback):
        self._template_callback = callback

    def _load_image(self, callback):
        try:
            with open(self._template_path) as f:
                callback(Image.open(f, formats=("PNG",)))
        except FileNotFoundError:
            pass

    def _store_template(self, image):
        with open(self._template_path, "w+") as f:
            image.save(f, "PNG")
            self._template_callback(image)

    def clear(self):
        self._labels.clear()

    def on_update(self, callback):
        self._callback = callback

    def update(self):
        self._update_callback(self.rectangles)

class Projects(object):
    def create_project(self, name, type_):
        return Project(name, type_)

    def open_project(self, name):
        with engine.connect() as con:
            row = con.execute(_GET_PROJECT, project_name=name).fetchone()
            return Project(
                row["project_name"],
                row["project_type"],
                row["width"],
                row["height"],
                False)

    def get_project_names(self):
        projects = []

        with engine.connect() as con:
            for row in con.execute(_GET_PROJECTS):
                projects.append(row["project_name"])

        return projects

    def get_project_types(self):
        types = []

        with engine.connect() as con:
            for row in con.execute(_GET_LEAF_PROJECT_TYPES):
                types.append(row["project_type"])
        return types


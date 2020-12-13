from os import path, mkdir

from sqlalchemy import text

from data import engine
from data import data
from data import paths

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
    VALUES (:name, :type_, :path_);
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
    def __init__(self, name, type_):
        self._name = name
        self._type = type_

        self._labels = {}

    @property
    def name(self):
        return self._name

    @property
    def project_type(self):
        return self._type

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

    def clear(self):
        self._labels.clear()

class Projects(object):
    def __init__(self):
        self._project = None

        self._new = False

        self._callbacks = []

    def on_load(self, callback):
        self._callbacks.append(callback)

    def create_project(self, name, type_):
        mkdir(path.join(paths.root(), name))
        self._project = pjt = Project(name, type_)
        self._new = True

        for c in self._callbacks:
            c(pjt)

    def open_project(self, name):
        with engine.connect() as con:
            row = con.execute(_GET_PROJECT, project_name=name).fetchone()

            self._project = pjt = Project(
                row["project_name"],
                row["project_type"])

            for c in self._callbacks:
                c(pjt)

    def get_projects(self):
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

    def save(self):
        if self._new:
            pjt = self._project
            #save project
            with engine.connect() as con:
                con.execute(_ADD_PROJECT, name=pjt.name, type_=pjt.project_type)





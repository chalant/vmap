from uuid import uuid4
from itertools import chain
from abc import abstractmethod, ABC

from sqlalchemy import text

from data import engine

ADD_LABEL_TYPE = text(
    """
    INSERT INTO label_types(label_type)
    VALUES (:label_type)
    """
)

ADD_LABEL = text(
    """
    INSERT INTO labels(label_id, label_name, label_type, parent_type, has_child, parent_type) 
    VALUES (:label_id, :label_name, :label_type, :parent_type, :has_child, :project_type);
     """
)

ADD_LABEL_COMPONENTS = text(
    """
    INSERT INTO label_components(label_id, component_id, lc_id)
    VALUES (:label_id, :component_id:, :lc_id);
    """
)

ADD_PROJECT_TYPE = text(
    """
    INSERT INTO project_types(project_type, parent_project_type, has_child)
    VALUES (:project_type, :parent_project_type, :has_child);
    """
)

ADD_PROJECT_TYPE_COMPONENT = text(
    """
    INSERT INTO project_type_components(project_type, component_project_type)
    VALUES (:project_type, :component_project_type);
    """
)

CLEAR_TABLE = text(
    """
    DROP TABLE IF EXISTS :table_name;
    """
)

_PROJECT_TYPES = {}
_LABEL_TYPES = {}

def clear(connection):
    #clear tables
    table_names = [
        "project_types",
        "project_type_components",
        "labels",
        "label_components"
    ]

    for name in table_names:
        connection.execute(CLEAR_TABLE, table_name=name)

class _Element(ABC):
    def __init__(self):
        self._submit_flag = False

    def submit(self, connection):
        if not self._submit_flag:
            self._submit(connection)
            self._submit_flag = True

    @abstractmethod
    def _submit(self, connection):
        raise NotImplementedError

    def clear(self):
        self._submit_flag = True

class _ProjectType(_Element):
    def __init__(self, name):
        super(_ProjectType, self).__init__()
        self.parent_type = None
        self._name = name
        self._labels = []
        self._children = []
        self._components = []

        self._submit_flag = False

    @property
    def name(self):
        return self._name

    def add_label(self, name, type_, max_=None):
        lbl = _Label(self._name, name, type_.name, max_)
        self._labels.append(lbl)
        return lbl

    def add_child(self, name):
        pt = _ProjectType(name)
        pt.parent_type = self._name
        self._children.append(pt)
        return pt

    def add_component(self, project_type):
        self._components.append(project_type)

    def _submit(self, connection):
        if not self._submit_flag:
            connection.execute(
                ADD_PROJECT_TYPE,
                project_type=self._name,
                parent_project_type=self.parent_type,
                has_child=True if self._children else False)

            for lbl in self._labels:
                lbl.submit(connection)

            for child in self._children:
                child.submit(connection)

            for component in self._components:
                connection.execute(
                    ADD_PROJECT_TYPE_COMPONENT,
                    project_type=self._name,
                    component_project_type=component.name)
            self._submit_flag = True

class _LabelType(_Element):
    def __init__(self, name):
        super(_LabelType, self).__init__()
        self._name = name
        self._submit_flag = name

    @abstractmethod
    def name(self):
        return self._name

    def _submit(self, connection):
        if not self._submit_flag:
            connection.execute(
                ADD_LABEL_TYPE,
                label_type=self._name)

class _Label(_Element):
    def __init__(self, project_type, label_name, label_type, max_=None):
        super(_Label, self).__init__()
        self._id_ = uuid4().hex

        self._label_name = label_name
        self._label_type = label_type
        self._project_type = project_type

        self.parent_id = None
        self.component_id = None
        self.capture = False
        self._max = max_

        self._children = []
        self._components = []

        self._submit_flag = False

    @property
    def label_id(self):
        return self._id_

    def add_child(self, label):
        label.parent_type = self._id_
        self._children.append(label)

    def add_component(self, label):
        #link the label to this label.
        self._components.append(label.label_id)

    def _submit(self, connection):
        hc = True if self._children else False
        connection.execute(
            ADD_LABEL,
            label_id=self._id_,
            label_name=self._label_name,
            label_type=self._label_type,
            parent_id=self.parent_id if self.parent_id else None,
            has_child=hc,
            project_type=self._project_type
        )

        id_ = self._id_
        #submit components
        for label_id in self._components:
            connection.execute(
                ADD_LABEL_COMPONENTS,
                label_id=id_,
                component_id=label_id,
                lc_id=uuid4().hex)

        for child in self._children:
            child.submit(connection)

    def clear(self):
        self._submit_flag = False

def submit():
    with engine.connect() as connection:
        clear(connection)
        for pj in chain(_PROJECT_TYPES.values(), _LABEL_TYPES.values()):
            pj.clear()
            pj.submit(connection)

def project_type(name):
    pj = _ProjectType(name)
    _PROJECT_TYPES[name] = pj
    return pj

def label_type(name):
    lt = _LabelType(name)
    _LABEL_TYPES[name] = lt
    return lt

class _Builder(object):
    def __enter__(self):
        return self

    def project_type(self, name):
        return project_type(name)

    def label_type(self, name):
        return label_type(name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        submit()

_BUILDER  = _Builder()

def build():
    return _BUILDER
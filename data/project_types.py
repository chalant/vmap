from sqlalchemy import text

from data.base import _Element
from data.labels import _Label

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

    def add_label(self, name, type_, max_=None, capture=False):
        lbl = _Label(self._name, name, type_.name, max_, capture)
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
from uuid import uuid4

from sqlalchemy import text

from data.base import _Element

ADD_LABEL_TYPE = text(
    """
    INSERT INTO label_types(label_type)
    VALUES (:label_type)
    """
)

ADD_LABEL = text(
    """
    INSERT INTO labels(label_id, label_name, label_type, capture, max_instances, total, project_type) 
    VALUES (:label_id, :label_name, :label_type, :capture, :max_instances, :total, :project_type);
     """
)

ADD_LABEL_COMPONENTS = text(
    """
    INSERT INTO label_components(label_id, component_id, lc_id)
    VALUES (:label_id, :component_id:, :lc_id);
    """
)

ADD_LABEL_INSTANCE = text(
    """
    INSERT INTO label_instances(instance_id, label_id, instance_name) 
    VALUES (:instance_id, :label_id, :instance_name);
    """
)

class _LabelType(_Element):
    def __init__(self, name):
        super(_LabelType, self).__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    def _submit(self, connection):
        if self._name:
            connection.execute(
                ADD_LABEL_TYPE,
                label_type=self._name)

class _LabelInstance(_Element):
    __slots__ = ["instance_id", "label_id", "instance_name"]

    def __init__(self, instance_id, label_id, instance_name):
        super(_LabelInstance, self).__init__()

        self.instance_id = instance_id
        self.label_id = label_id
        self.instance_name = instance_name

    def _submit(self, connection):
        connection.execute(
            ADD_LABEL_INSTANCE,
            instance_id=self.instance_id,
            instance_name=self.instance_name,
            label_id=self.label_id
        )

class _Label(_Element):
    __slots__ = ["_instances", "_label_id", "_label_name", "_label_type", "_total", "_max"]

    def __init__(self, project_type, label_name, label_type, max_=None, capture=False):
        super(_Label, self).__init__()
        self._label_id = uuid4().hex

        self._label_name = label_name
        self._label_type = label_type
        self._project_type = project_type

        self._capture = capture
        self._max = max_
        self._total = 0

        self._components = []
        self._instances = []

    @property
    def label_id(self):
        return self._label_id

    def add_instance(self, instance_name):
        """

        Parameters
        ----------
        label_instance: _LabelInstance

        Returns
        -------

        """
        if not self._max:
            instance = _LabelInstance(
                uuid4().hex,
                self._label_id,
                instance_name)
            self._instances.append(instance)
        else:
            if self._total < self._max:
                instance = _LabelInstance(
                    uuid4().hex,
                    self._label_id,
                    instance_name)
                self._total += 1
                self._instances.append(instance)

    def add_component(self, label):
        #link the label to this label.
        self._components.append(label)

    def _submit(self, connection):
        connection.execute(
            ADD_LABEL,
            label_id=self._label_id,
            label_name=self._label_name,
            label_type=self._label_type,
            project_type=self._project_type,
            max_instances=self._max,
            capture=self._capture,
            total=self._total
        )

        #submit components
        for label in self._components:
            label.submit(connection)

        for instance in self._instances:
            instance.submit(connection)



from uuid import uuid4

from sqlalchemy import text

from gscrap.utils import key_generator

from gscrap.data.base import _Element
from gscrap.data.properties import properties as pp

ADD_LABEL_TYPE = text(
    """
    INSERT INTO label_types(label_type)
    VALUES (:label_type)
    """
)

_ADD_LABEL = text(
    """
    INSERT OR IGNORE INTO labels(label_id, label_name, label_type, capture, max_instances, total, project_type, classifiable) 
    VALUES (:label_id, :label_name, :label_type, :capture, :max_instances, :total, :project_type, :classifiable);
     """
)

ADD_LABEL_COMPONENTS = text(
    """
    INSERT INTO label_components(label_id, component_id)
    VALUES (:label_id, :component_id);
    """
)

ADD_LABEL_INSTANCE = text(
    """
    INSERT INTO label_instances(instance_id, instance_name, label_name, label_type) 
    VALUES (:instance_id, :instance_name, :label_name, :label_type);
    """
)

ADD_LABEL_PROPERTY = text(
    """
    INSERT INTO label_properties(label_type, label_name, property_type, property_name)
    VALUES (:label_type, :label_name, :property_type, :property_name)
    """
)

_GET_LABEL = text(
    """
    SELECT * 
    FROM labels
    WHERE label_name=:label_name AND scene_name=:scene_name
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

    def __init__(self, instance_id, instance_name, label_name, label_type):
        super(_LabelInstance, self).__init__()

        self.instance_id = instance_id
        self.label_name = label_name
        self.label_type = label_type
        self.instance_name = instance_name

    def _submit(self, connection):
        connection.execute(
            ADD_LABEL_INSTANCE,
            instance_id=self.instance_id,
            instance_name=self.instance_name,
            label_name=self.label_name,
            label_type=self.label_type
        )

class LabelWriter(_Element):
    __slots__ = [
        "_instances",
        "_label_id",
        "_label_name",
        "_label_type",
        "_classifiable",
        "_property",
        "_total",
        "_max"]

    def __init__(
            self,
            scene_name,
            label,
            max_=None,
            capture=False,
            classifiable=False):

        super(LabelWriter, self).__init__()
        self._label_id = uuid4().hex

        self._label = label

        self._label_type = label.label_type
        self._label_name = label.label_name

        self._scene_name = scene_name

        self._capture = capture
        self._max = max_
        self._total = 0
        self._classifiable = classifiable

        self._components = []
        self._instances = []
        self._properties = []

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
        if self._classifiable:
            if not self._max:
                instance = _LabelInstance(
                    uuid4().hex,
                    instance_name,
                    self._label_name,
                    self._label_type)

                self._instances.append(instance)
            else:
                if self._total < self._max:
                    instance = _LabelInstance(
                        uuid4().hex,
                        instance_name,
                        self._label_name,
                        self._label_type)
                    self._total += 1
                    self._instances.append(instance)
        else:
            raise ValueError(
                "Non classifiable label"
            )

    def add_component(self, label):
        #link the label to this label.
        self._components.append(label)

    def add_property(self, property_):
        self._properties.append(property_)

    def _submit(self, connection):
        label_name = self._label_name
        label_type = self._label_type

        connection.execute(
            _ADD_LABEL,
            label_id=self._label_id,
            label_name=label_name,
            label_type=label_type,
            scene_name=self._scene_name,
            max_instances=self._max,
            capture=self._capture,
            total=self._total,
            classifiable=self._classifiable
        )

        for property_ in self._properties:
            pp.add_property(connection, property_)
            connection.execute(
                ADD_LABEL_PROPERTY,
                label_name=label_name,
                label_type=label_type,
                property_type=property_.property_type,
                property_name=property_.property_name
            )

        label_id = hash(self._label)

        #map components to this label
        for label in self._components:
            connection.execute(
                ADD_LABEL_COMPONENTS,
                label_id,
                hash(label)
            )

        for instance in self._instances:
            instance.submit(connection)

class Label(object):
    __slots__ = ['label_type', 'label_name']

    def __init__(self, label_type, label_name):
        self.label_type = label_type
        self.label_name = label_name

    def __hash__(self):
        return key_generator.generate_key(self.label_type + self.label_name)

    def __eq__(self, other):
        return other.label_type == self.label_type and \
               other.label_type == other.label_type

def label_type(label):
    return label.label_type

def label_name(label):
    return label.label_name

def get_label(connection, label_name, scene_name):
    res = connection.execute(
        _GET_LABEL,
        label_name=label_name,
        scene_name=scene_name)

    return Label(res['label_type'], res['label_name'])
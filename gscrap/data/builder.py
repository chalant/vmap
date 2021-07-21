from itertools import chain

from gscrap.data import engine
from gscrap.data.project_types import _ProjectType
from gscrap.data.labels.labels import _LabelType

from gscrap.data.properties import properties
from gscrap.data import attributes

CLEAR_TABLE = '''
    DELETE FROM {};
'''

_PROJECT_TYPES = {}
_LABEL_TYPES = {}
_PROPERTY_TYPES = {}
_PROPERTY_NAMES = {}
_PROPERTIES = {}

_PROPERTY_ATTRIBUTES = {}

def clear(connection):
    #clear tables
    table_names = [
        "project_types",
        "project_type_components",
        "labels",
        "label_components",
        "label_types",
        "label_instances",
        "properties",
        "property_types",
        "property_attributes",
        "attributes"
    ]

    for name in table_names:
        connection.execute(CLEAR_TABLE.format(name))

def _submit():
    with engine.connect() as connection:
        clear(connection)

        attributes.add_attribute(connection, attributes.UNIQUE)
        attributes.add_attribute(connection, attributes.INCREMENTAL)

        for pp in _PROPERTIES.values():
            properties.add_property_type(connection, pp.property_type)
            properties.add_property_name(connection, pp.property_name)

        for atr in _PROPERTY_ATTRIBUTES.values():
            properties.add_property_attribute(connection, atr)

        for pj in chain(
            _LABEL_TYPES.values(),
            _PROJECT_TYPES.values()):

            pj._submit(connection)
            pj.clear()

def project_type(name):
    pj = _ProjectType(name)
    _PROJECT_TYPES[name] = pj
    return pj

def _label_type(name):
    lt = _LabelType(name)
    _LABEL_TYPES[name] = lt
    return lt

def _property_(type_, name):
    ppt = properties.Property(type_, name)
    if ppt not in _PROPERTIES:
        _PROPERTIES[ppt] = ppt
    return ppt

def _add_property_attribute(property_, attribute):
    atr = properties.PropertyAttribute(property_, attribute)
    if atr not in _PROPERTY_ATTRIBUTES:
        _PROPERTY_ATTRIBUTES[atr] = atr

class _Builder(object):
    def __init__(self):
        self._built = False

    def __enter__(self):
        return self

    def label_type(self, name):
        return _label_type(name)

    def property_(self, type_, name):
        if type_ not in properties.PROPERTY_TYPES:
            return _property_(type_, name)
        else:
            raise ValueError("Property type {} is not supported".format(type_))

    def property_attribute(self, property_, attribute):
        if attribute not in properties.PROPERTY_TYPE_ATTRIBUTES[property_.property_type]:
            raise ValueError("Cannot assign {} attribute to {} property type".format(
                attribute,
                property_.property_type))

        _add_property_attribute(property_, attribute)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._built:
            _submit()
        self._built = True

_BUILDER  = _Builder()

def build():
    return _BUILDER
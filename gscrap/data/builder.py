from itertools import chain

from sqlalchemy import text

from gscrap.data import engine
from gscrap.data.project_types import _ProjectType
from gscrap.data.labels.labels import _LabelType
from gscrap.data.labels import labels

from gscrap.data.properties import properties
from gscrap.data import attributes
from gscrap.data.properties import value_source_factory as vsb
from gscrap.data.properties.values_sources import values_sources
from gscrap.data.properties import property_values_source as pvs

CLEAR_TABLE = '''
    DROP TABLE IF EXISTS {};
'''

_PROJECT_TYPES = {}
_LABEL_TYPES = {}
_PROPERTY_TYPES = {}
_PROPERTY_NAMES = {}
_PROPERTIES = {}

_PROPERTY_ATTRIBUTES = {}

_PROPERTY_VALUE_SOURCES = {}

_VALUES_SOURCES = []

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
        "property_names",
        "label_properties",
        "property_types",
        "property_attributes",
        "attributes",
        "properties_values_sources",
        "values_sources",
        "values_sources_names",
        "values_sources_types"
    ]

    for name in table_names:
        connection.execute(text(CLEAR_TABLE.format(name)))

def _submit(connection):
    #create value sources mappings

    values_sources.add_values_source_type(connection, 'input')
    values_sources.add_values_source_name(connection, 'values_input')

    values_sources.add_values_source_type(connection, 'generator')
    values_sources.add_values_source_name(connection, 'incremental_generator')

    for vs in _VALUES_SOURCES:
        values_sources.add_values_source(connection, vs)

    attributes.add_attribute(connection, attributes.DISTINCT)
    attributes.add_attribute(connection, attributes.GLOBAL)

    for pp in _PROPERTIES.values():
        properties.add_property_type(connection, pp.property_type)
        properties.add_property_name(connection, pp.property_name)

    for atr in _PROPERTY_ATTRIBUTES.values():
        properties.add_property_attribute(connection, atr)

    for vs in _PROPERTY_VALUE_SOURCES.values():
        pvs.add_property_values_source(
            connection,
            vs.property_values_source)

        #save value source instance
        vs.save(connection)

    for pj in chain(
        _LABEL_TYPES.values(),
        _PROJECT_TYPES.values()):

        pj._submit(connection)
        pj.clear()

def _project_type(name):
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
        self._to_import = {}
        self._to_create = {}

    def __enter__(self):
        with engine.connect() as connection:
            clear(connection)
            engine.create_tables(engine._ENGINE, engine._META)

        return self

    def get_label(self, scene_name, label_name):
        with engine.connect() as connection:
            labels.get_label(connection, label_name, scene_name)

    def new_scene(self, scene_name):
        #todo
        if scene_name not in self._to_create:
            return self._to_create[scene_name]

    def project_type(self, name):
        return _project_type(name)

    def label_type(self, name):
        return _label_type(name)

    def property_(self, type_, name):
        if type_ not in properties.PROPERTY_TYPES:
            raise ValueError("Property type {} is not supported".format(type_))
        return _property_(type_, name)

    def property_attribute(self, property_, attribute):
        _add_property_attribute(property_, attribute)

    def incremental_value_generator(self, property_, start=0, increment=1):
        if not property_ in _PROPERTY_VALUE_SOURCES:
            vs = values_sources.ValuesSource(
                'generator',
                'incremental_generator',
                hash((start, increment)))

            _VALUES_SOURCES.append(vs)

            ppt_vs = pvs.PropertyValueSource(property_, vs)

            _PROPERTY_VALUE_SOURCES[property_] = vsb.incremental_value_generator(
                ppt_vs,
                start,
                increment)

        else:
            raise RuntimeError(
                "Property {} already assigned to a values source".format(property_))

    def input_values(self, property_, values):
        if not property_ in _PROPERTY_VALUE_SOURCES:
            vs = values_sources.ValuesSource(
                'input',
                'values_input',
                hash(str(values)))

            _VALUES_SOURCES.append(vs)

            ppt_vs = pvs.PropertyValueSource(property_, vs)

            _PROPERTY_VALUE_SOURCES[property_] = vsb.input_values(values, ppt_vs)
        else:
            raise RuntimeError(
                "Property {} already assigned to a values source".format(property_))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._built:
            #todo: import and create scenes
            # if the scene doesn't exist in the database, create it
            # if the scene ex

            with engine.connect() as connection:
                for element in self._to_create.values():
                    #todo: create scene
                    pass

                _submit(connection)
        else:
            raise RuntimeError("Schema already built!")

_BUILDER  = _Builder()

def build():
    return _BUILDER
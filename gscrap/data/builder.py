from itertools import chain

from gscrap.data import engine
from gscrap.data.project_types import _ProjectType
from gscrap.data.labels.labels import _LabelType

from gscrap.data.properties import properties
from gscrap.data import attributes
from gscrap.data.properties import value_source_factory as vsb
from gscrap.data.properties.values_sources import values_sources
from gscrap.data.properties import property_values_source as pvs

CLEAR_TABLE = '''
    DELETE FROM {};
'''

_PROJECT_TYPES = {}
_LABEL_TYPES = {}
_PROPERTY_TYPES = {}
_PROPERTY_NAMES = {}
_PROPERTIES = {}

_PROPERTY_ATTRIBUTES = {}

_PROPERTY_VALUE_SOURCES = {}

_ICR_GEN_VS = values_sources.ValuesSource('generator', 'incremental_generator')
_RDN_GEN_VS = values_sources.ValuesSource('generator', 'random_generator')

_INPUT_VS = values_sources.ValuesSource('input', 'values_input')

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
        "attributes",
        "properties_values_sources",
        "values_sources_names",
        "values_sources_types",
        "values_sources",
        "values_sources_incremental_value_generators",
        "values_sources_values_inputs"
    ]

    for name in table_names:
        connection.execute(CLEAR_TABLE.format(name))

def _submit():
    with engine.connect() as connection:
        clear(connection)

        #create value sources mappings

        values_sources.add_values_source_type(connection, 'input')
        values_sources.add_values_source_name(connection, 'values_input')

        values_sources.add_values_source_type(connection, 'generator')
        values_sources.add_values_source_name(connection, 'incremental_generator')

        values_sources.add_values_source(connection, _INPUT_VS)
        values_sources.add_values_source(connection, _ICR_GEN_VS)

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
        _add_property_attribute(property_, attribute)

    def values_source(self, type_, name):
        return values_sources.ValuesSource(type_, name)

    def property_values_source(self, property_, values_source):
        return pvs.PropertyValueSource(property_, values_source)

    def incremental_value_generator(self, property_, start=0, increment=1):
        if not property_ in _PROPERTY_VALUE_SOURCES:
            ppt_vs = pvs.PropertyValueSource(property_, _ICR_GEN_VS)

            _PROPERTY_VALUE_SOURCES[property_] = vsb.incremental_value_generator(
                ppt_vs,
                start,
                increment)
        else:
            raise RuntimeError(
                "Property {} already assigned to a values source".format(property_))

    def input_values(self, property_, values):
        if not property_ in _PROPERTY_VALUE_SOURCES:
            ppt_vs = pvs.PropertyValueSource(property_, _INPUT_VS)

            _PROPERTY_VALUE_SOURCES[property_] = vsb.input_values(
                values,
                ppt_vs)
        else:
            raise RuntimeError(
                "Property {} already assigned to a values source".format(property_))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._built:
            _submit()
        else:
            raise RuntimeError("Schema already built!")

_BUILDER  = _Builder()

def build():
    return _BUILDER
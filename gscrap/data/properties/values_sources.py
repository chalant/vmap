from sqlalchemy import text

from gscrap.data.properties import properties
from gscrap.data.properties.values_sources import incremental_generator
from gscrap.data.properties.values_sources import input_values

_ADD_PROPERTY_VALUES_SOURCE = text(
    """
    INSERT INTO properties_values_sources(property_name, property_type, values_source)
    VALUES(:property_name, :property_type, :values_source)
    """)

_ADD_VALUES_SOURCE = text(
    """
    INSERT OR IGNORE INTO values_sources(values_source)
    VALUES(:values_source)
    """
)

_UNMAP_PROPERTY_VALUES_SOURCE = text(
    """
    DELETE FROM properties_values_sources
    WHERE property_type=:property_type, property_name=:property_name, values_source=:values_source
    """
)

_GET_VALUES_SOURCE_PROPERTIES = text(
    """
    SELECT * FROM values_sources
    INNER JOIN properties_values_sources on properties_values_sources.values_source = values_sources.values_source
    WHERE values_source=:values_source
    """
)

_DELETE_VALUES_SOURCE = text(
    """
    DELETE FROM values_sources
    WHERE values_source=:values_source
    """
)

class InputValues(object):
    name = 'values_input'

    def __init__(self, values):
        self._values = input_values.InputValues(values)

    def save(self, connection):
        input_values.add_input_values(connection, self._values)

    def delete(self, connection):
        input_values.delete_input_values(connection, self._values)

class IncrementalValuesGenerator(object):
    name = 'incremental_generator'

    def __init__(self, from_, increment):
        self._spec = incremental_generator.IncrementalGeneratorSpec(from_, increment)

    def save(self, connection):
        incremental_generator.add_incremental_generator(connection, self._spec)

    def delete(self, connection):
        incremental_generator.delete_incremental_generator(connection, self._spec)

class PropertyValueSource(object):
    def __init__(self, property_, value_source):
        self.property_ = property_
        self.value_source = value_source

def _save_value_source(connection, values_source):
    values_source.save(connection)

def values_source_name(values_source):
    return values_source.name

def unmap_values_source(connection, values_source):
    values_source.delete(connection)

def add_property_values_source(connection, property_values_source):
    property_ = property_values_source.property_

    connection.execute(
        _ADD_PROPERTY_VALUES_SOURCE,
        property_name=properties.property_name(property_),
        property_type=properties.property_type(property_),
        values_source=values_source_name(property_values_source.values_source)
    )

    _save_value_source(connection, property_values_source.values_source)

def unmap_property_value_source(connection, property_values_source):
    property_ = property_values_source.property_
    vn = values_source_name(property_values_source.values_source)

    connection.execute(
        _UNMAP_PROPERTY_VALUES_SOURCE,
        property_name=properties.property_name(property_),
        property_type=properties.property_type(property_),
        values_source=values_source_name(property_values_source.values_source),
    )

    counter = 0

    for _ in connection.execute(_GET_VALUES_SOURCE_PROPERTIES, vn):
        counter += 1

    #remove value source if it is not reference by any property
    if counter == 0:
        unmap_values_source(connection, property_values_source.values_source)
        connection.execute(_DELETE_VALUES_SOURCE)

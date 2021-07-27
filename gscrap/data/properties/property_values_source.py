from sqlalchemy import text

from gscrap.data.properties import properties
from gscrap.data.properties.values_sources import values_sources as vs

_GET_PROPERTY_VALUES_SOURCE = text(
    """
    SELECT * FROM properties_values_sources
    WHERE property_name=:property_name AND property_type=:property_type
    """
)

_ADD_PROPERTY_VALUES_SOURCE = text(
    """
    INSERT INTO properties_values_sources(property_name, property_type, values_source_id)
    VALUES(:property_name, :property_type, :values_source_id)
    """
)


_GET_VALUES_SOURCE_PROPERTIES = text(
    """
    SELECT * FROM values_sources
    INNER JOIN properties_values_sources 
        ON properties_values_sources.value_source_id = values_sources.value_source_id
    WHERE value_source_id=:value_source_id
    """
)

_UNMAP_PROPERTY_VALUES_SOURCE = text(
    """
    DELETE FROM properties_values_sources
    WHERE property_type=:property_type, property_name=:property_name, values_source_id=:values_source_id
    """
)

class PropertyValueSource(object):
    __slots__ = ['property_', 'value_source', '_hash']

    def __init__(self, property_, value_source):
        self.property_ = property_
        self.value_source = value_source

        self._hash = hash((property_, value_source))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return other.property_ == self.property_ and \
               other.value_source == self.value_source

def get_property_values_source(connection, property_):
    return PropertyValueSource(
        property_,
        vs.get_value_source_by_property(connection, property_))

def add_property_values_source(connection, property_values_source):
    property_ = property_values_source.property_

    connection.execute(
        _ADD_PROPERTY_VALUES_SOURCE,
        property_name=properties.property_name(property_),
        property_type=properties.property_type(property_),
        values_source_id=hash(property_values_source.values_source)
    )

    vs.save_value_source(connection, property_values_source.values_source)

def unmap_property_value_source(connection, property_values_source):
    property_ = property_values_source.property_

    connection.execute(
        _UNMAP_PROPERTY_VALUES_SOURCE,
        property_name=properties.property_name(property_),
        property_type=properties.property_type(property_),
        values_source_id=hash(property_values_source.values_source),
    )

    counter = 0

    for _ in connection.execute(
            _GET_VALUES_SOURCE_PROPERTIES,
            hash(property_values_source.values_source)):
        counter += 1

    #remove value source if it is not reference by any property
    if counter == 0:
        vs.unmap_values_source(
            connection,
            property_values_source.values_source)
from sqlalchemy import text

_ADD_VALUES_SOURCE = text(
    """
    INSERT OR IGNORE INTO values_sources(values_source_name, value_source_type)
    VALUES(:values_source_name, :value_source_type)
    """
)

_ADD_VALUES_SOURCE_NAME = text(
    """
    INSERT OR IGNORE INTO values_sources_names(values_source_name)
    VALUES(:values_source_name)
    """
)

_ADD_VALUES_SOURCE_TYPE = text(
    """
    INSERT OR IGNORE INTO values_sources_names(values_source_type)
    VALUES(:values_source_type)
    """
)

_GET_VALUES_SOURCES_BY_PROPERTY = text(
    """
    SELECT * FROM values_sources
    INNER JOIN properties_values_sources
        ON properties_values_sources.values_source_id = values_sources.values_source_id
    WHERE values_source_id=:values_source_id
    """
)

GENERATOR = 'generator'
INPUT = 'input'

class ValuesSource(object):
    def __init__(self, type_, name):
        self.type_ = type_
        self.name = name

    def __hash__(self):
        return hash((self.type_, self.name))

    def __eq__(self, other):
        return other.type_ == self.type_ and \
               other.name == other.type_

def add_values_source(connection, values_source):
    connection.execute(
        _ADD_VALUES_SOURCE,
        values_source_name=values_source.name,
        values_source_type=values_source.type_
    )

def add_values_source_name(connection, name):
    connection.execute(
        _ADD_VALUES_SOURCE_NAME,
        values_source_name=name
    )

def add_values_source_type(connection, type_):
    connection.execute(
        _ADD_VALUES_SOURCE_TYPE,
        values_source_type=type_
    )

def save_value_source(connection, values_source):
    values_source.save(connection)

def values_source_name(values_source):
    return values_source.name

def values_source_type(values_source):
    return values_source.type_

def unmap_values_source(connection, values_source):
    values_source.delete(connection)

def get_value_source_by_property(connection, property_):
    res = connection.execute(
        _GET_VALUES_SOURCES_BY_PROPERTY,
        property_name=property_.property_name,
        property_type=property_.property_type)

    return ValuesSource(
        res['values_source_type'],
        res['values_source_name'])
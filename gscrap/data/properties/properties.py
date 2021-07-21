from sqlalchemy import text

from gscrap.data import attributes

INTEGER = 0
BOOLEAN = 1

PROPERTY_TYPES = {INTEGER, BOOLEAN}

PROPERTY_TYPE_ATTRIBUTES = {
    INTEGER:{attributes.INCREMENTAL, attributes.UNIQUE}
}

_ADD_PROPERTY_TYPE = text(
    '''
    INSERT OR IGNORE INTO property_types(property_type)
    VALUES (:property_type)
    '''
)

_ADD_PROPERTY_VALUE = text(
    '''
    INSERT INTO property_values(property_type, property_name, property_value, property_id)
    VALUES (:property_type, :property_name, :property_value, :property_id)
    '''
)

_DELETE_PROPERTY_VALUE = text(
    """
    DELETE FROM property_values
    WHERE property_id=:property_id
    """
)

_ADD_PROPERTY = text(
    '''
    INSERT OR IGNORE INTO properties(property_name)
    VALUES (:property_name)
    '''
)

_ADD_PROPERTY_ATTRIBUTE = text(
    '''
    INSERT OR IGNORE INTO property_attributes(property_type, property_name, property_attribute)
    VALUES(:property_type, :property_name, :property_attribute)
    '''
)

_GET_PROPERTY_ATTRIBUTES = text(
    """
    SELECT * FROM property_attributes
    WHERE property_type=:property_type AND property_name=:property_name
    """
)

class PropertyType(object):
    __slots__ = ['name']

    def __init__(self, name):
        self.name = name

class PropertyName(object):
    __slots__ = ['name']

    def __init__(self, name):
        self.name = name

class Property(object):
    __slots__ = ['property_type', 'property_name']

    def __init__(self, property_type, property_name):
        self.property_type = property_type
        self.property_name = property_name

    def __hash__(self):
        return hash((self.property_type, self.property_name))

    def __eq__(self, other):
        return other.property_type == self.property_type and \
               other.property_name == self.property_name

class PropertyAttribute(object):
    __slots__ = ['property_', 'attribute']
    def __init__(self, property_, attribute):
        self.property_ = property_
        self.attribute = attribute

    def __hash__(self):
        return hash((self.property_, self.attribute))

    def __eq__(self, other):
        return other.property == self.property_ and \
               other.attribute == other.attribute

class PropertyValue(object):
    __slots__ = ['property_', 'value', '_hash']

    def __init__(self, property_, value):
        self.property_ = property_
        self.value = value
        self._hash = hash((property_, value))

    def __eq__(self, other):
        return other.property == self.property_ and \
               other.value == self.value

    def __hash__(self):
        return self._hash

def property_name(property_):
    return property_.property_name

def property_type(property_):
    return property_.property_type

def add_property_type(connection, property_type):
    connection.execute(
        _ADD_PROPERTY_TYPE,
        property_type=property_type.name
    )

def add_property_name(connection, property_name):
    connection.execute(
        _ADD_PROPERTY,
        property_name=property_name.name
    )

def add_property(connection, property_):
    add_property_type(connection, property_.property_type)
    add_property_name(connection, property_.property_name)

def add_property_attribute(connection, property_attribute):
    ppt = property_attribute.property_
    connection.execute(
        _ADD_PROPERTY_ATTRIBUTE,
        property_attribute=property_attribute.attribute,
        property_type=property_type(ppt),
        property_name=property_name(ppt)
    )

def add_property_value(connection, property_value):
    '''

    Parameters
    ----------
    connection
    property_value: PropertyValue

    Returns
    -------

    '''

    property_ = property_value.property_

    connection.execute(
        _ADD_PROPERTY_VALUE,
        property_type=property_type(property_),
        property_name=property_name(property_),
        property_value=property_value.value,
        property_id=hash(property_value)
    )

def delete_property_value(connection, property_value):
    connection.execute(
        _DELETE_PROPERTY_VALUE,
        property_id=hash(property_value)
    )

def get_property_attributes(connection, property_):
    for res in connection.execute(
        _GET_PROPERTY_ATTRIBUTES,
        property_type=property_.property_type,
        property_name=property_.property_name):

        yield PropertyAttribute(property_, res['attribute_name'])
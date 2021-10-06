from sqlalchemy import text

from gscrap.data.properties import properties

_MAP_TO_PROPERTY_VALUE = text(
    """
    INSERT OR IGNORE INTO rectangle_instances_property_values(r_instance_id, property_id)
    VALUES(:r_instance_id, :property_id)
    """
)

_UNMAP_FROM_PROPERTY_VALUE = text(
    """
    DELETE FROM rectangle_instances_property_values
    WHERE r_instance_id=:r_instance_id AND property_id=:property_id
    """
)

_GET_PROPERTY_VALUE = text(
    """
    SELECT * FROM property_values
    INNER JOIN rectangle_instances_property_values 
        ON rectangle_instances_property_values.property_id = property_values.property_id
    WHERE r_instance_id=:r_instance_id 
        AND property_type=:property_type
        AND property_name=:property_name 
    """
)

_GET_INSTANCES_WITH_PROPERTY_VALUE = text(
    """
    SELECT * FROM rectangle_instances_property_values 
    INNER JOIN property_values 
        ON rectangle_instances_property_values.property_id = property_values.property_id
    WHERE rectangle_instances_property_values.property_id=:property_id
    """
)

_DELETE_ALL_RECTANGLE_INSTANCES = text(
    """
    DELETE FROM rectangle_instances
    WHERE rectangle_id=:rectangle_id
    """
)

_DELETE_RECTANGLE_INSTANCE_PROPERTY_VALUES = text(
    """
    DELETE FROM rectangle_instances_property_values
    WHERE r_instance_id=:r_instance_id
    """
)

_DELETE_RECTANGLE_INSTANCE = text(
    """
    DELETE FROM rectangle_instances 
    WHERE r_instance_id=:r_instance_id
    """
)

def delete_rectangle_instance_values(connection, rectangle_instance):
    connection.execute(
        _DELETE_RECTANGLE_INSTANCE_PROPERTY_VALUES,
        r_instance_id=rectangle_instance.id
    )

def delete_rectangle_instance(connection, rectangle_instance):
    delete_rectangle_instance_values(connection, rectangle_instance)

    connection.execute(
        _DELETE_RECTANGLE_INSTANCE,
        r_instance_id=rectangle_instance.id
    )

def map_to_property_value(connection, rectangle_instance, property_value):
    connection.execute(
        _MAP_TO_PROPERTY_VALUE,
        r_instance_id=rectangle_instance.id,
        property_id=hash(property_value)
    )

def unmap_from_property_value(connection, rectangle_instance, property_value):
    connection.execute(
        _UNMAP_FROM_PROPERTY_VALUE,
        r_instance_id=rectangle_instance.id,
        property_id=hash(property_value)
    )

def get_property_value(connection, rectangle_instance, property_):
    row = connection.execute(
        _GET_PROPERTY_VALUE,
        r_instance_id=rectangle_instance.id,
        property_type=property_.property_type,
        property_name=property_.property_name
    ).first()

    if row:
        return properties.PropertyValue(property_, row['property_value'])

    return properties.PropertyValue(property_, None)

def count_mapped_instances(connection, property_value):
    counter = 0

    for _ in connection.execute(
        _GET_INSTANCES_WITH_PROPERTY_VALUE,
        property_id=hash(property_value)):
        counter += 1

    return counter

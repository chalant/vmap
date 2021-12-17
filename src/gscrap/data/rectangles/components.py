from sqlalchemy import text

_DELETE_COMPONENTS_OF_INSTANCE = text(
    """
    DELETE FROM rectangle_components
    WHERE r_instance_id=:instance_id
    """
)

_DELETE_COMPONENT = text(
    """
    DELETE FROM rectangle_components
    WHERE r_instance_id=:instance_id 
        AND r_component_id=:component_id
    """
)

def delete_components_of_instance(connection, instance_id):
    connection.execute(
        _DELETE_COMPONENTS_OF_INSTANCE,
        instance_id=instance_id
    )

def delete_component(connection, instance_id, component_id):
    connection.execute(
        _DELETE_COMPONENT,
        instance_id=instance_id,
        component_id=component_id
    )
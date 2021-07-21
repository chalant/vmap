from sqlalchemy import text

UNIQUE = 0
INCREMENTAL = 1
RANDOM = 2

_ADD_ATTRIBUTE = text(
    """
    INSERT INTO attributes(attribute_name)
    VALUES (:attribute_name)
    """
)

def add_attribute(connection, attribute_name):
    connection.execute(
        _ADD_ATTRIBUTE,
        attribute_name=attribute_name)
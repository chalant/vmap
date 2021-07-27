from sqlalchemy import text

DISTINCT = 0
#scope of property
GLOBAL = 1 #values are applied accross all elements with the label
LOCAL = 2 #values are limited to instances of the rectangle

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
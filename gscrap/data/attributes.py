from sqlalchemy import text

DISTINCT = 0
INCREMENTAL = 1
RANDOM = 2
SHARED = 3

#scope of property
LABEL = 4 #values are applied accross all elements with the label
RECTANGLE = 5 #values are limited to instances of the rectangle

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
from sqlalchemy import text

from gscrap.data.rectangles import rectangles

_GET_RECTANGLES = text(
    """
    SELECT * FROM rectangles
    INNER JOIN rectangle_labels ON rectangle_labels.rectangle_id = rectangles.rectangle_id
    INNER JOIN label_properties ON label_properties.label_type = rectangle_labels.label_type 
        AND label_properties.label_name = rectangle_labels.label_name
    WHERE property_type=:property_type AND property_name=:property_name
    """
)

def get_rectangles_of_property(connection, property_):
    for res in connection.execute(
        _GET_RECTANGLES,
        property_type=property_.property_type,
        property_name=property_.property_name):

        yield rectangles.Rectangle(
            res["rectangle_id"],
            res["project_name"],
            res["width"],
            res["height"])
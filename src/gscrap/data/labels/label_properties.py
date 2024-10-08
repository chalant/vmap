from sqlalchemy import text

from gscrap.data.labels import labels
from gscrap.data.properties import properties

_GET_LABELS_PROPERTIES = text(
    """
    SELECT * FROM labels
    INNER JOIN label_properties 
        ON label_properties.label_type=labels.label_type 
        AND label_properties.label_name=labels.label_name
    """
)

_GET_LABELS_WITH_PROPERTY = text(
    """
    SELECT * FROM labels
    INNER JOIN label_properties 
        ON label_properties.label_type=labels.label_type 
        AND label_properties.label_name=labels.label_name
    WHERE label_properties.property_type=:property_type 
        AND label_properties.property_name=:property_name
    """
)

class LabelProperties(object):
    __slots__ = ['label', 'property_']

    def __init__(self, label, property_):
        self.label = label
        self.property_ = property_

    def __hash__(self):
        return hash((self.label, self.property_))

    def __eq__(self, other):
        return other.label == self.label and \
               other.property == self.property_


def get_labels_properties(connection):
    for res in connection.execute(
        _GET_LABELS_PROPERTIES):

        yield LabelProperties(
            labels.Label(res['label_type'], res['label_name']),
            properties.Property(res['property_type'], res['property_name'])
        )

def get_labels_of_property(connection, property_):
    for res in connection.execute(
        _GET_LABELS_WITH_PROPERTY,
        property_type=property_.property_type,
        property_name=property_.property_name):

        yield LabelProperties(
            labels.Label(res['label_type'], res['label_name']),
            properties.Property(res['property_type'], res['property_name'])
        )
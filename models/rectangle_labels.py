from sqlalchemy import text

_GET_RECTANGLE_LABELS = text(
    """
    SELECT * FROM rectangle_labels
    INNER JOIN labels ON 
        rectangle_labels.label_name = labels.label_name AND 
        rectangle_labels.label_type = labels.label_type  
    WHERE rectangle_id=:rectangle_id
    """
)

_ADD_LABEL = text(
    """
    INSERT OR REPLACE INTO rectangle_labels (rectangle_id, label_name, label_type)
    VALUES (:rectangle_id, :label_name, :label_type)
    """
)

_REMOVE_LABEL = text(
    """
    DELETE FROM rectangle_labels
    WHERE rectangle_id=:rectangle_id 
        AND label_type=:label_type 
        AND label_name=:label_name
    """
)

_REMOVE_LABELS = text(
    """
    DELETE FROM rectangle_labels
    WHERE rectangle_id=:rectangle_id
    """
)

class RectangleLabel(object):
    __slots__ = [
        'classifiable',
        'capture',
        'label_type',
        'label_name',
        '_rectangle'
    ]

    def __init__(self, label, rectangle):
        self.classifiable = label["classifiable"]
        self.capture = label["capture"]
        self.label_type = label["label_type"]
        self.label_name = label["label_name"]
        self._rectangle = rectangle

    def delete(self, connection):
        connection.execute(
            _REMOVE_LABEL,
            rectangle_id=self._rectangle.id,
            label_type=self.label_type,
            label_name=self.label_name,
        )

class RectangleLabels(object):
    def __init__(self, rectangle):
        """

        Parameters
        ----------
        rectangle: models.rectangles.Rectangle
        """
        self._rectangle = rectangle
        self._new_labels = []

    def get_labels(self, connection):
        for label in connection.execute(
                _GET_RECTANGLE_LABELS,
                rectangle_id=self._rectangle.id):
            yield RectangleLabel(label, self._rectangle)

    def add_label(self, label_name, label_type):
        self._new_labels.append((label_name, label_type))

    def submit(self, connection):
        id_ = self._rectangle.id

        for lb, lt in self._new_labels:
            connection.execute(
                _ADD_LABEL,
                rectangle_id=id_,
                label_name=lb,
                label_type=lt
            )

    def delete(self, connection):
        connection.execute(
            _REMOVE_LABELS,
            rectangle_id=self._rectangle.id
        )
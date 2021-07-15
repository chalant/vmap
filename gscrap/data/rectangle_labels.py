from collections import defaultdict

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
        'rectangle_id'
    ]

    def __init__(self, label, rectangle_id):
        self.classifiable = label["classifiable"]
        self.capture = label["capture"]
        self.label_type = label["label_type"]
        self.label_name = label["label_name"]
        self.rectangle_id = rectangle_id

    def delete(self, connection):
        connection.execute(
            _REMOVE_LABEL,
            rectangle_id=self.rectangle_id,
            label_type=self.label_type,
            label_name=self.label_name,
        )

    def __hash__(self):
        return hash((self.label_type, self.label_name))

    def __eq__(self, other):
        return other.label_type == self.label_type \
               and other.label_name == self.label_name


class UnsavedRectangleLabel(object):
    __slots__ = ['label_type', 'label_name', '_labels']

    def __init__(self, label_type, label_name, labels):
        self.label_type = label_type
        self.label_name = label_name
        self._labels = labels

    def delete(self, connection):
        names = self._labels[self.label_type]
        names.pop(names.index(self.label_name))

    def __hash__(self):
        return hash((self.label_type, self.label_name))

    def __eq__(self, other):
        return other.label_type == self.label_type \
               and other.label_name == self.label_name

class RectangleLabels(object):
    def __init__(self, rectangle_id):
        """

        Parameters
        ----------
        rectangle: models.rectangles.Rectangle
        """
        self._rectangle_id = rectangle_id
        self._new_labels = defaultdict(list)

    def get_labels(self, connection):
        rectangle_id = self._rectangle_id
        for label in connection.execute(
                _GET_RECTANGLE_LABELS,
                rectangle_id=rectangle_id):
            yield RectangleLabel(label, rectangle_id)

    def get_unsaved_labels(self):
        new_labels = self._new_labels
        for lt, labels in new_labels.items():
            for ln in labels:
                yield UnsavedRectangleLabel(lt, ln, new_labels)


    def add_label(self, label_name, label_type):
        new_labels = self._new_labels
        new_labels[label_type].append(label_name)

        return UnsavedRectangleLabel(label_type, label_name, new_labels)

    def submit(self, connection):
        id_ = self._rectangle_id
        new_labels = self._new_labels

        for lt, labels in new_labels.items():
            for lb in labels:
                connection.execute(
                    _ADD_LABEL,
                    rectangle_id=id_,
                    label_name=lb,
                    label_type=lt
                )

        new_labels.clear()

    def delete(self, connection):
        connection.execute(
            _REMOVE_LABELS,
            rectangle_id=self._rectangle_id
        )

def delete_rectangle_labels(connection, rectangle_id):
    connection.execute(
        _REMOVE_LABELS,
        rectangle_id=rectangle_id
    )

def get_labels(connection, rectangle_id):
    for row in connection.execute(_GET_RECTANGLE_LABELS, rectangle_id=rectangle_id):
        yield RectangleLabel(row, rectangle_id)
from collections import defaultdict

from sqlalchemy import text

from gscrap.utils import key_generator

_GET_RECTANGLE_LABELS = text(
    """
    SELECT * FROM rectangle_labels
    INNER JOIN labels ON 
        rectangle_labels.label_name = labels.label_name AND 
        rectangle_labels.label_type = labels.label_type  
    WHERE rectangle_id=:rectangle_id
    """
)

_GET_ALL_RECTANGLES_LABELS = text(
    """
    SELECT * FROM rectangle_labels
    """
)

_ADD_LABEL = text(
    """
    INSERT OR REPLACE INTO rectangle_labels (rectangle_id, label_name, label_type)
    VALUES (:rectangle_id, :label_name, :label_type)
    """
)

_DELETE_RECTANGLE_LABELS = text(
    """
    DELETE FROM rectangle_labels
    WHERE rectangle_id=:rectangle_id
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
        'label',
        'rectangle'
    ]

    def __init__(self, label, rectangle):
        self.label = label
        self.rectangle = rectangle

    @property
    def classifiable(self):
        return self.label["classifiable"]

    @property
    def capture(self):
        return self.label["capture"]

    @property
    def label_type(self):
        return self.label["label_type"]

    @property
    def label_name(self):
        return self.label["label_name"]

    @property
    def rectangle_id(self):
        return self.rectangle.id

    def delete(self, connection):
        connection.execute(
            _REMOVE_LABEL,
            rectangle_id=self.rectangle_id,
            label_type=self.label_type,
            label_name=self.label_name,
        )

    def __hash__(self):
        return key_generator.generate_key(self.label_type + self.label_name)

    def __eq__(self, other):
        return other._label_type == self.label_type and \
               other.label_name == self.label_name


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
        return key_generator.generate_key(self.label_type + self.label_name)

    def __eq__(self, other):
        return other._label_type == self.label_type \
               and other.label_name == self.label_name


class RectangleLabels(object):
    def __init__(self, rectangle):
        """

        Parameters
        ----------
        rectangle: models.rectangles.Rectangle
        """
        self._rectangle = rectangle
        self._new_labels = defaultdict(list)

    def get_labels(self, connection):
        rectangle = self._rectangle
        for label in connection.execute(
                _GET_RECTANGLE_LABELS,
                rectangle_id=rectangle.id):
            yield RectangleLabel(label, rectangle)

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
        id_ = self._rectangle.id
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
            rectangle_id=self._rectangle.id
        )


def delete_all_rectangle_labels(connection, rectangle):
    connection.execute(
        _REMOVE_LABELS,
        rectangle_id=rectangle.id
    )


def delete_rectangle_label(connection, rectangle_label):
    rectangle_label.delete(connection)


def get_rectangle_labels(connection, rectangle):
    for row in connection.execute(_GET_RECTANGLE_LABELS, rectangle_id=rectangle.id):
        yield RectangleLabel(row, rectangle)

def get_all_rectangles_labels(connection):
    for row in connection.execute(_GET_ALL_RECTANGLES_LABELS):
        yield row

def delete_labels_by_rectangle_id(connection, rectangle_id):
    connection.execute(
        _DELETE_RECTANGLE_LABELS,
        rectangle_id=rectangle_id
    )

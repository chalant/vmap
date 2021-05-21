import os
from os import path

from PIL import Image

from sqlalchemy import text

from gscrap.data import paths

_GET_IMAGE = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name AND label_name=:label_name AND label_type=:label_type
    ORDER BY position ASC
    """
)

_ADD_IMAGE_METADATA = text(
    """
    INSERT OR REPLACE INTO images(image_id, project_name, label_instance_name, label_type, label_name, hash_key, position)
    VALUES (:image_id, :project_name, :label_instance_name, :label_type, :label_name, :hash_key, :position)
    """
)

_DELETE_IMAGE_METADATA = text(
    """
    DELETE FROM images
    WHERE image_id=:image_id AND project_name=:project_name
    """
)

_DELETE_ALL_PROJECT_IMAGES = text(
    """
    DELETE FROM images
    WHERE project_name=:project_name
    """
)

class ImageMetadata(object):
    __slots__ = ['_id', '_project_name', '_rectangle', '_hash_key', '_position', '_label', '_image']

    def __init__(
            self,
            id_,
            project_name,
            rectangle,
            hash_key,
            position,
            label):

        self._id = id_
        self._project_name = project_name
        self._rectangle = rectangle
        self._hash_key = hash_key
        self._position = position
        self._label = label

    @property
    def height(self):
        return self._rectangle.height

    @property
    def width(self):
        return self._rectangle.width

    @property
    def hash_key(self):
        return self._hash_key

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def id(self):
        return self._id

    @property
    def path(self):
        return path.join(paths.images(), self._id)

    @property
    def label(self):
        return self._label

    @property
    def rectangle(self):
        return self._rectangle

    def get_image(self):
        return Image.open(self.path, formats=("PNG",))

    def submit(self, connection):
        label = self._label
        connection.execute(
            _ADD_IMAGE_METADATA,
            image_id=self._id,
            project_name=self._project_name,
            label_type=label["label_type"],
            label_name=label["label_name"],
            label_instance_name=label["instance_name"],
            hash_key=self._hash_key,
            position=self._position)

    def delete_image(self, connection):
        connection.execute(
            _DELETE_IMAGE_METADATA,
            image_id=self._id,
            project_name=self._project_name
        )

        try:
            #remove image from disk
            os.remove(self.path)
        except FileNotFoundError:
            pass

def delete_for_project(connection, project_name):
    connection.execute(
        _DELETE_ALL_PROJECT_IMAGES,
        project_name=project_name
    )
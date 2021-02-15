from os import path

from PIL import Image, ImageTk

from sqlalchemy import text

from data import paths

_ADD_IMAGE_METADATA = text(
    """
    INSERT OR REPLACE INTO images(image_id, project_name, label_instance_name, r_instance_id, hash_key, position)
    VALUES (:image_id, :project_name, :label_instance_name, :r_instance_id, :hash_key, :position)
    """
)

class ImageMetadata(object):
    __slots__ = ['_id', '_project_name', '_r_instance_id', '_hash_key', '_position', '_label_instance_name']

    def __init__(
            self,
            id_,
            project_name,
            r_instance_id,
            hash_key,
            position,
            label_instance_name="n/a"):
        self._id = id_
        self._project_name = project_name
        self._r_instance_id = r_instance_id
        self._hash_key = hash_key
        self._position = position
        self._label_instance_name = label_instance_name

    @property
    def hash_key(self):
        return self._hash_key

    @property
    def position(self):
        return self._position

    @property
    def id(self):
        return self._id

    @property
    def path(self):
        return path.join(paths.images(), self._id)

    @property
    def label_instance_name(self):
        return self._label_instance_name

    @label_instance_name.setter
    def label_instance_name(self, value):
        self._label_instance_name = value

    def get_image(self):
        return ImageTk.PhotoImage(Image.open(self.path, formats=("PNG",)))

    def submit(self, connection):
        connection.execute(
            _ADD_IMAGE_METADATA,
            image_id=self._id,
            project_name=self._project_name,
            label_instance_name=self._label_instance_name,
            r_instance_id=self._r_instance_id,
            hash_key=self._hash_key,
            position=self._position)

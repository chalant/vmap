import os
from os import path

from PIL import Image

from uuid import uuid4

from sqlalchemy import text

from gscrap.data import paths

_GET_IMAGES = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name 
        AND label_name=:label_name 
        AND label_type=:label_type
    """
)

_GET_IMAGE = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name 
        AND label_name=:label_name 
        AND label_type=:label_type 
        AND label_instance_name=:label_instance_name
    """
)

_ADD_IMAGE_METADATA = text(
    """
    INSERT OR REPLACE INTO images(image_id, project_name, label_instance_name, label_type, label_name, width, height)
    VALUES (:image_id, :project_name, :label_instance_name, :label_type, :label_name, :width, :height)
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
    __slots__ = [
        '_id',
        '_project_name',
        '_label',
        '_image',
        '_width',
        '_height']

    def __init__(
            self,
            id_,
            project_name,
            label,
            width,
            height):

        self._id = id_
        self._project_name = project_name
        self._label = label
        self._height = height
        self._width = width

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def id(self):
        return self._id

    @property
    def path(self):
        return path.join(paths.images(), self._id)

    @property
    def label(self):
        return self._label

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
            width=self._width,
            height=self._height
        )

    def delete_image(self, connection):
        connection.execute(
            _DELETE_IMAGE_METADATA,
            image_id=self._id,
            project_name=self._project_name)

        try:
            #remove image from disk
            os.remove(self.path)
        except FileNotFoundError:
            pass

def delete_for_project(connection, project_name):
    connection.execute(
        _DELETE_ALL_PROJECT_IMAGES,
        project_name=project_name)

def get_images(
        connection,
        project_name,
        label_type,
        label_name):

    for im in connection.execute(
            _GET_IMAGES,
        project_name=project_name,
        label_type=label_type,
        label_name=label_name):

        yield ImageMetadata(
            im["image_id"],
            im["project_name"],
            {'label_name': label_name,
             'label_type': label_type,
             'instance_name': im["label_instance_name"]},
            im["width"],
            im["height"])

def create_image_metadata(
        project_name,
        label_name,
        label_type,
        instance_name,
        width,
        height):
    return ImageMetadata(
        uuid4().hex,
        project_name,
        {
            'label_name': label_name,
            'label_type': label_type,
            'instance_name': instance_name
        },
        width,
        height
    )

def get_image(connection, project_name, label):
    res = connection.execute(
        _GET_IMAGE,
        project_name=project_name,
        label_type=label['label_type'],
        label_name=label['label_class'],
        label_instance_name=label['instance_name']).first()

    return ImageMetadata(
        res['image_id'],
        res['project_name'],
        {'label_name': res['label_name'],
         'label_type': res['label_type'],
         'instance_name': res['label_instance_name']
         },
        res['width'],
        res['height']
    )
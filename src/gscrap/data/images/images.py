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
    WHERE label_name=:label_name AND label_type=:label_type
    """
)

_GET_IMAGE = text(
    """
    SELECT *
    FROM images
    WHERE label_name=:label_name 
        AND label_type=:label_type 
        AND label_instance_name=:label_instance_name
    """
)

_ADD_IMAGE_METADATA = text(
    """
    INSERT OR REPLACE 
    INTO images(image_id, label_instance_name, label_type, label_name, width, height, rectangle_id)
    VALUES (:image_id, :label_instance_name, :label_type, :label_name, :width, :height, :rectangle_id)
    """
)

_DELETE_IMAGE_METADATA = text(
    """
    DELETE FROM images
    WHERE image_id=:image_id
    """
)

_DELETE_ALL_SCENE_IMAGES = text(
    """
    DELETE FROM images
    """
)

class ImageMetadata(object):
    __slots__ = [
        '_id',
        '_scene',
        '_label',
        '_image',
        '_width',
        '_height',
        '_rectangle_id'
    ]

    def __init__(
            self,
            id_,
            scene,
            label,
            width,
            height,
            rectangle_id):

        self._id = id_
        self._scene = scene
        self._label = label
        self._height = height
        self._width = width
        self._rectangle_id = rectangle_id

    @property
    def rectangle_id(self):
        return self._rectangle_id

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
        return path.join(self._scene.path, 'images', self._id)

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
            scene_name=self._scene.name,
            label_type=label["label_type"],
            label_name=label["label_name"],
            label_instance_name=label["instance_name"],
            width=self._width,
            height=self._height,
            rectangle_id=self._rectangle_id)

    def delete_image(self, connection):
        connection.execute(
            _DELETE_IMAGE_METADATA,
            image_id=self._id)

        try:
            #remove image from disk
            os.remove(self.path)
        except FileNotFoundError:
            pass

def delete_for_scene(connection, project_name):
    connection.execute(
        _DELETE_ALL_SCENE_IMAGES,
        project_name=project_name)

def get_images(
        connection,
        scene,
        label_type,
        label_name):

    for im in connection.execute(
            _GET_IMAGES,
        label_type=label_type,
        label_name=label_name):

        yield ImageMetadata(
            im["image_id"],
            scene,
            {'label_name': label_name,
             'label_type': label_type,
             'instance_name': im["label_instance_name"]},
            im["width"],
            im["height"],
            im['rectangle_id']
        )

def create_image_metadata(
        scene,
        label_name,
        label_type,
        instance_name,
        width,
        height,
        rectangle_id):
    return ImageMetadata(
        uuid4().hex,
        scene,
        {
            'label_name': label_name,
            'label_type': label_type,
            'instance_name': instance_name
        },
        width,
        height,
        rectangle_id)

def get_image(connection, scene, label):
    res = connection.execute(
        _GET_IMAGE,
        label_type=label['label_type'],
        label_name=label['label_class'],
        label_instance_name=label['instance_name']).first()

    return ImageMetadata(
        res['image_id'],
        scene,
        {'label_name': res['label_name'],
         'label_type': res['label_type'],
         'instance_name': res['label_instance_name']
         },
        res['width'],
        res['height'],
        res['rectangle_id']
    )
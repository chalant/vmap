import os
from os import path

from functools import partial

from PIL import Image

from sqlalchemy import text

from gscrap.data import io
from gscrap.data.images import images as img
from gscrap.data.rectangles import rectangles
from gscrap.data.labels import labels

_DELETE_SCENE = text(
    """
    DELETE FROM scenes
    WHERE scene_name=:scene_name
    """
)

_ADD_SCENE = text(
    """
    INSERT INTO scenes(scene_name)
    VALUES (:scene_name)
    """
)

_ADD_SCENE_SIZE = text(
    """
    INSERT INTO scenes_sizes(scene_name, height, width)
    VALUES (:scene_name, :height, :width)
    """
)

_GET_SCENES = text(
    """
    SELECT *
    FROM scenes
    """
)

_GET_SCENE = text(
    """
    SELECT *
    FROM scenes
    WHERE scene_name=:scene_name;
    """
)

_GET_SCENE_SIZE = text(
    """
    SELECT *
    FROM scenes_sizes
    WHERE scene_name=:scene_name
    """
)

_GET_IMAGE_PATHS = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name AND r_instance_id=:r_instance_id
    """
)

class SceneWriter(object):
    def __init__(self, name):
        self.parent_type = None
        self._name = name
        self._labels = []

        self._submit_flag = False

    @property
    def name(self):
        return self._name

    def add_label(self, name, type_, max_=None, capture=False, classifiable=False):
        lbl = labels.LabelWriter(self._name, labels.Label(type_, name), max_, capture, classifiable)
        self._labels.append(lbl)
        return lbl

    def _submit(self, connection):
        if not self._submit_flag:
            labels = self._labels

            name = self._name

            connection.execute(
                _ADD_SCENE,
                scene_name=name)

            for lbl in labels:
                lbl._submit(connection)

            labels.clear()

            self._submit_flag = True

class Scene(object):
    def __init__(self, name, height, width):
        self.name = name
        self.height = height
        self.width = width

        self._template_path = None

    def save(self, connection):
        connection.execute(
            _ADD_SCENE_SIZE,
            scene_name=self.name,
            width=self.width,
            height=self.height)

    def get_label(self, connection, label_name):
        return labels.get_label(connection, self.name, label_name)

    def get_image_metadata(self, connection, instance_id):
        for element in connection.execute(
                _GET_IMAGE_PATHS,
                project_name=self.name,
                r_instance_id=instance_id):
            yield element

    def store_template(self, image):
        io.execute(partial(self._store_template, image=image))

    def load_template(self, callback, on_error):
        io.execute(partial(self._load_image, callback=callback, on_error=on_error))

    def template_update(self, callback):
        self._template_callback = callback

    def delete(self, connection):

        name = self.name

        connection.execute(
            _DELETE_SCENE,
            project_name=name)

        #delete all elements related to the project
        img.delete_for_project(connection, name)
        rectangles.delete_for_scene(connection, name)

        io.execute(self._delete_template)

    def _delete_template(self):
        tp = self._template_path

        if path.exists(tp):
            os.remove(tp)

    def _load_image(self, callback, on_error):
        try:
            # with open(self._template_path) as f:
            callback(Image.open(self._template_path, formats=("PNG",)))
        except FileNotFoundError as e:
            on_error(e)

    def _store_template(self, image):
        image.save(self._template_path, "PNG")
        self._template_callback(image)

def get_scene(connection, scene_name):
    res = connection.execute(
        _GET_SCENE_SIZE,
        scene_name=scene_name
    )

    return Scene(scene_name, res["height"], res["width"])





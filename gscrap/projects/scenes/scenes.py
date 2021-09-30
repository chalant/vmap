import os
from os import path

from functools import partial

from PIL import Image

from sqlalchemy import text, exc, engine, MetaData

from gscrap.projects.scenes import schema

from gscrap.data import io
from gscrap.data import paths

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

_GET_LABEL_INSTANCES = text(
    """
    SELECT *
    FROM label_instances
    WHERE label_name=:label_name AND label_type=:label_type
    """
)

_GET_LABEL_TYPES = text(
    """
    SELECT *
    FROM label_types
    """
)

_GET_PROJECT_TYPE = text(
    """
    SELECT * 
    FROM project_types
    WHERE project_type = :project_type;
    """
)

_GET_PROJECT_TYPE_COMPONENTS = text(
    """
    SELECT *
    FROM project_types
    INNER JOIN project_type_components 
        ON project_type_components.project_type = project_types.project_type
    WHERE project_types.project_type=:project_type;
    """
)

_GET_LABEL = text(
    """
    SELECT *
    FROM labels
    WHERE project_type=:project_type;
    """
)

_SCENES = {}

class SceneWriter(object):
    def __init__(self, name):
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

    def submit(self, connection):
        labels = self._labels

        name = self._name

        connection.execute(
            _ADD_SCENE,
            scene_name=name)

        for lbl in labels:
            lbl._submit(connection)

        labels.clear()

class SceneDimensions(object):
    def __init__(self, scene, height=None, width=None):
        self.height = height
        self.width = width
        self._scene = scene

    def save(self, connection):
        width = self.width
        height = self.height

        if width and height:
            connection.execute(
                _ADD_SCENE_SIZE,
                scene_name=self._scene.name,
                width=self.width,
                height=self.height)


class _Scene(object):
    def __init__(self, project, name):
        self.project = project
        self.name = name

        self._template_path = paths.templates()

        self._dimensions = None

        self._engine = engine.create_engine(
            "sqlite:////{}".format(path.join(
                self.project.working_dir,
                "",
                "data.db")))

        def null_callback(data):
            pass

        self._update_callback = null_callback
        self._template_callback = null_callback

    def set_dimensions(self, dimensions):
        self._dimensions = dimensions

    @property
    def width(self):
        return self._dimensions.width

    @width.setter
    def width(self, value):
        self._dimensions.width = value

    @property
    def height(self):
        return self._dimensions.height

    @height.setter
    def height(self, value):
        self._dimensions.height = value

    @property
    def path(self):
        return path.join(self.project.working_dir, '')

    def connect(self):
        return self._engine.connect()

    def save(self, connection):
        self._dimensions.save(connection)

    def get_label(self, connection, label_name):
        return labels.get_label(connection, self.name, label_name)

    def get_label_instances(self, connection, label_name, label_type):
        for element in connection.execute(
                _GET_LABEL_INSTANCES,
                label_name=label_name,
                label_type=label_type):
            yield element

    def get_label_types(self, connection):
        for row in connection.execute(_GET_LABEL_TYPES):
            yield row["label_type"]

    def get_labels_of_type(self, connection, label_type):
        for element in self._get_labels(connection, self.name, label_type):
            yield element

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
        img.delete_for_scene(connection, name)
        rectangles.delete_for_scene(connection, name)

        io.execute(self._delete_template)

    def get_rectangles(self, connection):
        return rectangles.get_rectangles(connection, self.name)

    def create_rectangle(self, width, height):
        return rectangles.create_rectangle(width, height, self.name)

    def _get_labels(self, connection, project_type, label_type):
        row = connection.execute(_GET_PROJECT_TYPE, project_type=project_type).fetchone()

        parent = row["parent_project_type"]

        for lt in connection.execute(_GET_LABEL, project_type=project_type):
            if lt["label_type"] == label_type:
                yield lt

        for cmp in connection.execute(_GET_PROJECT_TYPE_COMPONENTS, project_type=project_type):
            for element in self._get_labels(connection, cmp["component_project_type"], label_type):
                yield element

        while parent != None:
            for element in self._get_labels(connection, parent, label_type):
                yield element

            parent = connection.execute(_GET_PROJECT_TYPE, project_type=parent).fetchone()["parent_project_type"]

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

def create_tables(scene):
    meta = MetaData()
    schema.build_schema(meta)
    meta.create_all(scene._engine)

def get_scene(project, scene_name):
    if scene_name not in _SCENES:
        _SCENES[scene_name] = scene = _Scene(scene_name, project)
        return scene
    else:
        return _SCENES[scene_name]

def get_scene_dimensions(connection, scene):
    res = connection.execute(
        _GET_SCENE_SIZE,
        scene_name=scene.name
    )

    return SceneDimensions(scene, res["height"], res["width"])

def get_scene_names(connection):
    try:
        for res in connection.execute(_GET_SCENES):
            yield res["scene_name"]
    except exc.OperationalError:
        return []

def connect(scene):
    return scene.connect()




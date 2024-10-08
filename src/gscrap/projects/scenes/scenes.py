import os
from functools import partial
from os import path

from PIL import Image
from sqlalchemy import text, exc, engine, MetaData

from gscrap.data import io
from gscrap.data.images import images as img
from gscrap.data.labels import labels
from gscrap.data.rectangles import rectangles
from gscrap.data.rectangles import components
from gscrap.data.rectangles import rectangle_labels

from gscrap.projects.scenes import schema

_DELETE_SCENE = text(
    """
    DELETE FROM scenes
    WHERE scene_name=:scene_name
    """
)

_ADD_SCENE = text(
    """
    INSERT OR IGNORE INTO scenes(scene_name)
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
    """
)

_SCENES = {}

class SceneWriter(object):
    def __init__(self, scene):
        self._name = scene.name
        self._labels = []

        self._submit_flag = False

    @property
    def name(self):
        return self._name

    def add_label(self, name, type_, max_=None, capture=False, classifiable=False):
        lbl = labels.LabelWriter(self._name, labels.Label(type_.name, name), max_, capture, classifiable)
        self._labels.append(lbl)
        return lbl

    def submit(self, connection):
        labels = self._labels

        name = self._name

        connection.execute(
            _ADD_SCENE,
            scene_name=name)

        for lbl in labels:
            lbl.submit(connection)

        labels.clear()

class SceneDimensions(object):
    def __init__(self, scene, height=0, width=0):
        self.height = height
        self.width = width
        self._scene = scene

        scene.set_dimensions(self)

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

        self._template_path = path.join(
            project.working_dir,
            'scenes',
            name,
            'template')

        self._dimensions = None

        self._engine = engine.create_engine(
            "sqlite:////{}".format(path.join(
                self.project.working_dir,
                "scenes",
                name,
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
        return path.join(self.project.working_dir, 'scenes', self.name)

    def connect(self):
        return self._engine.connect()

    def save(self, connection):
        self._dimensions.save(connection)

    def get_label(self, connection, label_type, label_name):
        return labels.get_label(
            connection,
            label_type,
            label_name,
            self.name)

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
        return rectangles.get_rectangles(connection, self)

    def create_rectangle(self, width, height):
        return rectangles.create_rectangle(width, height, self)

    def _get_labels(self, connection, project_type, label_type):
        # row = connection.execute(_GET_PROJECT_TYPE, project_type=project_type).fetchone()
        #
        # parent = row["parent_project_type"]

        for lt in connection.execute(_GET_LABEL):
            if lt["label_type"] == label_type:
                yield lt

        # for cmp in connection.execute(_GET_PROJECT_TYPE_COMPONENTS, project_type=project_type):
        #     for element in self._get_labels(connection, cmp["component_project_type"], label_type):
        #         yield element

        # while parent != None:
        #     for element in self._get_labels(connection, parent, label_type):
        #         yield element
        #
        #     parent = connection.execute(_GET_PROJECT_TYPE, project_type=parent).fetchone()["parent_project_type"]

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

        self.width = image.width()
        self.height = image.height()

def cleanup(connection, scene):
    #todo: this is a temporary fix for removing junk data...
    # normally this data should not exist.

    rct_array = []
    rct_lbl = []
    instances = []
    comp_instances = []

    # remove rectangles with no instances.

    for rct in rectangles.get_rectangles(connection, scene):
        count = 0
        for instance in rct.get_instances(connection):
            count += 1

            instances.append(instance.id)

        if count == 0:
            rectangles.delete_rectangle(connection, rct)

        rct_array.append(rct.id)

    for lbl in rectangle_labels.get_all_rectangles_labels(connection):
        rct_lbl.append(lbl["rectangle_id"])

    for rb in set(rct_lbl) - set(rct_array):
        rectangle_labels.delete_labels_by_rectangle_id(connection, rb)
        print("Deleting", rb)

    for cmp in rectangles.get_all_instances_components(connection):
        comp_instances.append(cmp["r_instance_id"])

    #remove instances that do not exist
    for instance_id in set(comp_instances) - set(instances):
        components.delete_components_of_instance(connection, instance_id)
        print("Deleting", instance_id)


def create_tables(scene):
    meta = MetaData()
    schema.build_schema(meta)
    meta.create_all(scene._engine)

def get_scene(project, scene_name):
    if scene_name not in _SCENES:
        _SCENES[scene_name] = scene = _Scene(project, scene_name)
        return scene
    else:
        return _SCENES[scene_name]

def load_dimensions(connection, scene):
    res = connection.execute(
        _GET_SCENE_SIZE,
        scene_name=scene.name
    ).first()

    if res:
        SceneDimensions(scene, res["height"], res["width"])
    else:
        SceneDimensions(scene)

def set_dimensions(connection, scene, width, height):
    SceneDimensions(scene, height, width).save(connection)

def get_scene_names(connection):
    try:
        for res in connection.execute(_GET_SCENES):
            yield res["scene_name"]
    except exc.OperationalError:
        return []

def connect(scene):
    return scene.connect()




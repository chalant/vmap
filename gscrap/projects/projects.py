from os import path, listdir, mkdir

from sqlalchemy import text, engine, MetaData

from gscrap.projects.scenes import scenes
from gscrap.projects import schema

from gscrap.data import builder
from gscrap.data.images import videos as vds

_GET_LEAF_PROJECT_TYPES = text(
    """
    SELECT * 
    FROM project_types
    WHERE has_child=0;
    """
)

_DELETE_PROJECT = text(
    """
    DELETE FROM projects
    WHERE project_name=:project_name
    """
)

_ADD_PROJECT = text(
    """
    INSERT OR REPLACE INTO projects(project_type, project_name, height, width)
    VALUES (:project_type, :project_name, :height, :width);
    """
)

_GET_PROJECTS = text(
    """
    SELECT *
    FROM projects
    """
)

_GET_PROJECT = text(
    """
    SELECT *
    FROM projects
    WHERE project_name=:project_name;
    """
)

_GET_LABEL = text(
    """
    SELECT *
    FROM labels
    WHERE project_type=:project_type;
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

_GET_LABEL_INSTANCES = text(
    """
    SELECT *
    FROM label_instances
    WHERE label_name=:label_name AND label_type=:label_type
    """
)

_GET_IMAGE_PATHS = text(
    """
    SELECT *
    FROM images
    WHERE project_name=:project_name AND r_instance_id=:r_instance_id
    """
)

_ADD_IMAGE = text(
    """
    INSERT INTO images(image_id, project_name, label_instance_id, r_instance_id, hash_key, position)
    VALUES (:image_id, :project_name, :label_instance_id, :r_instance_id, :hash_key, :position)
    """
)

_GET_SCENE = text(
    """
    SELECT * FROM project_scenes
    WHERE scene_name=:scene_name
    """
)

_PROJECT = None

def set_project(working_directory):
    global _PROJECT

    if not _PROJECT:
        _PROJECT = Project(working_directory)

def get_project():
    global _PROJECT

    if not _PROJECT:
        raise RuntimeError("Project was not set")

    return _PROJECT

def connect():
    return _PROJECT.connect()

def make_directory(path):
    try:
        mkdir(path)
    except FileExistsError:
        pass

class Project(object):
    _instance = None

    def __init__(self, working_directory):
        self.working_dir = working_directory
        self.namespace = {}

        self._scenes = {}

        self._update = False

        self._engine = eng = engine.create_engine(
            "sqlite:////{}".format(path.join(
                self.working_dir,
                "meta.db")))

        self._meta = meta = MetaData()

        schema.build_schema(meta)
        meta.create_all(eng)

    def connect(self):
        return self._engine.connect()

    def load_scene(self, scene_name):
        scene = scenes.get_scene(self, scene_name)

        #load scene and set dimensions.
        with scene.connect() as connection:
            scene = scenes.get_scene(self, scene_name)
            dimensions = scenes.get_scene_dimensions(connection, scene)
            scene.set_dimensions(dimensions)

            #rebuild label data in case label schema changed
            # todo: should use git to check for changes before rebuilding

            self._build_label_data(
                connection,
                scene,
                get_schema_name(connection, scene_name))

        return scene

    def create_scene(self, scene_name, schema_name):

        scene = scenes.get_scene(self, scene_name)
        pth = path.join(self.working_dir, 'scenes', scene_name)

        make_directory(pth)
        make_directory(path.join(pth, 'images'))

        with scene.connect() as connection:
            builder.clear(connection)
            scenes.create_tables(scene)

            self._build_label_data(connection, scene, schema_name)

        return scene

    def get_build_function(self, schema_name):
        schema_path = path.join(self.working_dir, 'schemas', schema_name + '.py')
        namespace = self.namespace

        with open(schema_path, 'r') as f:
            code = compile(f.read(), schema_path, 'exec')
            exec(code, namespace)

        return namespace.get('build')

    def _build_label_data(self, connection, scene, schema_name):
        with builder.build(connection, self, scene) as bld:
            self.get_build_function(schema_name)(bld)

    def get_scene_schemas(self):
        for element in listdir(path.join(self.working_dir, 'schemas')):
            if element.endswith(".py"):
                yield element.split(".")[0]

    def get_scene_names(self, connection):
        return scenes.get_scene_names(connection)

    def get_video_metadata(self, connection):
        vds.get_metadata(connection)

    def __new__(cls, working_directory):
        if cls._instance is None:
            ist = super().__new__(cls)
            cls._instance = ist
            return ist
        else:
            return cls._instance

def get_schema_name(connection, scene_name):
    return connection.execute(
        _GET_SCENE,
        scene_name=scene_name
    )['schema_name']
from os import path, listdir, mkdir

from sqlalchemy import text, engine, MetaData

from gscrap.projects.scenes import scenes
from gscrap.projects import schema

from gscrap.data import builder
from gscrap.data.images import videos as vds

_ADD_PROJECT = text(
    """
    INSERT OR REPLACE INTO projects(project_type, project_name, height, width)
    VALUES (:project_type, :project_name, :height, :width);
    """
)

_GET_SCENE = text(
    """
    SELECT * FROM project_scenes
    WHERE scene_name=:scene_name
    """
)

_GET_SCENES = text(
    """
    SELECT * FROM project_scenes
    """
)

_ADD_SCENE = text(
    """
    INSERT INTO project_scenes(scene_name, schema_name)
    VALUES (:scene_name, :schema_name)
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
            builder.clear(connection)
            scenes.create_tables(scene)

            scenes.load_dimensions(connection, scene)

            #rebuild label data in case label schema changed
            # todo: should use git (or check differences in file) to check for changes before rebuilding
            with self._engine.connect() as con:
                self._build_label_data(
                    connection,
                    scene,
                    get_schema_name(con, scene_name))

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

        with self._engine.connect() as connection:
            connection.execute(
                _ADD_SCENE,
                scene_name=scene_name,
                schema_name=schema_name
            )

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
        for res in connection.execute(_GET_SCENES):
            yield res['scene_name']

    def get_video_metadata(self, connection):
        return vds.get_metadata(connection)

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
        scene_name=scene_name).first()['schema_name']
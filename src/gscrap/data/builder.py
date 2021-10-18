from sqlalchemy import text

from gscrap.projects.scenes import scenes

from gscrap.data.project_types import _ProjectType
from gscrap.data.labels.labels import _LabelType
from gscrap.data.labels import labels

from gscrap.data import attributes

from gscrap.data.properties import properties
from gscrap.data.properties import value_source_factory as vsb
from gscrap.data.properties.values_sources import values_sources
from gscrap.data.properties import property_values_source as pvs

CLEAR_TABLE = '''
    DROP TABLE IF EXISTS {};
'''

def clear(connection):
    #clear tables
    table_names = [
        "project_types",
        "project_type_components",
        "labels",
        "label_components",
        "label_types",
        "label_instances",
        "properties",
        "property_names",
        "label_properties",
        "property_types",
        "property_attributes",
        "attributes",
        "incremental_value_generator",
        "values_input",
        "values_sources",
        "properties_values_sources",
        "values_sources_names",
        "values_sources_types"
    ]

    for name in table_names:
        connection.execute(text(CLEAR_TABLE.format(name)))

class _SceneLabels(object):
    def __init__(self, scene_name, connection):
        self._connection = connection
        self._scene_name = scene_name

    def get_label(self, label_type, label_name):
        return labels.get_label(
            self._connection,
            label_type,
            label_name,
            self._scene_name)

class _Builder(object):
    def __init__(self, connection, project, scene):
        """

        Parameters
        ----------
        project: gscrap.projects.projects.Project
        scene: gscrap.projects.scenes._Scene
        """
        self._project = project
        self._scene = scene

        self._connection = connection

        self._project_types = {}
        self._property_types = {}
        self._property_names = {}
        self._properties = {}

        self._label_types = {}
        self._labels = {}

        self._property_attributes = {}
        self._property_value_sources = {}

        self._values_sources = []

        self._scene_writer = scenes.SceneWriter(scene)

    def __enter__(self):
        # clear(self._connection)
        connection = self._connection

        self._scene_writer.submit(connection)

        values_sources.add_values_source_type(connection, 'input')
        values_sources.add_values_source_name(connection, 'values_input')

        values_sources.add_values_source_type(connection, 'generator')
        values_sources.add_values_source_name(connection, 'incremental_generator')

        attributes.add_attribute(connection, attributes.DISTINCT)
        attributes.add_attribute(connection, attributes.GLOBAL)

        return self

    def scene(self):
        return self._scene_writer

    def import_scene(self, schema_name):
        connection = self._connection
        project = self._project

        scene = self._scene

        #build sub-schema
        with _InnerBuilder(connection, project, scene) as bld:
            project.get_build_function(schema_name)(bld)

        return _SceneLabels(scene.name, connection)

    def project_type(self, name):
        return self._project_type(name)

    def label_type(self, name):
        return self._label_type(name)

    def property_(self, type_, name):
        if type_ not in properties.PROPERTY_TYPES:
            raise ValueError("Property type {} is not supported".format(type_))
        return self._property_(type_, name)

    def property_attribute(self, property_, attribute):
        self._add_property_attribute(property_, attribute)

    def incremental_value_generator(self, property_, start=0, increment=1):
        _pvs = self._property_value_sources

        if not property_ in _pvs:
            vs = values_sources.ValuesSource(
                'generator',
                'incremental_generator')

            self._values_sources.append(vs)

            ppt_vs = pvs.PropertyValueSource(property_, vs)

            _pvs[property_] = vsb.incremental_value_generator(
                ppt_vs,
                start,
                increment)

        else:
            raise RuntimeError(
                "Property {} already assigned to a values source".format(property_))

    def input_values(self, property_, values):
        _pvs = self._property_value_sources

        if not property_ in _pvs:
            vs = values_sources.ValuesSource(
                'input',
                'values_input')

            self._values_sources.append(vs)

            ppt_vs = pvs.PropertyValueSource(property_, vs)

            _pvs[property_] = vsb.input_values(values, ppt_vs)
        else:
            raise RuntimeError(
                "Property {} already assigned to a values source".format(property_))

    def _submit(self, connection):
        self._scene_writer.submit(connection)

        for vs in self._values_sources:
            values_sources.add_values_source(connection, vs)

        for pp in self._properties.values():
            properties.add_property_type(connection, pp.property_type)
            properties.add_property_name(connection, pp.property_name)

        for atr in self._property_attributes.values():
            properties.add_property_attribute(connection, atr)

        for vs in self._property_value_sources.values():
            pvs.add_property_values_source(
                connection,
                vs.property_values_source)

            # save value source instance
            vs.save(connection)

        for pj in self._label_types.values():
            pj.submit(connection)
            pj.clear()

    def _project_type(self, name):
        pj = _ProjectType(name)
        self._project_types[name] = pj

        return pj

    def _label_type(self, name):
        lt = _LabelType(name)
        self._label_types[name] = lt

        return lt

    def _add_property_attribute(self, property_, attribute):
        atr = properties.PropertyAttribute(property_, attribute)
        property_attributes = self._property_attributes

        if atr not in property_attributes:
            property_attributes[atr] = atr

    def _property_(self, type_, name):
        ppt = properties.Property(type_, name)
        _properties = self._properties

        if ppt not in _properties:
            _properties[ppt] = ppt
        return ppt

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._submit(self._connection)

class _InnerBuilder(_Builder):
    def __enter__(self):
        #does delete tables.
        return self

def build(connection, project, scene):
    return  _Builder(connection, project, scene)
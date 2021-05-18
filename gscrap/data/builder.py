from itertools import chain

from gscrap.data import engine
from gscrap.data.project_types import _ProjectType
from gscrap.data.labels import _LabelType

CLEAR_TABLE = '''
    DELETE FROM {};
'''

_PROJECT_TYPES = {}
_LABEL_TYPES = {}

def clear(connection):
    #clear tables
    table_names = [
        "project_types",
        "project_type_components",
        "labels",
        "label_components",
        "label_types",
        "label_instances"
    ]

    for name in table_names:
        connection.execute(CLEAR_TABLE.format(name))

def submit():
    with engine.connect() as connection:
        clear(connection)
        for pj in chain(_PROJECT_TYPES.values(), _LABEL_TYPES.values()):
            pj.submit(connection)
            pj.clear()

def project_type(name):
    pj = _ProjectType(name)
    _PROJECT_TYPES[name] = pj
    return pj

def label_type(name):
    lt = _LabelType(name)
    _LABEL_TYPES[name] = lt
    return lt

class _Builder(object):
    def __init__(self):
        self._built = False

    def __enter__(self):
        if not self._built:
            return self
        return

    def project_type(self, name):
        return project_type(name)

    def label_type(self, name):
        return label_type(name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        submit()
        self._built = True

_BUILDER  = _Builder()

def build():
    return _BUILDER
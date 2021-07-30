from os.path import join

from sqlalchemy import engine
from sqlalchemy import MetaData

from gscrap.data.paths import root
from gscrap.data import schemas

from gscrap.data.filters import schema as mld

_META = MetaData()

_ENGINE = engine.create_engine("sqlite:////{}".format(join(root(), "data.db")))

_BUILT = False

def create_tables(engine, meta):
    mld.build_schema(meta)
    schemas.build_schema(meta)
    meta.create_all(engine)

# create tables
# if not _BUILT:
#     create_tables(_ENGINE, _META)
#     _BUILT = True

def connect():
    return _ENGINE.connect()
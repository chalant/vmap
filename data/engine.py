from os.path import join

from sqlalchemy import engine

from data.paths import root
from data import schemas

_ENGINE = engine.create_engine("sqlite:////{}".format(join(root(), "data.db")))

# create tables
schemas.create_all(_ENGINE)

def connect():
    return _ENGINE.connect()
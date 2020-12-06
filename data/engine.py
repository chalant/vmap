from os.path import join

from sqlalchemy import engine

from data.paths import root

_ENGINE = engine.create_engine("sqlite:////{}".format(join(root(), "data.db")))

def connect():
    return _ENGINE.connect()
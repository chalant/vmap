from os.path import join

from sqlalchemy import text, engine

from data.paths import root

from tools.detection.data import schema

_GET_GROUPS = text(
    """
    SELECT * FROM filter_groups
    """
)

_GET_FILTERS = text(
    """
    SELECT * FROM filters
    WHERE group=:group
    ORDER BY position ASC
    """
)

_PARAMETER_QUERY = """SELECT * FROM {} WHERE group=:group AND position=:position"""

_ENGINE = engine.create_engine("sqlite:////{}".format(join(root(), "filters.db")))

schema.create_all(_ENGINE)

def connect():
    return _ENGINE.connect()

def get_parameters(connection, filter_, group):
    query = None
    if filter_.type == "Blur":
        if filter_.name == "Gaussian":
            query = text(_PARAMETER_QUERY.format("gaussian_blur"))
        elif filter_.name == "Average":
            pass
            #todo: more parameters
    if query:
        return connection.execute(query, group=group, position=filter_.position)

def get_filters(connection, group):
    return connection.execute(_GET_FILTERS, group=group)

def get_groups(connection):
    return connection.execute(_GET_GROUPS)



from uuid import uuid4

from sqlalchemy import text, engine

_ENGINE = engine.create_engine() #todo: engine should be created in main script!

_UPDATE_PARENT = text(
    """
    UPDATE label_instances SET has_child = :has_child
    WHERE instance_id = :parent_id;
    """)

_ADD_LABEL_INSTANCE_TO_PARENT = text(
    """
    INSERT INTO label_instances(instance_id, parent_id) VALUES (:instance_id, :parent_id)
    ON CONFLICT(instance_id) DO UPDATE SET parent_id=:parent_id; 
    """)

_ADD_LABEL_INSTANCE = text(
    """
    INSERT INTO label_instances(instance_id, label_id, rectangle_id) VALUES (:instance_id, :label_id, :rectangle_id)
    """)

_SELECT_LABEL_INSTANCE = text(
    """
    SELECT *
    FROM label_instances
    WHERE instance_id=:instance_id
    """)

_SELECT_LABEL_INSTANCE_OF_PARENT = text(
    """
    SELECT *
    FROM label_instances
    WHERE instance_id=:instance_id AND parent_id=:parent_id
    """)

_SELECT_LABEL_INSTANCE_IS_CHILD = text(
    """
    SELECT *
    FROM label_instances
    WHERE has_child=:has_child
    """)

_SELECT_LABEL_INSTANCE_PARENT =  text(
    """
    SELECT *
    FROM label_instances
    WHERE label_instances.parent_id = :parent_id
    """)

def _get_root(engine):
    with engine.begin() as conn:
        name = "root"
        results = conn.execute(_SELECT_LABEL_INSTANCE, instance_id=name)
        if not len(results):
            conn.execute(_ADD_LABEL_INSTANCE, instance_id=name)
            return _LabelInstance(engine, name)

_ROOT = _get_root(_ENGINE)

def get_root():
    """
    Returns
    -------
    _LabelInstance
    """
    return _ROOT

def get_instance_id(name):
    with _ENGINE.begin() as conn:
        result = conn.execute(_SELECT_LABEL_INSTANCE, instance_id=name)
        row = result.fetchone()
        return _LabelInstance(
            _ENGINE,
            row["instance_id"],
            row["label_id"],
            row["parent_id"],
            row["has_child"])

class _Label(object):
    __slots__ = ["_engine", "_label_id", "_label_name", "_label_type", "_total", "_max"]

    def __init__(self, engine, label_id, label_name, label_type, total, max=None):
        self._engine = engine
        self._label_id = label_id
        self._label_name = label_name
        self._label_type = label_type
        self._total = total
        self._max = max

    def add_instance(self, label_instance):
        """

        Parameters
        ----------
        label_instance: _LabelInstance

        Returns
        -------

        """
        if not self._max:
            instance = _LabelInstance(
                engine,
                uuid4().hex,
                self._label_id,
                label_instance.instance_id,
                label_instance.has_child)

            self._total += 1
            return instance
        else:
            if self._total < self._max:
                instance = _LabelInstance(
                    engine,
                    uuid4().hex,
                    self._label_id,
                    label_instance.instance_id,
                    label_instance.has_child)
                self._total += 1
                return instance
            return

    def get_instances(self):
        return

class _LabelInstance(object):
    __slots__ = ["_engine", "_instance_id", "_label_id", "_rectangle_id", "_parent_id", "_has_child"]

    def __init__(self, engine, instance_id, label_id, rectangle_id, parent_id=None, has_child=False):
        """

        Parameters
        ----------
        connection: sqlalchemy.engine.Engine
        """
        self._engine = engine
        self._instance_id = instance_id
        self._parent_id = parent_id
        self._has_child = has_child
        self._label_id = label_id
        self._rectangle_id = rectangle_id

    @property
    def instance_id(self):
        return self._instance_id

    def add_child(self, label_id, rectangle_id):
        #add type to this label type in the database
        with self._engine.begin() as conn:
            parent_id = self._instance_id
            instance_id = uuid4().hex
            # will set this node as the parent_id of instance_id "instance_id"
            conn.execute(_UPDATE_PARENT, has_child=True, parent_id=parent_id)
            conn.execute(
                _ADD_LABEL_INSTANCE_TO_PARENT,
                instance_id=instance_id,
                parent_id=parent_id,
                rectangle_id=rectangle_id)
            return _LabelInstance(self._engine, uuid4().hex, label_id, rectangle_id, parent_id)

    def get_parent(self):
        with self._engine.begin() as conn:
            if self._parent_id:
                result = conn.execute(_SELECT_LABEL_INSTANCE, instance_id=self._parent_id)
                row = result.fecthone()
                return _LabelInstance(
                    self._engine,
                    row["instance_id"],
                    row["label_id"],
                    row["parent_id"],
                    row["has_child"]
                )
            return

    @property
    def has_child(self):
        return self._has_child

    def get_child(self, instance_id):
        with self._engine.begin() as conn:
            if self._has_child:
                result = conn.execute(
                    _SELECT_LABEL_INSTANCE_OF_PARENT,
                    instance_id=instance_id,
                    parent_id=self._parent_id)
                if not result:
                    return
                row = result.fetchone()
                return _LabelInstance(
                    self._engine,
                    row["instance_id"],
                    row["label_id"],
                    row["parent_id"],
                    row["has_child"])
            return

    def get_children(self):
        #return all the children of this instance_id
        parent_id = self._parent_id
        engine = self._engine
        with engine.begin() as conn:
            # returns all the children of parent_id
            for row in conn.execute(_SELECT_LABEL_INSTANCE_PARENT, parent_id=parent_id):
                yield _LabelInstance(
                    engine,
                    row["instance_id"],
                    row["label_id"],
                    parent_id,
                    row["has_child"])
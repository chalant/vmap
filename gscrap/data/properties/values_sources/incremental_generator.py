from sqlalchemy import text

_ADD_INCREMENTAL_GENERATOR = text(
    """
    INSERT OR IGNORE INTO incremental_generator(from, increment, generator_id)
    VALUES(:from_, :increment, :generator_id)
    """
)

_GET_INCREMENTAL_GENERATOR_SPEC = text(
    """
    SELECT * FROM incremental_generator
    WHERE generator_id=:generator_id
    """
)

_DELETE_INCREMENTAL_GENERATOR = text(
    """
    DELETE FROM incremental_generator
    WHERE generator_id=:generator_id
    """
)

class IncrementalGeneratorSpec(object):
    __slots__ = ['from_', 'increment', '_hash']
    
    def __init__(self, from_=0, increment=1):
        self.from_ = from_
        self.increment=increment

        self._hash = hash((from_, increment))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return other.from_ == self.from_ and \
               other.increment == self.increment

def add_incremental_generator(connection, incremental_generator):
    connection.execute(
        _ADD_INCREMENTAL_GENERATOR,
        from_=incremental_generator.from_,
        increment=incremental_generator.increment,
        generator_id=hash(incremental_generator)
    )

def get_incremental_generator_spec(connection, generator_id):
    connection.execute(
        _GET_INCREMENTAL_GENERATOR_SPEC,
        generator_id=generator_id
    )

def delete_incremental_generator(connection, incremental_generator):
    connection.execute(
        _DELETE_INCREMENTAL_GENERATOR,
        incremental_generator=hash(incremental_generator)
    )
from sqlalchemy import text

_ADD_INCREMENTAL_GENERATOR = text(
    """
    INSERT OR IGNORE INTO incremental_value_generator(start, increment, values_source_id)
    VALUES(:from_, :increment, :values_source_id)
    """
)

_GET_INCREMENTAL_GENERATOR_SPEC = text(
    """
    SELECT * FROM incremental_value_generator
    WHERE values_source_id=:values_source_id
    """
)

_DELETE_INCREMENTAL_GENERATOR = text(
    """
    DELETE FROM incremental_generator
    WHERE values_source_id=:generator_id
    """
)

class IncrementalGeneratorSpec(object):
    __slots__ = ['from_', 'increment', '_hash']
    
    def __init__(self, values_source, from_=0, increment=1):
        self.from_ = from_
        self.increment = increment

        self._hash = hash(values_source)

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
        values_source_id=hash(incremental_generator)
    )

def get_incremental_generator_spec(connection, values_source):
    res = connection.execute(
        _GET_INCREMENTAL_GENERATOR_SPEC,
        values_source_id=hash(values_source)
    ).first()

    return IncrementalGeneratorSpec(values_source, res['start'], res['increment'])

def delete_incremental_generator(connection, incremental_generator):
    connection.execute(
        _DELETE_INCREMENTAL_GENERATOR,
        incremental_generator=hash(incremental_generator)
    )
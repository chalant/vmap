from sqlalchemy import text

_ADD_VALUES_INPUT = text(
    """
    INSERT INTO values_input(values_source_name, values_source_type, values_input_id, values)
    VALUES(:values_source_name, :values_source_type, :values_input_id, :values)
    """
)

_GET_VALUES_INPUT =  text(
    """
    SELECT * FROM values_input
    WHERE values_input_id=:values_input_id
    """
)

_DELETE_VALUES_INPUT = text(
    """
    DELETE FROM values_input
    WHERE values_input_id:values_input_id
    """
)

class InputValues(object):
    def __init__(self, values):
        self.values = values

    def __hash__(self):
        return hash(str(self.values))

    def __eq__(self, other):
        for a, b in zip(other.values, self.values):
            if a != b:
                return False

        return True

def add_input_values(connection, values_input):
    values = str(values_input.values)

    connection.execute(
        _ADD_VALUES_INPUT,
        values_input_id=hash(values),
        values=values
    )

def delete_input_values(connection, values_input):
    connection.execute(
        _DELETE_VALUES_INPUT,
        values_input=hash(values_input)
    )

def get_input_values(connection, input_values_id):
    return connection.execute(
        _GET_VALUES_INPUT,
        values_input_id=input_values_id
    )

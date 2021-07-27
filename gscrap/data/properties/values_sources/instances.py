from abc import ABC, abstractmethod

from sqlalchemy import text

from gscrap.data.properties.values_sources import input_values
from gscrap.data.properties.values_sources import incremental_generator

_GET_INCREMENTAL_GENERATOR = text(
    """
    SELECT * FROM incremental_value_generator
    INNER JOIN values_sources_incremental_value_generators 
        ON values_sources_incremental_value_generators.generator_id = incremental_value_generator.generator_id
    WHERE value_source_id=:values_source_id
    """
)

_GET_INPUT_VALUES = text(
    """
    SELECT * FROM values_input
    INNER JOIN values_sources_values_inputs
        ON values_sources_values_inputs.values_inputs_id = values_input.values_input_id
    WHERE value_source_id=:values_source_id
    """
)

_MAP_VALUES_SOURCE_TO_ICR_GEN = text(
    """
    INSERT INTO values_sources_incremental_value_generators(value_source_id, generator_id)
    VALUES (:value_source_id, :generator_id)
    """
)

_MAP_VALUES_SOURCE_TO_VAL_IPT = text(
    """
    INSERT INTO values_sources_values_inputs(value_source_id, values_inputs_id)
    VALUES (:value_source_id, :values_inputs_id)
    """
)

class ValueSourceInstance(ABC):
    def __init__(self, property_values_source):
        self.property_values_source = property_values_source

    @abstractmethod
    def save(self, connection):
        raise NotImplementedError

    @abstractmethod
    def delete(self, connection):
        raise NotImplementedError


class InputValues(ValueSourceInstance):
    def __init__(self, values, property_values_source):
        super(InputValues, self).__init__(property_values_source)

        self._values = input_values.InputValues(values)

    def save(self, connection):
        values = self._values
        input_values.add_input_values(
            connection,
            values)

        connection.execute(
            _MAP_VALUES_SOURCE_TO_VAL_IPT,
            value_source_id=hash(self.property_values_source.value_source),
            values_inputs_id=hash(values)
        )

    def delete(self, connection):
        #todo: count all the mappings. if count == 0 delete
        input_values.delete_input_values(connection, self._values)


class IncrementalValuesGenerator(ValueSourceInstance):
    def __init__(self, from_, increment, property_values_source):
        super(IncrementalValuesGenerator, self).__init__(property_values_source)

        self._spec = incremental_generator.IncrementalGeneratorSpec(from_, increment)

    def save(self, connection):
        spec = self._spec

        incremental_generator.add_incremental_generator(connection, spec)

        connection.execute(
            _MAP_VALUES_SOURCE_TO_ICR_GEN,
            value_source_id=hash(self.property_values_source.value_source),
            values_inputs_id=hash(spec)
        )

    def delete(self, connection):
        # todo: count all the mappings. if count == 0 delete
        incremental_generator.delete_incremental_generator(connection, self._spec)

def get_value_source_instance(connection, values_source):
    id_ = hash(values_source)

    if values_source.name == 'incremental_generator':
        res = connection.execute(
            _GET_INCREMENTAL_GENERATOR,
            values_source_id=id_
        ).first()

        return IncrementalValuesGenerator(
            res['from'],
            res['increment'],
            values_source)

    elif values_source.name == 'values_input':
        res = connection.execute(
            _GET_INPUT_VALUES,
            values_source_id=id_
        ).first()

        return InputValues(
            eval(res['values']),
            values_source)

    else:
        raise ValueError("Value source: {} {} is not supported".format(
            values_source.type_,
            values_source.name))
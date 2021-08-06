from abc import ABC, abstractmethod

from gscrap.data.properties import properties

from gscrap.data.properties.values_sources import incremental_generator
from gscrap.data.properties.values_sources import values_sources

class Generator(ABC):
    @abstractmethod
    def next_value(self):
        raise NotImplementedError

class RandomGenerator(Generator):
    def __init__(self, sequence_length):
        self._sequence_length = sequence_length

    @abstractmethod
    def set_value_samples(self, samples):
        raise NotImplementedError

class RandomStringGenerator(RandomGenerator):
    def __init__(self, sequence_length):
        super(RandomStringGenerator, self).__init__(sequence_length)

        self._sequence_length = sequence_length

    def next_value(self):
        #todo
        return

    def set_value_samples(self, samples):
        pass


class RandomIntegerGenerator(RandomGenerator):
    def __init__(self, sequence_length):
        super(RandomIntegerGenerator, self).__init__(sequence_length)

    def next_value(self):
        #todo
        return

    def set_value_samples(self, samples):
        pass

class RandomBooleanGenerator(RandomGenerator):
    def __init__(self, sequence_length):
        super(RandomBooleanGenerator, self).__init__(sequence_length)

    def next_value(self):
        return

    def set_value_samples(self, samples):
        pass

class IncrementalGenerator(Generator):
    def __init__(self, from_=0, increment=1):
        self._p_value = from_
        self._increment = increment

    def next_value(self):
        value = self._p_value
        self._p_value += self._increment
        return value

def get_value_generator(connection, property_value_source):
    property_ = property_value_source.property_
    source = property_value_source.values_source

    source_name = values_sources.values_source_name(source)

    if source_name == 'incremental_generator':
        spec = incremental_generator.get_incremental_generator_spec(
            connection,
            source)

        if properties.property_type(property_) ==  properties.INTEGER:
            return IncrementalGenerator(int(spec.from_), int(spec.increment))
        else:
            return IncrementalGenerator(spec.from_, spec.increment)

    elif source_name == 'random_generator':
        raise NotImplementedError(source_name)

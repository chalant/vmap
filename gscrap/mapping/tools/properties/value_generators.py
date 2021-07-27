from gscrap.data.properties.values_sources import values_sources

from abc import ABC, abstractmethod

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

def get_value_generator(property_value_source):
    property_ = property_value_source.property_
    source = property_value_source.value_source

    source_name = values_sources.values_source_name(source)

    if source_name == 'incremental_generator':
        return IncrementalGenerator(source.from_, source.increment)
    elif source_name == 'random_generator':
        raise NotImplementedError()

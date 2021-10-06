from gscrap.data.properties import properties
from gscrap.data.properties.values_sources import instances


# def random_value_generator(property_, sequence_length=8):
#     property_type = property_.property_type
#
#     if property_type == properties.INTEGER:
#         return value_generators.RandomIntegerGenerator(sequence_length)
#     elif property_type == properties.STRING:
#         return value_generators.RandomStringGenerator(sequence_length)
#     elif property_type == properties.BOOLEAN:
#         return value_generators.RandomBooleanGenerator(sequence_length)
#     else:
#         raise ValueError("No random value generator for property type {}".format(property_type))

def incremental_value_generator(property_values_source, start=0, increment=1):
    property_type = properties.property_type(property_values_source.property_)

    if property_type == properties.INTEGER:
        if not isinstance(start, int) or not isinstance(increment, int):
            raise ValueError("Type mismatch!")
        return instances.IncrementalValuesGenerator(
            start, increment, property_values_source)

    elif property_type == properties.FLOAT:
        if not isinstance(start, float) or not isinstance(increment, float):
            raise ValueError("Type mismatch!")
        return instances.IncrementalValuesGenerator(
            start, increment, property_values_source)
    else:
        raise ValueError("No incremental value generator for property type {}".format(property_type))

def input_values(property_values_source, values):
    property_type = properties.property_type(property_values_source.property_)
    values_source = property_values_source.values_source

    if property_type == properties.INTEGER:
        _check_values_types(values, int)
    elif property_type == properties.FLOAT:
        _check_values_types(values, float)
    elif property_type == properties.STRING:
        _check_values_types(values, str)

    return instances.InputValues(values, values_source)


def _check_values_types(values, type_):
    for v in values:
        if not isinstance(v, type_):
            raise ValueError(
                "Cannot assign value of type {} to property of type {}".format(type(v), type_))





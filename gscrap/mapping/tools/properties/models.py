from collections import OrderedDict

from gscrap.data.properties import properties
from gscrap.data.rectangles import rectangle_instances as ri

def get_property_model(property_):
    return PropertyModel(property_)

class PropertyValueWrapper(object):
    def __init__(self, property_):
        self.property_ = property_
        self._value = None
        self.pvalue = None
        self._property_value = None

    @property
    def property_value(self):
        return self._property_value

    @property_value.setter
    def property_value(self, value):
        self._property_value = value
        if self._value == None:
            self._value = value.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, ipt):
        val = self._value

        self.pvalue = val
        self._value = ipt

        if not self._property_value and ipt != None:
            self._property_value = properties.PropertyValue(self.property_, ipt)

        elif ipt != None:
            self._property_value.value = ipt

class PropertyModel(object):
    def __init__(self, property_):
        self._rectangle_instances = OrderedDict()
        self._property_values = []

        self._values = ()
        self._property_ = property_

        self._index = 0

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, ipt):
        self._values = ipt

    @property
    def rectangle_instances(self):
        return self._rectangle_instances

    def get_rectangle_instance(self, index):
        return self._rectangle_instances[index]

    def get_property_value(self, index):
        return self._property_values[index]

    def set_value(self, index, value):
        self._property_values[index].value = value

    def remove_value(self, index):
        self._property_values[index].value = None

    def add_rectangle_instance(self, rectangle_instance):
        self._rectangle_instances[self._index] = rectangle_instance
        self._index += 1

    def load_property_values(self, connection):
        property_ = self._property_
        property_values = [] * (self._index + 1)

        for idx, instance in self._rectangle_instances.items():
            pvw = PropertyValueWrapper(property_)
            pvw._property_value = ri.get_property_value(connection, instance, property_)
            property_values[idx] = pvw

        self._property_values = property_values

    def clear(self):
        self._rectangle_instances.clear()
        self._index = 0
        self._property_values.clear()

    def submit(self, connection):
        instances = self._rectangle_instances

        for idx, ppt in enumerate(self._property_values):

            rct = instances[idx]

            #un-map any value set to none
            property_value = ppt.property_value

            if property_value:
                if ppt.value == None:
                    ri.unmap_from_property_value(connection, rct, property_value)
                    continue

                properties.add_property_value(connection, property_value)
                ri.map_to_property_value(connection, instances[idx], property_value)


        #remove property values that are not referenced by any rectangle instance.

        for property_value in self._property_values:
            if ri.count_mapped_instances(connection, property_value) == 0:
                properties.delete_property_value(connection, property_value)





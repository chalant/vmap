from abc import ABC, abstractmethod

from gscrap.data.properties import properties
from gscrap.data.rectangles import rectangle_instances as ri

from gscrap.mapping.tools import display

def get_property_model(property_, value_store):
    return PropertyModel(property_, value_store)

class AbstractValueAssignment(ABC):
    @property
    @abstractmethod
    def values(self):
        raise NotImplementedError

    @values.setter
    @abstractmethod
    def values(self, ipt):
        raise NotImplementedError

    @abstractmethod
    def assign_value(self, row_index, value_index, rectangle_instance):
        raise  NotImplementedError

    @abstractmethod
    def remove_value(self, row_index, value_index, rectangle_instance):
        raise NotImplementedError

class SharedValueAssignment(AbstractValueAssignment):
    def __init__(self):
        self._values = None

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, ipt):
        self._values = ipt

    def __iter__(self):
        return iter([val for val in self._values])

    def assign_value(self, row_index, value_index, rectangle_instance):
        rectangle_instance.set_value(row_index, self._values[value_index])

    def remove_value(self, row_index, value_index, rectangle_instance):
        pass

class DistinctValueAssignment(AbstractValueAssignment):
    def __init__(self):
        self._values = None
        self._assigned = None

    @property
    def values(self):
        #yields non-assigned values
        for val in self._values:
            yield val

    @values.setter
    def values(self, ipt):
        self._values = ipt
        self._assigned = [None] * len(ipt)

    def __iter__(self):
        return iter([val for val in self._values])

    def assign_value(self, row_index, value_index, rectangle_instance):
        value = self._values[value_index]
        assigned = self._assigned

        rectangle_instance.set_value(row_index, value)

        prv_instance = assigned[value_index]

        if prv_instance:
            # remove value from previous instance
            ppt_value = prv_instance.get_value(row_index)
            ppt_value.value = None

        assigned[value_index] = rectangle_instance

    def remove_value(self, row_index, value_index, rectangle_instance):
        self._assigned[value_index] = None

        ppt_value = rectangle_instance.get_value(row_index)
        ppt_value.value = None

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
            self._property_value = properties.PropertyValue(
                self.property_,
                ipt)

        elif ipt != None:
            self._property_value.value = ipt

class PropertyApplication(object):
    def __init__(self, property_model, property_controller, index):
        self.property_model = property_model
        self.property_controller = property_controller
        self.index = index

    def view(self):
        return self.property_controller.view()

    @property
    def controller(self):
        return self.property_controller

    @property
    def model(self):
        return self.property_model


class PropertyRectangle(display.DisplayItem):
    def __init__(self, id_, rectangle_instance):
        super(PropertyRectangle, self).__init__(id_, rectangle_instance)

        self.values = []
        self.applications = []

        def null_callback(instance):
            pass

        self._callback = null_callback

    def get_value(self, index):
        return self.values[index]

    def set_value(self, index, value):
        self.values[index].value = value

        self._callback(self)

    def on_value_set(self, callback):
        self._callback = callback

    def add_application(self, application):
        self.applications.append(application)


class PropertyRectangleFactory(object):
    def create_instance(self, id_, rectangle):
        return PropertyRectangle(id_, rectangle)

class PropertyModel(object):
    def __init__(self, property_, assignment):
        """

        Parameters
        ----------
        property_
        assignment: AbstractValueAssignment
        """

        self._assignment = assignment
        self._property_ = property_

        self._index = 0
        self.application_index = 0
        self.selected_instance = None

    @property
    def assignment(self):
        return self._assignment

    @property
    def values(self):
        return self._assignment.values

    @values.setter
    def values(self, ipt):
        self._assignment.values = ipt

    def assign_value(self, value_index):
        self._assignment.assign_value(
            self.application_index,
            value_index,
            self.selected_instance)

    def remove_value(self, value_index):
        self._assignment.remove_value(
            self.application_index,
            value_index,
            self.selected_instance)

    def store(self, connection, value, rectangle_instance):
        pass
from gscrap.data import attributes
from gscrap.data.properties import properties

class PropertyController(object):
    def __init__(self, values, values_view):
        self._values = values
        self._values_view = values_view

    def on_selection(self, index):
        self._values.set_value(index)



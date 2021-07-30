from gscrap.mapping.tools.properties import views

class PropertyController(object):
    def __init__(self, model, property_):
        '''

        Parameters
        ----------
        model: gscrap.mapping.tools.properties.models.PropertyModel
        '''
        self._view = views.PropertyView(self, model, property_)
        self._model = model
        self._selected_instance = None

    def view(self):
        return self._view

    @property
    def selected_instance(self):
        return self._selected_instance

    @selected_instance.setter
    def selected_instance(self, instance):
        self._selected_instance = instance

    def on_value_selection(self, index):
        instance = self._selected_instance

        if instance:
            #assign value to rectangle instance
            self._model.assign_value(index, instance)
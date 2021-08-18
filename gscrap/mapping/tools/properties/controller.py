class PropertyController(object):
    def __init__(self, model):
        '''

        Parameters
        ----------
        model: gscrap.mapping.tools.properties.models.PropertyModel
        '''

        self._view = None
        self._model = model

    def view(self):
        return self._view

    def set_view(self, view):
        self._view = view

    def on_value_selection(self, index):
        self._view.set_value(self._model.assign_value(index))

    def on_clear(self):
        self._model.remove_value()
        self._view.set_value(None)
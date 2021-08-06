from gscrap.gui import button
from gscrap.gui import menu_bar

SAVE_BUTTON = button.Button("Save")

class Saving(button.ButtonController):
    def __init__(self, button, rectangle_instances):
        super(Saving, self).__init__(button)

        self._rectangle_instances = rectangle_instances

    def _execute(self, button):
        pass




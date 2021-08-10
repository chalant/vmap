from gscrap.gui import button
from gscrap.gui import menu_bar

from gscrap.data import engine
from gscrap.data.properties import properties
from gscrap.data.rectangles import rectangle_instances as ri

SAVE_BUTTON = button.Button("Save")

MENU_BAR = menu_bar.MenuBar()

class PropertyValueSaving(button.ButtonController):
    def __init__(self, button):
        super(PropertyValueSaving, self).__init__(button)

        self._saved = False

        self._to_save = []

    def on_value_set(self, rectangle_instance):
        self._to_save.append(rectangle_instance)

        if not self._saved:
            self._button.enable_button()

    def _execute(self, button):
        to_delete = []

        with engine.connect() as connection:
            for instance in self._to_save:
                for property_value in instance.values:
                    if property_value:
                        rectangle_instance = instance.rectangle_instance
                        if property_value.value == None:
                            ri.unmap_from_property_value(
                                connection,
                                rectangle_instance,
                                property_value)
                            to_delete.append(property_value)
                            continue

                        properties.add_property_value(
                            connection,
                            property_value)

                        ri.map_to_property_value(
                            connection,
                            rectangle_instance,
                            property_value)

            #delete property values that are not mapped to any rectangle instance
            for property_value in to_delete:
                if ri.count_mapped_instances(connection, property_value) == 0:
                    properties.delete_property_value(
                        connection,
                        property_value)

        button.disable_button()
        self._saved = False

def set_controller(button, controller):
    button.set_controller(controller)

MENU_BAR.add_button(SAVE_BUTTON)




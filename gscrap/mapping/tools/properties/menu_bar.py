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

        self._to_save = {}
        self._to_delete = {}

    def on_value_set(self, rectangle_instance):
        self._to_save.append(rectangle_instance)

        if not self._saved:
            self._button.enable_button()

    def delete_value(self, rectangle_instance, property_value):
        print("DELETE VALUE", property_value.value)

        tpl = (rectangle_instance, property_value)

        if tpl in self._to_save:
            self._to_save.pop(tpl)

        self._to_delete[tpl] = tpl
        self._saved = False

        self._button.enable_button()

    def save_value(self, rectangle_instance, property_value):
        tpl = (rectangle_instance, property_value)

        if tpl in self._to_delete:
            self._to_delete.pop(tpl)

        self._to_save[tpl] = tpl
        self._saved = False

        self._button.enable_button()

    def _execute(self, button):
        with engine.connect() as connection:
            for instance, value in self._to_save.values():
                properties.add_property_value(
                    connection,
                    value)

                ri.map_to_property_value(
                    connection,
                    instance,
                    value)

            for instance, value in self._to_delete.values():
                ri.unmap_from_property_value(
                    connection,
                    instance,
                    value)

                #delete property values that are not mapped to any rectangle instance
                if ri.count_mapped_instances(connection, value) == 0:
                    properties.delete_property_value(
                        connection,
                        value)

        self._to_save.clear()
        self._to_delete.clear()

        button.disable_button()
        self._saved = True

def set_controller(button, controller):
    button.set_controller(controller)

MENU_BAR.add_button(SAVE_BUTTON)




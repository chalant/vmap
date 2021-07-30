from collections import defaultdict

from gscrap.windows import windows
from gscrap.windows import factory as wf

from gscrap.data import engine
from gscrap.data import attributes

from gscrap.data.rectangles import rectangles
from gscrap.data.rectangles import rectangle_labels

from gscrap.data.labels import label_properties

from gscrap.data.properties import properties
from gscrap.data.properties import property_values_source as pvs

from gscrap.data.properties.values_sources import values_sources

from gscrap.mapping.tools import tools
from gscrap.mapping.tools import display
from gscrap.mapping.tools import interaction

from gscrap.mapping.tools.properties import models
from gscrap.mapping.tools.properties import value_generators
from gscrap.mapping.tools.properties import controller

class Properties(tools.Tool):
    def __init__(self, main_view):
        canvas = main_view.canvas

        self._canvas = main_view.canvas
        self._container = main_view

        self._display = display.RectangleDisplay(canvas)
        self._interaction = interaction.Interaction(canvas, 0, 0)

        self._models = {}

        self._instances = {}

        self._selected_rectangle = None

        self._window_manager = wm = windows.DefaultWindowModel(400, 600)
        self._windows_controller = windows.WindowController(
            wm,
            wf.WindowFactory())

    def get_view(self, container):
        return self._windows_controller.start(container)

    def start_tool(self, project):

        #load rectangle instances with properties
        canvas = self._canvas

        dsp = display.RectangleDisplay(canvas)
        fct = models.PropertyRectangleFactory()

        itc = self._interaction

        itc.width = project.width
        itc.height = project.height

        instances = self._instances

        rectangles_dict = defaultdict(list)

        with engine.connect() as connection:
            for label_property in label_properties.get_labels_with_properties(connection):

                property_ = label_property.property_

                #todo: create property view
                # for each property, we have a mvc pattern.
                # the view can get the property values from the model.
                #problem: how do we map to the values?

                distinct = False

                for att in properties.get_property_attributes(
                        connection,
                        property_):

                    if att.attribute == attributes.DISTINCT:
                        distinct = True

                if distinct:
                    value_store = models.DistinctValueStore()
                else:
                    value_store = models.SharedValueStore()

                #load and draw values

                values = []

                ppt_vs = pvs.get_property_values_source(connection, property_)

                ppt_model = models.get_property_model(property_, value_store)
                ppt_controller = controller.PropertyController(ppt_model, property_)

                source_type = values_sources.values_source_type(ppt_vs.values_source)

                count = 0

                app = models.PropertyApplication(ppt_model, ppt_controller)

                #todo: we query and map rectangle to label to avoid reloading already loaded
                # rectangles.

                for rct in rectangle_labels.get_rectangles_with_label(connection, label_property.label):
                    if rct.id not in rectangles_dict:
                        for ist in rectangles.get_rectangle_instances(connection, rct):

                            instances[count + 1] = instance = dsp.draw(ist, fct)

                            ppt_model.add_rectangle_instance(ist)

                            count += 1

                            rectangles_dict[rct.id].append(instance)
                    else:
                        for instance in rectangles_dict[rct.id]:
                            instance.add_application(app)

                if source_type == values_sources.GENERATOR:
                    value_generator = value_generators.get_value_generator(ppt_vs)
                    #generate a value for each rectangle instance
                    for _ in range(count):
                        values.append(value_generator.next_value())

                elif source_type == values_sources.INPUT:
                    #todo:
                    raise NotImplementedError("input values source")

                #assign values to value store
                value_store.values = values

            #start interaction
            itc.start(instances)
            itc.on_left_click(self._on_left_click)

    def _on_left_click(self, rct):
        rid = self._rectangle_id(rct)
        p_rid = self._selected_rectangle

        #display property setters
        if rid != p_rid:
            wc = self._windows_controller
            for app in rct.applications:
                wc.clear()
                wc.add_window(app)
                wc.start(self._container)

                self._set_selected_instance(app.controller, rct)

            self._selected_rectangle = rid
        else:
            for app in rct.applications:
                self._set_selected_instance(app.controller, rct)

    def _set_selected_instance(self, property_controller, instance):
        property_controller.selected_instance = instance

    def _rectangle_id(self, rectangle):
        return rectangle.id

    def clear_tool(self):
        self._interaction.unbind()

        dsp = self._display

        for instance in self._instances.values():
            dsp.delete(instance)

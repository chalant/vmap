import tkinter as tk
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

from gscrap.data.rectangles import rectangle_instances as ri

from gscrap.mapping.tools import tools
from gscrap.mapping.tools import display
from gscrap.mapping.tools import interaction

from gscrap.mapping.tools.properties import views
from gscrap.mapping.tools.properties import models
from gscrap.mapping.tools.properties import value_generators
from gscrap.mapping.tools.properties import controller
from gscrap.mapping.tools.properties import menu_bar


class Properties(tools.Tool):
    def __init__(self, main_view):
        canvas = main_view.canvas

        self._canvas = main_view.canvas
        self._container = main_view

        save_button = menu_bar.SAVE_BUTTON

        self._saving = saving = menu_bar.PropertyValueSaving(save_button)

        menu_bar.set_controller(save_button, saving)

        self._display = display.RectangleDisplay(canvas)
        self._interaction = interaction.Interaction(canvas, 0, 0)

        self._models = {}

        self._instances = {}

        self._selected_rectangle = None
        self._selected_instance = None

        self._properties_win = wm = windows.DefaultWindowModel(400, 600)
        self._properties_wc = windows.WindowController(
            wm,
            wf.WindowFactory())

    def get_view(self, container):
        frame = tk.Frame(container)
        mb = menu_bar.MENU_BAR.render(frame)
        mb.pack(anchor=tk.NW)

        self._properties_wc.start(frame).pack()

        return frame

    def start_tool(self, project):

        #load rectangle instances with properties
        canvas = self._canvas

        dsp = display.RectangleDisplay(canvas)
        fct = models.PropertyRectangleFactory()
        saving = self._saving

        itc = self._interaction

        itc.width = project.width
        itc.height = project.height

        instances = self._instances

        rectangles_dict = defaultdict(list)

        ppt_app_idx = 0

        with engine.connect() as connection:
            for property_ in properties.get_properties(connection):
                count = 0
                distinct = False

                for att in properties.get_property_attributes(
                        connection,
                        property_):

                    if att.attribute == attributes.DISTINCT:
                        distinct = True

                if distinct:
                    value_store = models.DistinctValueAssignment()
                else:
                    value_store = models.SharedValueAssignment()

                # load and draw values

                values = []

                ppt_model = models.get_property_model(property_, value_store)
                ppt_controller = controller.PropertyController(ppt_model)

                ppt_view = views.PropertyView(ppt_controller, ppt_model, property_)
                ppt_controller.set_view(ppt_view)
                app = models.PropertyApplication(
                    ppt_model,
                    ppt_controller,
                    ppt_app_idx)

                ppt_app_idx += 1

                ppt_vs = pvs.get_property_values_source(connection, property_)

                for label_property in label_properties.get_labels_of_property(connection, property_):
                    #todo: (optimization) pre-query and map rectangle to label to avoid reloading already loaded
                    # rectangles.

                    for rct in rectangle_labels.get_rectangles_with_label(connection, label_property.label):
                        if rct.id not in rectangles_dict:
                            for ist in rectangles.get_rectangle_instances(connection, rct):

                                instances[count + 1] = instance = dsp.draw(ist, fct)

                                rectangles_dict[rct.id].append(instance)
                                instance.add_application(app)

                                instance.values.append(ri.get_property_value(
                                    connection,
                                    instance.rectangle_instance,
                                    property_
                                ))

                                count += 1

                                #register saving
                                instance.on_value_set(saving.on_value_set)

                        else:
                            for instance in rectangles_dict[rct.id]:

                                instance.values.append(ri.get_property_value(
                                    connection,
                                    instance.rectangle_instance,
                                    property_
                                ))

                                instance.add_application(app)
                                instance.on_value_set(saving.on_value_set)

                source_type = values_sources.values_source_type(ppt_vs.values_source)

                if source_type == values_sources.GENERATOR:
                    value_generator = value_generators.get_value_generator(
                        connection,
                        ppt_vs)
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
        rid = self._rectangle_id(rct.rectangle_instance)
        p_rid = self._selected_rectangle

        iid = rct.rid
        p_iid = self._selected_instance

        #display property setters only if the rectangle has changed
        # if the instance changed, update the values

        if rid != p_rid:
            wc = self._properties_wc

            for app in rct.applications:
                wc.clear()
                wc.add_window(app)

                self._set_selected_instance(app.model, rct)
                self._set_application_index(app.model, app.index)

            self._selected_rectangle = rid
        else:
            for app in rct.applications:
                self._set_selected_instance(app.model, rct)
                self._set_application_index(app.model, app.index)

        #update values of the view.
        if iid != p_iid:
            self._update_view(zip(rct.values, rct.applications))
            
            self._selected_instance = iid

    def _set_selected_instance(self, property_model, instance):
        """

        Parameters
        ----------
        property_model:models.PropertyModel
        instance

        Returns
        -------

        """
        property_model.selected_instance = instance

    def _set_application_index(self, property_model, index):
        property_model.application_index = index

    def _rectangle_id(self, rectangle):
        return rectangle.id

    def _update_view(self, value_app_pairs):
        for ppt_value, app in value_app_pairs:
            view = self._get_view(app)
            view.set_value(ppt_value.value)

    def _get_view(self, application):
        return application.view()

    def clear_tool(self):
        self._interaction.unbind()

        dsp = self._display

        for instance in self._instances.values():
            dsp.delete(instance)

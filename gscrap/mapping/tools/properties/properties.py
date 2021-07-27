from gscrap.mapping.tools import tools

from gscrap.data import engine
from gscrap.data import attributes
from gscrap.data.rectangles import rectangles, rectangle_labels
from gscrap.data.labels import label_properties
from gscrap.data.properties import properties
from gscrap.data.properties import property_values_source as pvs
from gscrap.data.properties.values_sources import values_sources

from gscrap.mapping.tools.properties import models
from gscrap.mapping.tools.properties import value_generators

class Properties(tools.Tool):
    def __init__(self, main_view):
        self._canvas = main_view.canvas

    def start_tool(self, project):
        #load rectangle instances with properties

        with engine.connect() as connection:
            for label_property in label_properties.get_labels_with_properties(connection):

                property_ = label_property.property_

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

                source_type = values_sources.values_source_type(ppt_vs.value_source)

                count = 0

                for rct in rectangle_labels.get_rectangles_with_label(connection, label_property.label):
                    #todo: draw all instances on the canvas when we click on them, display all
                    # the properties associated with the rectangle.

                    for ist in rectangles.get_rectangle_instances(connection, rct):
                        ppt_model.add_rectangle_instance(ist)

                        count += 1

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



    def clear_tool(self):
        pass
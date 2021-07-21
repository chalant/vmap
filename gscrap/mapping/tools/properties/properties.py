from gscrap.mapping.tools import tools

from gscrap.data import engine
from gscrap.data.rectangles import rectangles, rectangle_labels
from gscrap.data.labels import label_properties
from gscrap.data.properties import properties

from gscrap.mapping.tools.properties import models

class Properties(tools.Tool):
    def __init__(self, main_view):
        self._canvas = main_view.canvas

    def start_tool(self, project):
        #load rectangle instances with properties

        with engine.connect() as connection:
            for label_property in label_properties.get_labels_with_properties(connection):
                #create a property setter based on attributes (unique, incremental, ...) and property
                # type (integer, string...)
                #if attribute is "unique", each rectangle instance will have a unique property
                # value.

                property_ = label_property.property_

                #todo: generate values of the property model based on property type,
                # and attributes
                for att in properties.get_property_attributes(connection, property_):
                    pass

                ppt_model = models.get_property_model(property_)

                for rct in rectangle_labels.get_rectangles_with_label(connection, label_property.label):
                    #todo: draw all instances on the canvas when we click on them, display all
                    # the properties associated with the rectangle.

                    for ist in rectangles.get_rectangle_instances(connection, rct):
                        ppt_model.add_rectangle_instance(ist)

    def clear_tool(self):
        pass
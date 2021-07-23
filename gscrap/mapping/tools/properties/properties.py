from gscrap.mapping.tools import tools

from gscrap.data import engine
from gscrap.data.rectangles import rectangles, rectangle_labels
from gscrap.data.labels import label_properties
from gscrap.data.properties import properties
from gscrap.data import attributes

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

                value_generator = models.IncrementalIntegerGenerator()
                value_store = models.SharedValueStore()
                ppt_type = properties.property_type(property_)
                values = []
                distinct = False

                for att in properties.get_property_attributes(connection, property_):
                    # distinct values must be generated
                    if att.attribute == attributes.DISTINCT:
                        distinct = True
                        value_store = models.DistinctValueStore()
                        if ppt_type == properties.INTEGER:
                            if att.attribute == attributes.RANDOM:
                                #todo: attributes can have parameters (integer incremental generator has from_ and increments)
                                value_generator = models.UniqueRandomIntegerGenerator()


                    elif att.attribute == attributes.SHARED:
                        if ppt_type == properties.BOOLEAN:
                            values.append(False)
                            values.append(True)



                ppt_model = models.get_property_model(property_, value_store)

                for rct in rectangle_labels.get_rectangles_with_label(connection, label_property.label):
                    #todo: draw all instances on the canvas when we click on them, display all
                    # the properties associated with the rectangle.

                    for ist in rectangles.get_rectangle_instances(connection, rct):
                        ppt_model.add_rectangle_instance(ist)

                        if distinct:
                            #generate a value for each rectangle instance
                            values.append(value_generator.next_value())

                #assign values to value store
                value_store.values = values



    def clear_tool(self):
        pass
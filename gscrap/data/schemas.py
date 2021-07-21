from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    Table,
    Float)

def build_schema(meta):
    # there is a hierarchy with project types (ex: game -> cards -> poker)
    Table(
        "project_types",
        meta,
        Column("project_type", String, primary_key=True),
        Column("parent_project_type", String, ForeignKey("project_types.project_type")),
        Column("has_child", Boolean, default=False)
    )

    Table(
        "project_type_components",
        meta,
        Column("project_type", String, ForeignKey("project_types.project_type"), nullable=False),
        Column("component_project_type", String, ForeignKey("project_types.project_type"), nullable=False)
    )

    Table(
        "projects",
        meta,
        Column("project_type", String, ForeignKey("project_types.project_type"), nullable=False),
        Column("project_name", String, primary_key=True),
        Column("height", Float(32), nullable=False),
        Column("width", Float(32), nullable=False)
    )

    # these are pre-populated by admin
    Table(
        "label_types",
        meta,
        Column("label_type", String, primary_key=True),
        # Column("project_type", ForeignKey("project_trectanglesypes.project_type"), nullable=False)
    )

    Table(
        "label_names",
        meta,
        Column("label_name", String, primary_key=True)
    )

    #pre-populated by admin
    Table(
        "labels",
        meta,
        Column("label_id", String, primary_key=True),
        Column("label_name", String, ForeignKey("label_names"), nullable=False),
        Column("label_type", String, ForeignKey("label_types.label_type"), nullable=False),
        # query: max == null || added < max
        Column("capture", Boolean, default=False), #whether to capture the label contents or not
        Column("max_instances", Integer), # maximum instances of this label
        Column("total", Integer, nullable=False, default=0), # tracks number of instances of this label
        # labels are bound to a project_type
        Column("project_type", ForeignKey("project_types.project_type"), nullable=False),
        # each label is mapped to a detection model
        Column("classifiable", Boolean, default=False)
    )

    Table(
        "label_components",
        meta,
        Column("label_id", String, ForeignKey("labels.label_id"), nullable=False),
        Column("component_id", String, ForeignKey("labels.label_id"), nullable=False),
        Column("lc_id", String, primary_key=True)
    )

    Table(
        "property_types",
        meta,
        Column("property_type", Integer, primary_key=True, nullable=False)
    )

    Table(
        "properties",
        meta,
        Column("property_name", String, primary_key=True, nullable=False)
    )

    Table(
        "property_values",
        meta,
        Column("property_name", String, ForeignKey("properties.property_name"), nullable=False),
        Column("property_type", Integer, ForeignKey("property_types.property_type"), nullable=False),
        Column("property_id", String, primary_key=True, nullable=False),
        Column("property_value", String, nullable=False),
    )

    Table(
        "attributes",
        meta,
        Column("attribute_name", Integer, primary_key=True)
    )

    Table(
        "property_attributes",
        meta,
        Column("property_type", Integer, ForeignKey("property_types.property_type"), nullable=False),
        Column("property_name", String, ForeignKey("properties.property_name"), nullable=False),
        Column("property_attribute", Integer, ForeignKey("attributes.attribute_name"), nullable=False)
    )

    Table(
        "label_properties",
        meta,
        Column("label_type", String, ForeignKey("label_types.label_type"), nullable=False),
        Column("label_name", String, ForeignKey("label_names.label"), nullable=False),
        Column("property_type", Integer, ForeignKey("property_types.property_type"), nullable=False),
        Column("property_name", String, ForeignKey("property_names.property_name"), nullable=False)
    )

    Table(
        "project_types_labels",
        meta,
        Column("project_type", ForeignKey("project_types.project_type"), nullable=False),
        Column("label_name", String, ForeignKey("label_names.label_name"), nullable=False),
        Column("label_type", String, ForeignKey("label_types.label_type"), nullable=False)
    )

    # multiple project per label
    Table(
        "rectangles",
        meta,
        Column("rectangle_id", String, primary_key=True),
        Column("height", Integer, nullable=False),
        Column("width", Integer, nullable=False),
        # project are per-project
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False))

    Table(
        "rectangle_instances",
        meta,
        # Column("instance_id", String, primary_key=True),
        #cz has multiple instances
        Column("r_instance_id", String, primary_key=True),
        Column("rectangle_id", String, ForeignKey("rectangles.rectangle_id"), nullable=False),
        Column("left", Integer, nullable=False),
        Column("top", Integer, nullable=False)
    )

    Table(
        "rectangle_instances_property_values",
        meta,
        Column("r_instance_id", String, ForeignKey("rectangle_instances.rectangle_id"), nullable=False),
        #no two rectangle instances share the save property value
        Column("property_id", String, ForeignKey("property_values.property_id"), nullable=False),
    )

    Table(
        "rectangle_components",
        meta,
        Column("r_instance_id", String, ForeignKey("rectangle_instances.r_instance_id"), nullable=False),
        Column("r_component_id", String, ForeignKey("rectangle_instances.r_instance_id"), nullable=False)
    )

    #provided by user
    Table(
        "label_instances",
        meta,
        Column("instance_id", String, primary_key=True),
        Column("instance_name", String, nullable=False),
        # Column("label_id", String, ForeignKey("labels.label_id")),
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False)
        #multiple label_instances can share the same cz
    )

    Table("rectangle_labels",
          meta,
          Column("rectangle_id", String, ForeignKey("rectangles.rectangle_id"), nullable=False),
          Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
          Column("label_type", String, ForeignKey("labels.label_type"), nullable=False))

    Table(
        "images",
        meta,
        Column("image_id", String, primary_key=True),
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
        # each image is mapped to an instance id
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False),
        Column("label_instance_name", String, nullable=False),
        Column("width", Integer, nullable=False),
        Column("height", Integer, nullable=False),
        Column("rectangle_id", String, ForeignKey('rectangles.rectangle_id'), nullable=False)
    )

    Table(
        "videos",
        meta,
        Column("video_id", String, primary_key=True),
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
        Column("fps", Integer, nullable=False),
        Column("byte_size", Integer, nullable=False),
        Column("width", Integer, nullable=False),
        Column("height", Integer, nullable=False),
        Column("mode", String, nullable=False),
        Column("frames", Integer, nullable=False),
        Column("total_time", String, nullable=False)
    )
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

    #pre-populated by admin
    Table(
        "labels",
        meta,
        Column("label_id", String, primary_key=True),
        Column("label_name", String, nullable=False),
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
        "rectangle_components",
        meta,
        Column("r_instance_id", String, ForeignKey("rectangle_instances.r_instance_id")),
        Column("r_component_id", String, ForeignKey("rectangle_instances.r_instance_id"))
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
          Column("rectangle_id", String, ForeignKey("rectangles.rectangle_id")),
          Column("label_name", String, ForeignKey("labels.label_name")),
          Column("label_type", String, ForeignKey("labels.label_type")))

    Table(
        "images",
        meta,
        Column("image_id", String, primary_key=True),
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
        # each image is mapped to an instance id
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False),
        Column("label_instance_name", String, nullable=False),
        Column("hash_key", String, nullable=False),
        Column("position", Integer, nullable=False)
    )

    Table(
        "videos",
        meta,
        Column("video_id", String, primary_key=True),
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
        Column("fps", Integer, nullable=False),
        Column("byte_size", Integer, nullable=False),
        Column("mode", String, nullable=False),
    )
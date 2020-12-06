from sqlalchemy import (
    MetaData,
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    Table)

meta = MetaData()

# there is a hierarchy with project types (ex: game -> cards -> poker)
project_types = Table(
    "project_types",
    meta,
    Column("project_type", String, primary_key=True),
    Column("parent_project_type", String, ForeignKey("project_types.project_type")),
    Column("has_child", Boolean, default=False)
)

project_type_components = Table(
    "project_type_components",
    meta,
    Column("project_type", String, ForeignKey("project_types.project_type"), nullable=False),
    Column("component_project_type", String, ForeignKey("project_types.project_type"), nullable=False)
)

projects = Table(
    "projects",
    meta,
    Column("project_type_id", String, ForeignKey("project_types.project_type_id")),
    Column("project_name", String, primary_key=True)
)

# these are pre-populated by admin
label_types = Table(
    "label_types",
    meta,
    Column("label_type", String, primary_key=True)
)

#pre-populated by admin
labels = Table(
    "labels",
    meta,
    Column("label_id", String, primary_key=True),
    Column("label_name", String, nullable=False),
    Column("label_type", String, ForeignKey("label_types.label_type"), nullable=False),
    #label instance can be within another label instance
    Column("parent_type", String, ForeignKey("labels.label_id")),
    Column("has_child", Boolean, default=False),
    # query: max == null || added < max
    Column("capture", Boolean, default=False), #whether to capture the label contents or not
    Column("max", Integer), # maximum instances of this label
    Column("total", Integer, nullable=False, default=0), # tracks number of instances of this label
    # labels are bound to a single project_type
    Column("project_type", ForeignKey("project_types.project_type"), nullable=False)
)

label_components = Table(
    "label_components",
    meta,
    Column("label_id", String, ForeignKey("labels.label_id"), nullable=False),
    Column("component_id", String, ForeignKey("labels.label_id"), nullable=False),
    Column("lc_id", String, primary_key=True)
)

# multiple rectangles per label
rectangles = Table(
    "rectangles",
    meta,
    Column("rectangle_id", String, primary_key=True),
    Column("height", Integer, nullable=False),
    Column("width", Integer, nullable=False),
    # rectangles are per-project
    Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
    Column("label_id", String, ForeignKey("labels.label_id"), nullable=False)
)

rectangle_instances = Table(
    "rectangle_instances",
    meta,
    # Column("instance_id", String, primary_key=True),
    #rectangle has multiple instances
    Column("rectangle_id", String, ForeignKey("requests.rectangle_id"), nullable=False),
    Column("left", Integer, nullable=False),
    Column("top", Integer, nullable=False)
)

#provided by user
label_instances = Table(
    "label_instances",
    meta,
    Column("instance_id", String, primary_key=True),
    #name of the instance (bet, call, etc.)
    Column("instance_name", String, nullable=False),
    Column("label_id", String, ForeignKey("labels.label_id"))
    #multiple label_instances can share the same rectangle
)

#label instances can map to multiple requests and vice-versa
# label_rectangle_instances = Table(
#     "label_rectangle_instances",
#     meta,
#     Column("rectangle_instance_id", String, ForeignKey("rectangle_instances.instance_id"), nullable=False),
#     Column("label_instance_id", String, ForeignKey("label_instances.instance_id"), nullable=False)
# )

images = Table(
    "images",
    meta,
    Column("image_id", String, primary_key=True),
    #multiple images per rectangle instance
    Column("rectangle_instance_id", String, ForeignKey("rectangle_instances.instance_id"), nullable=False),
    Column("image_path", String, nullable=False)
)
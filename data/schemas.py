from sqlalchemy import (
    MetaData,
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    Table,
    Float)

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
    Column("project_type", String, ForeignKey("project_types.project_type"), nullable=False),
    Column("project_name", String, primary_key=True),
    Column("height", Float(32), nullable=False),
    Column("width", Float(32), nullable=False)
)

filter_groups = Table(
    "filter_groups",
    meta,
    Column("name", String, primary_key=True)
)

blur = Table(
    "blur",
    meta,
    Column("id", String, primary_key=True),
    Column("group", String, ForeignKey("filter_group.name"), nullable=False),
    Column("type", String, nullable=False),
    Column("position", Integer, nullable=False)
)

color = Table(
    "color",
    meta,
    Column("id", String, primary_key=True),
    Column("group", String, ForeignKey("filter_group.name"), nullable=False),
    Column("type", String, nullable=False),
    Column("position", Integer, nullable=False)
)

resize = Table(
    "resize",
    meta,
    Column("id", String, primary_key=True),
    Column("group", String, ForeignKey("filter_group.name"), nullable=False),
    Column("type", String, nullable=False),
    Column("position", Integer, nullable=False)
)

threshold = Table(
    "threshold",
    meta,
    Column("id", String, primary_key=True),
    Column("group", String, ForeignKey("filter_group.name"), nullable=False),
    Column("type", String, nullable=False),
    Column("position", Integer, nullable=False)
)

filters = Table(
    "filters",
    meta,
    Column("id", String, primary_key=True),
    Column("group", String, ForeignKey("filter_group.name"), nullable=False),
    Column("type", String, nullable=False),
    Column("position", Integer, nullable=False)
)

gaussian_blur = Table(
    "gaussian_blur",
    meta,
    Column("id", String, primary_key=True),
    Column("blur_id", String, ForeignKey("filters.id"), nullable=False),
    Column("ksizeX", Float),
    Column("ksizeY", Float),
    Column("sigmaX", Float, nullable=False),
    Column("sigmaY", Float)
)

average_blur = Table(
    "average_blur",
    meta,
    Column("id", String, primary_key=True),
    Column("blur_id", String, ForeignKey("filters.id"), nullable=False),
    Column("ksizeX", Float),
    Column("ksizeY", Float)
)

median_blur = Table(
    "median_blur",
    meta,
    Column("id", String, primary_key=True),
    Column("blur_id", String, ForeignKey("filters.id"), nullable=False),
    Column("ksize", Float)
)

# these are pre-populated by admin
label_types = Table(
    "label_types",
    meta,
    Column("label_type", String, primary_key=True),
    # Column("project_type", ForeignKey("project_trectanglesypes.project_type"), nullable=False)
)

#pre-populated by admin
labels = Table(
    "labels",
    meta,
    Column("label_id", String, primary_key=True),
    Column("label_name", String, nullable=False),
    Column("label_type", String, ForeignKey("label_types.label_type"), nullable=False),
    # query: max == null || added < max
    Column("capture", Boolean, default=False), #whether to capture the label contents or not
    Column("max_instances", Integer), # maximum instances of this label
    Column("total", Integer, nullable=False, default=0), # tracks number of instances of this label
    # labels are bound to a single project_type
    Column("project_type", ForeignKey("project_types.project_type"), nullable=False),
    #preprocessing is done per label
    Column("preprocessing_name", ForeignKey("preprocessing.preprocessing_name"))
)

label_components = Table(
    "label_components",
    meta,
    Column("label_id", String, ForeignKey("labels.label_id"), nullable=False),
    Column("component_id", String, ForeignKey("labels.label_id"), nullable=False),
    Column("lc_id", String, primary_key=True)
)

# multiple project per label
rectangles = Table(
    "rectangles",
    meta,
    Column("rectangle_id", String, primary_key=True),
    Column("height", Integer, nullable=False),
    Column("width", Integer, nullable=False),
    # project are per-project
    Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
    Column("label_type", String, ForeignKey("label_types.label_type"), nullable=False),
    Column("label_name", String, ForeignKey("labels.label_name"), nullable=False)
)

rectangle_instances = Table(
    "rectangle_instances",
    meta,
    # Column("instance_id", String, primary_key=True),
    #cz has multiple instances
    Column("r_instance_id", String, primary_key=True),
    Column("rectangle_id", String, ForeignKey("rectangles.rectangle_id"), nullable=False),
    Column("left", Integer, nullable=False),
    Column("top", Integer, nullable=False)
)

rectangle_components = Table(
    "rectangle_components",
    meta,
    Column("r_instance_id", String, ForeignKey("rectangle_instances.r_instance_id")),
    Column("r_component_id", String, ForeignKey("rectangle_instances.r_instance_id"))
)

#provided by user
label_instances = Table(
    "label_instances",
    meta,
    Column("instance_id", String, primary_key=True),
    Column("instance_name", String, nullable=False),
    # Column("label_id", String, ForeignKey("labels.label_id")),
    Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
    Column("label_type", String, ForeignKey("labels.label_type"), nullable=False)
    #multiple label_instances can share the same cz
)

images = Table(
    "images",
    meta,
    Column("image_id", String, primary_key=True),
    Column("project_name", String, ForeignKey("projects.project_name"), nullable=False),
    # each image is mapped to an instance id
    Column("r_instance_id", String, ForeignKey("rectangle_instances.r_instance_id"), nullable=False),
    Column("hash_key", String, nullable=False),
    Column("position", Integer, nullable=False),
    Column("label_instance_name", String, nullable=False)
)

def create_all(engine):
    meta.create_all(engine)
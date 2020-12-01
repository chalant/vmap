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

games_types = Table(
    "games_types",
    meta,
    Column("game_type", String, primary_key=True)
)

# from settings we can pre-build labels in database => necessary in new project
settings = Table(
    "settings",
    meta,
    Column("game_type", String, ForeignKey("games_types.game_type"), nullable=False),
    Column("game_name", String, primary_key=True)
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
    Column("label_id", String, ForeignKey("labels.label_id"), nullable=False),
    #label instance can be within another label instance
    Column("parent_id", String, ForeignKey("labels.label_id")),
    Column("has_child", Boolean, default=False),
    # query: max == null || added < max
    Column("capture", Boolean, default=False), #whether to capture the label contents or not
    Column("max", Integer), # maximum instances of this label
    Column("total", Integer, nullable=False, default=0), # tracks number of instances of this label
    Column("game_type", String, ForeignKey("games_types.game_type"))
)


rectangles = Table(
    "requests",
    meta,
    Column("rectangle_id", String, primary_key=True),
    Column("height", Float(32), nullable=False),
    Column("width", Float(32), nullable=False)
)

rectangle_instances = Table(
    "rectangle_instances",
    meta,
    Column("instance_id", String, primary_key=True),
    #rectangle has multiple instances
    Column("rectangle_id", String, ForeignKey("requests.rectangle_id"), nullable=False),
    Column("ul_x", Float(32), nullable=False),
    Column("ul_y", Float(32), nullable=False)
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
label_rectangle_instances = Table(
    "label_rectangle_instances",
    meta,
    Column("rectangle_instance_id", String, ForeignKey("rectangle_instances.instance_id"), nullable=False),
    Column("label_instance_id", String, ForeignKey("label_instances.instance_id"), nullable=False)
)

images = Table(
    "images",
    meta,
    Column("image_id", String, primary_key=True),
    #multiple images per rectangle instance
    Column("rectangle_instance_id", String, ForeignKey("rectangle_instances.instance_id"), nullable=False),
    Column("image_path", String, nullable=False)
)
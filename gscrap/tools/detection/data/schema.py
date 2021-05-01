from sqlalchemy import Table, Column, String, ForeignKey, Integer, Float, Boolean

def build_schema(meta):
    Table(
        "models",
        meta,
        Column("name", String, primary_key=True),
    )

    #model associated with the label
    Table(
        "labels_models",
        meta,
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False),
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
        Column("model_name", String, ForeignKey("models.name"), nullable=False)
    )

    Table(
        "filter_groups",
        meta,
        Column("name", String, primary_key=True),
        Column("committed", Boolean, default=False)
    )

    #filter to label mapping
    Table(
        "labels_filters",
        meta,
        Column("filter_group", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False,),
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False)
    )

    Table(
        "filters",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("type", String, nullable=False),
        Column("name", String, nullable=False),
        Column("position", Integer, nullable=False)
    )

    Table(
        "threshold",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("thresh_value", Integer, nullable=False),
        Column("max_value", Integer, nullable=False),
        Column("type", String, nullable=False)
    )

    Table(
        "gaussian_blur",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksizeX", Float, nullable=False),
        Column("ksizeY", Float, nullable=False),
        Column("sigmaX", Float, nullable=False),
        Column("sigmaY", Float)
    )

    Table(
        "average_blur",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksizeX", Float),
        Column("ksizeY", Float)
    )

    Table(
        "median_blur",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksize", Float)
    )
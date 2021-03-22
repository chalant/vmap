from sqlalchemy import Table, Column, String, ForeignKey, Integer, Float, Boolean

def build_schema(meta):
    Table(
        "models",
        meta,
        Column("name", String, primary_key=True),
        Column("type", String, primary_key=True),
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
        Column("filter_group", String, ForeignKey("filter_groups.name")),
        Column("label_type", String, ForeignKey("labels.label_type")),
        Column("label_name", String, ForeignKey("labels.label_name"))
    )

    # labels and models mapping
    # todo
    # Table(
    #     "labels_models",
    #     meta,
    #
    # )

    Table(
        "filters",
        meta,
        Column("group", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("type", String, nullable=False),
        Column("name", String, nullable=False),
        Column("position", Integer, nullable=False)
    )

    Table(
        "threshold",
        meta,
        Column("group", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("thresh_value", Integer, nullable=False),
        Column("max_value", Integer, nullable=False),
        Column("type", String, nullable=False)
    )

    Table(
        "gaussian_blur",
        meta,
        Column("group", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksizeX", Float, nullable=False),
        Column("ksizeY", Float, nullable=False),
        Column("sigmaX", Float, nullable=False),
        Column("sigmaY", Float)
    )

    Table(
        "average_blur",
        meta,
        Column("group", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksizeX", Float),
        Column("ksizeY", Float)
    )

    Table(
        "median_blur",
        meta,
        Column("group", String, ForeignKey("filter_groups.name"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksize", Float)
    )
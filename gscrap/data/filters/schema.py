from sqlalchemy import Table, Column, String, ForeignKey, Integer, Float

def build_schema(meta):
    Table(
        "models",
        meta,
        Column("model_name", String, primary_key=True),
        #(could be tesseract, difference_matching etc.)
        Column("model_type", String, nullable=False)
    )

    #model parameters.
    Table(
        "difference_matching",
        meta,
        Column("threshold", Float, nullable=False),
        #one-to-one relationship with model name.
        Column("model_name", ForeignKey("models.model_name"), nullable=False, unique=True),
    )

    #model associated with the label
    Table(
        "labels_models",
        meta,
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False),
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
        Column("model_name", String, ForeignKey("models.model_name"), nullable=False),
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False)
    )

    Table(
        "filter_groups",
        meta,
        Column("group_id", String, primary_key=True),
    )
    #different groups can have the same parameters sequence.

    Table(
        "parameters",
        meta,
        Column("parameter_id", String, primary_key=True)
    )
    #difference groups

    #filter to label mapping
    Table(
        "labels_filters",
        meta,
        Column("filter_group", String, ForeignKey("filter_groups.group_id"), nullable=False),
        Column("parameter_id", String, ForeignKey("parameters.parameter_id"), nullable=False),
        Column("label_type", String, ForeignKey("labels.label_type"), nullable=False),
        Column("label_name", String, ForeignKey("labels.label_name"), nullable=False),
        Column("project_name", String, ForeignKey("projects.project_name"), nullable=False)
    )

    Table(
        "filters",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.group_id"), nullable=False),
        Column("parameter_id", String, ForeignKey("parameters.parameter_id"), nullable=False),
        Column("type", String, nullable=False),
        Column("name", String, nullable=False),
        Column("position", Integer, nullable=False)
    )

    Table(
        "threshold",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.group_id"), nullable=False),
        Column("parameter_id", String, ForeignKey("parameters.parameter_id"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("thresh_value", Integer, nullable=False),
        Column("max_value", Integer, nullable=False),
        Column("type", String, nullable=False)
    )

    Table(
        "gaussian_blur",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.group_id"), nullable=False),
        Column("parameter_id", String, ForeignKey("parameters.parameter_id"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksizeX", Float, nullable=False),
        Column("ksizeY", Float, nullable=False),
        Column("sigmaX", Float, nullable=False),
        Column("sigmaY", Float)
    )

    Table(
        "average_blur",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.group_id"), nullable=False),
        Column("parameter_id", String, ForeignKey("parameters.parameter_id"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksizeX", Float, nullable=False),
        Column("ksizeY", Float, nullable=False)
    )

    Table(
        "median_blur",
        meta,
        Column("group_name", String, ForeignKey("filter_groups.group_id"), nullable=False),
        Column("parameter_id", String, ForeignKey("parameters.parameter_id"), nullable=False),
        Column("position", Integer, ForeignKey("filters.position"), nullable=False),
        Column("ksize", Float, nullable=False)
    )
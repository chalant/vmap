from sqlalchemy import (
    Column,
    String,
    Integer,
    Table)

def build_schema(meta):
    Table(
        'project_scenes',
        meta,
        Column('scene_name', String, primary_key=True),
        Column('schema_name', String, nullable=False)
    )

    Table(
        "videos",
        meta,
        Column("video_id", String, primary_key=True),
        Column("fps", Integer, nullable=False),
        Column("byte_size", Integer, nullable=False),
        Column("width", Integer, nullable=False),
        Column("height", Integer, nullable=False),
        Column("mode", String, nullable=False),
        Column("frames", Integer, nullable=False),
        Column("total_time", String, nullable=False)
    )
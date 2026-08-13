
from datetime import timedelta

from feast import Entity
from feast import FeatureView
from feast import Field
from feast import FileSource

from feast.types import Float32
from feast.types import Int64
from feast.types import String


skill_gap_source = FileSource(
    name="skill_gap_parquet_source",
    path="data/skill_gap_features.parquet",
    timestamp_field="event_timestamp",
)


student = Entity(
    name="student",
    join_keys=["student_id"],
    description="Student skill-gap entity",
)


skill_gap_features = FeatureView(
    name="skill_gap_features",
    entities=[student],
    ttl=timedelta(days=3650),
    online=True,
    source=skill_gap_source,
    schema=[
        Field(
            name="curriculum_track",
            dtype=String
        ),

        Field(
            name="python_gap",
            dtype=Float32
        ),
        Field(
            name="sql_gap",
            dtype=Float32
        ),
        Field(
            name="ml_gap",
            dtype=Float32
        ),
        Field(
            name="cloud_gap",
            dtype=Float32
        ),
        Field(
            name="communication_gap",
            dtype=Float32
        ),

        Field(
            name="average_skill_gap",
            dtype=Float32
        ),
        Field(
            name="industry_skill_average",
            dtype=Float32
        ),

        Field(
            name="projects_completed",
            dtype=Int64
        ),
        Field(
            name="internship_months",
            dtype=Int64
        ),
        Field(
            name="certification_count",
            dtype=Int64
        ),
        Field(
            name="industry_experience_months",
            dtype=Int64
        ),

        Field(
            name="project_experience_score",
            dtype=Float32
        ),
        Field(
            name="internship_experience_score",
            dtype=Float32
        ),
        Field(
            name="certification_score",
            dtype=Float32
        ),
        Field(
            name="industry_experience_score",
            dtype=Float32
        ),
    ],
)

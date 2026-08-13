
from pathlib import Path
import pandas as pd
from IPython.display import display


INPUT_FILE = "curriculum_industry_skill_gap.csv"
OUTPUT_FILE = "data/skill_gap_features.parquet"


def main():
    Path("data").mkdir(exist_ok=True)

    df = pd.read_csv(INPUT_FILE)
    df["event_timestamp"] = pd.to_datetime(
        df["event_timestamp"]
    )

    skills = [
        "python",
        "sql",
        "ml",
        "cloud",
        "communication",
    ]

    for skill in skills:
        df[f"{skill}_gap"] = (
            df[f"{skill}_curriculum"]
            - df[f"{skill}_industry"]
        ).astype("float32")

    gap_columns = [
        f"{skill}_gap"
        for skill in skills
    ]

    industry_columns = [
        f"{skill}_industry"
        for skill in skills
    ]

    df["average_skill_gap"] = (
        df[gap_columns]
        .mean(axis=1)
        .astype("float32")
    )

    df["industry_skill_average"] = (
        df[industry_columns]
        .mean(axis=1)
        .astype("float32")
    )

    df["project_experience_score"] = (
        df["projects_completed"] / 8.0
    ).clip(0, 1).astype("float32")

    df["internship_experience_score"] = (
        df["internship_months"] / 12.0
    ).clip(0, 1).astype("float32")

    df["certification_score"] = (
        df["certification_count"] / 4.0
    ).clip(0, 1).astype("float32")

    df["industry_experience_score"] = (
        df["industry_experience_months"] / 36.0
    ).clip(0, 1).astype("float32")

    output_columns = [
        "student_id",
        "event_timestamp",
        "curriculum_track",

        "python_gap",
        "sql_gap",
        "ml_gap",
        "cloud_gap",
        "communication_gap",

        "average_skill_gap",
        "industry_skill_average",

        "projects_completed",
        "internship_months",
        "certification_count",
        "industry_experience_months",

        "project_experience_score",
        "internship_experience_score",
        "certification_score",
        "industry_experience_score",

        "target_readiness",
    ]

    feature_df = df[output_columns].copy()

    feature_df["student_id"] = (
        feature_df["student_id"].astype(str)
    )

    feature_df["curriculum_track"] = (
        feature_df["curriculum_track"].astype(str)
    )

    feature_df.to_parquet(
        OUTPUT_FILE,
        index=False
    )

    print("Created:", OUTPUT_FILE)
    print("Shape:", feature_df.shape)
    display(feature_df.head())


if __name__ == "__main__":
    main()

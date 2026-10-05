import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("transformer")


def transform_data(df):
    logger.info("Transformation started")
    data = df.copy()

    # Missing GPA: median of available GPA values.
    if data["gpa"].isna().any():
        median_gpa = data["gpa"].median()
        data["gpa"] = data["gpa"].fillna(median_gpa)

    # Missing attendance: business rule = 0 (not recorded means no confirmed attendance).
    data["attendance"] = data["attendance"].fillna(0)

    # Missing optional database fields.
    data["course"] = data["course"].fillna("Not Available")
    data["semester"] = data["semester"].fillna("Not Available")
    data["average_score"] = data["average_score"].fillna(0)
    data["total_courses"] = data["total_courses"].fillna(0).astype(int)

    data["performance_level"] = pd.cut(
        data["gpa"],
        bins=[-float("inf"), 2.0, 2.5, 3.0, 3.5, float("inf")],
        labels=["At Risk", "Acceptable", "Good", "Very Good", "Excellent"],
        right=False,
    ).astype(str)

    data["attendance_status"] = data["attendance"].apply(
        lambda x: "Good" if x >= 75 else "Low"
    )

    data["average_score"] = data["average_score"].round(2)
    data["gpa"] = data["gpa"].round(2)
    data["attendance"] = data["attendance"].round(2)

    return data

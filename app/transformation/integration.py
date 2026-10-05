import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("integration")


def integrate_data(csv_data, api_data, database_data):
    """Join the three sources using student_id."""
    logger.info("Data integration started")

    # One student can have multiple course records, so aggregate SQLite data.
    db_summary = (
        database_data.groupby("student_id", as_index=False)
        .agg(
            course=("course", lambda x: ", ".join(sorted(set(x.dropna().astype(str))))),
            semester=("semester", lambda x: ", ".join(sorted(set(x.dropna().astype(str))))),
            average_score=("score", "mean"),
            total_courses=("course", "count"),
        )
    )

    integrated = csv_data.merge(api_data, on="student_id", how="inner")
    integrated = integrated.merge(db_summary, on="student_id", how="left")

    integrated["source"] = "CSV + API + DATABASE"
    logger.info("Integrated records: %d", len(integrated))
    return integrated

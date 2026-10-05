import sqlite3
import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("database_source")


def extract_database(db_path):
    """Extract course enrollment data from SQLite."""
    logger.info("Database extraction started")
    query = """
        SELECT
            e.student_id,
            c.course_name AS course,
            c.credit_hours,
            e.semester,
            e.score
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
    """

    with sqlite3.connect(db_path) as connection:
        data = pd.read_sql_query(query, connection)

    logger.info("Database records: %d", len(data))
    return data

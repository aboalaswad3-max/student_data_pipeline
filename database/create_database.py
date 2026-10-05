import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "students.db"


def create_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS enrollments;
    DROP TABLE IF EXISTS courses;

    CREATE TABLE courses (
        course_id INTEGER PRIMARY KEY,
        course_name TEXT NOT NULL,
        credit_hours INTEGER NOT NULL
    );

    CREATE TABLE enrollments (
        student_id INTEGER,
        course_id INTEGER,
        semester TEXT,
        score REAL
    );
    """)

    courses = [
        (1, "Database Systems", 3),
        (2, "Python Programming", 3),
        (3, "Data Engineering", 3),
        (4, "Artificial Intelligence", 4),
    ]
    cursor.executemany(
        "INSERT INTO courses VALUES (?, ?, ?)", courses
    )

    enrollments = [
        (1001, 1, "2026-1", 90),
        (1001, 2, "2026-1", 87),
        (1002, 1, "2026-1", 95),
        (1002, 4, "2026-1", 91),
        (1003, 2, "2026-1", 78),
        (1003, 3, "2026-1", 80),
        (1004, 1, "2026-1", 72),
        (1005, 3, "2026-1", 88),
        (1006, 2, "2026-1", 92),
        (1007, 4, "2026-1", 99),
        (1008, 1, "2026-1", 76),
        (1009, 3, "2026-1", 55),
        (1010, 1, "2026-1", 84),
        (1011, 2, "2026-1", 79),
        (1007, 3, "2026-1", 120),  # intentional invalid score
    ]
    cursor.executemany(
        "INSERT INTO enrollments VALUES (?, ?, ?, ?)", enrollments
    )

    connection.commit()
    connection.close()
    print(f"Database created: {DB_PATH}")


if __name__ == "__main__":
    create_database()

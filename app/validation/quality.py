import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("quality")


def validate_student_source(df):
    """Return valid rows and rejected rows for the CSV source."""
    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    def add_error(mask, message):
        nonlocal errors
        errors.loc[mask] = errors.loc[mask].apply(
            lambda old: f"{old}; {message}" if old else message
        )

    add_error(data["student_id"].isna(), "Missing student_id")
    add_error(data["age"].isna(), "Missing age")
    add_error(~data["age"].isna() & ~data["age"].between(16, 80), "Invalid Age")
    add_error(data["student_name"].isna() | (data["student_name"].astype(str).str.strip() == ""), "Missing student_name")

    # Duplicate IDs are rejected after cleaning.
    duplicate_mask = data["student_id"].duplicated(keep=False) & data["student_id"].notna()
    add_error(duplicate_mask, "Duplicate student_id")

    rejected = data.loc[errors != ""].copy()
    rejected["error_reason"] = errors.loc[errors != ""].values
    valid = data.loc[errors == ""].copy()

    logger.info("Student validation: valid=%d rejected=%d", len(valid), len(rejected))
    return valid, rejected


def validate_api_source(df):
    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    def add_error(mask, message):
        nonlocal errors
        errors.loc[mask] = errors.loc[mask].apply(
            lambda old: f"{old}; {message}" if old else message
        )

    add_error(data["student_id"].isna(), "Missing student_id")
    add_error(~data["gpa"].isna() & ~data["gpa"].between(0, 4), "Invalid GPA")
    add_error(~data["attendance"].isna() & ~data["attendance"].between(0, 100), "Invalid Attendance")

    rejected = data.loc[errors != ""].copy()
    rejected["error_reason"] = errors.loc[errors != ""].values
    valid = data.loc[errors == ""].copy()
    return valid, rejected


def validate_database_source(df):
    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    def add_error(mask, message):
        nonlocal errors
        errors.loc[mask] = errors.loc[mask].apply(
            lambda old: f"{old}; {message}" if old else message
        )

    add_error(data["student_id"].isna(), "Missing student_id")
    add_error(~data["score"].isna() & ~data["score"].between(0, 100), "Invalid Score")

    rejected = data.loc[errors != ""].copy()
    rejected["error_reason"] = errors.loc[errors != ""].values
    valid = data.loc[errors == ""].copy()
    return valid, rejected


def validate_final_data(df):
    """Final quality check. Rows failing any final rule are rejected."""
    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    def add_error(mask, message):
        nonlocal errors
        errors.loc[mask] = errors.loc[mask].apply(
            lambda old: f"{old}; {message}" if old else message
        )

    add_error(data["student_id"].isna(), "Missing student_id")
    add_error(data["student_id"].duplicated(keep=False), "Duplicate student_id")
    add_error(~data["age"].between(16, 80), "Invalid Age")
    add_error(~data["gpa"].between(0, 4), "Invalid GPA")
    add_error(~data["attendance"].between(0, 100), "Invalid Attendance")

    rejected = data.loc[errors != ""].copy()
    rejected["error_reason"] = errors.loc[errors != ""].values
    valid = data.loc[errors == ""].copy()

    logger.info("Final validation: valid=%d rejected=%d", len(valid), len(rejected))
    return valid, rejected

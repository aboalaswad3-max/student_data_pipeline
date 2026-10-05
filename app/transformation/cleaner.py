import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("cleaner")


def normalize_column_names(df):
    data = df.copy()
    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return data


def clean_text_columns(df):
    data = df.copy()
    text_columns = data.select_dtypes(include="object").columns

    for column in text_columns:
        data[column] = data[column].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    # Normalize common text fields.
    for column in ["city", "major", "status", "course", "semester"]:
        if column in data.columns:
            data[column] = data[column].apply(
                lambda value: value.title() if isinstance(value, str) else value
            )

    return data


def clean_student_data(df):
    logger.info("Student cleaning started")
    data = normalize_column_names(df)
    data = clean_text_columns(data)

    if "student_id" in data.columns:
        data["student_id"] = pd.to_numeric(data["student_id"], errors="coerce").astype("Int64")
    if "age" in data.columns:
        data["age"] = pd.to_numeric(data["age"], errors="coerce")

    # Keep the first occurrence of duplicate student IDs.
    before = len(data)
    data = data.drop_duplicates(subset=["student_id"], keep="first")
    logger.info("Student duplicate records removed: %d", before - len(data))

    return data


def clean_api_data(df):
    data = normalize_column_names(df)
    data = clean_text_columns(data)

    for column in ["student_id", "gpa", "attendance"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    return data


def clean_database_data(df):
    data = normalize_column_names(df)
    data = clean_text_columns(df)
    for column in ["student_id", "score", "credit_hours"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data

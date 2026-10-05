import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("new_cleaner")


def clean_scraped_countries(df):
    logger.info("Web scraping cleaning started")
    data = df.copy()
    data.columns = data.columns.astype(str).str.strip().str.lower()

    for column in ["country", "capital"]:
        if column in data.columns:
            data[column] = data[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    if "population" in data.columns:
        data["population"] = pd.to_numeric(data["population"], errors="coerce")

    if "country" in data.columns:
        data = data.drop_duplicates(subset=["country"], keep="first")

    return data


def clean_orders(df):
    logger.info("MongoDB orders cleaning started")
    data = df.copy()
    data.columns = data.columns.astype(str).str.strip().str.lower()

    for column in ["order_id", "customer_id", "payment_method", "status"]:
        if column in data.columns:
            data[column] = data[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    if "payment_method" in data.columns:
        data["payment_method"] = data["payment_method"].apply(
            lambda value: value.title() if isinstance(value, str) else value
        )

    if "status" in data.columns:
        data["status"] = data["status"].apply(
            lambda value: value.upper() if isinstance(value, str) else value
        )

    if "total_amount" in data.columns:
        data["total_amount"] = pd.to_numeric(data["total_amount"], errors="coerce")

    if "created_at" in data.columns:
        data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce", utc=True)

    if "order_id" in data.columns:
        data = data.drop_duplicates(subset=["order_id"], keep="first")

    return data

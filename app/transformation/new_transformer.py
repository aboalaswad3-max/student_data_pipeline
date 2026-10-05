import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("new_transformer")


def transform_scraped_countries(df):
    logger.info("Web scraping transformation started")
    data = df.copy()
    data["population"] = data["population"].astype("int64")
    data["capital"] = data["capital"].replace({"None": None})
    return data


def transform_orders(df):
    logger.info("MongoDB orders transformation started")
    data = df.copy()
    data["total_amount"] = data["total_amount"].round(2)
    data["created_at"] = data["created_at"].apply(lambda value: value.isoformat() if pd.notna(value) else None)
    return data

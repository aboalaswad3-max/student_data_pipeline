import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("new_quality")


def _add_error(errors, mask, message):
    errors.loc[mask] = errors.loc[mask].apply(
        lambda old: f"{old}; {message}" if old else message
    )


def validate_scraped_countries(df):
    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    _add_error(errors, data["country"].isna() | (data["country"].astype(str).str.strip() == ""), "Missing country")
    _add_error(errors, data["population"].isna(), "Invalid population")
    _add_error(errors, data["population"].notna() & (data["population"] < 0), "Invalid population")

    rejected = data.loc[errors != ""].copy()
    rejected["error_reason"] = errors.loc[errors != ""].values
    valid = data.loc[errors == ""].copy()

    logger.info("Web scraping validation: valid=%d rejected=%d", len(valid), len(rejected))
    return valid, rejected


def validate_orders(df):
    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    _add_error(errors, data["order_id"].isna() | (data["order_id"].astype(str).str.strip() == ""), "Missing order_id")
    _add_error(errors, data["customer_id"].isna() | (data["customer_id"].astype(str).str.strip() == ""), "Missing customer_id")
    _add_error(errors, data["total_amount"].isna(), "Invalid total_amount")
    _add_error(errors, data["total_amount"].notna() & (data["total_amount"] < 0), "Invalid total_amount")
    _add_error(errors, data["created_at"].isna(), "Invalid created_at")

    rejected = data.loc[errors != ""].copy()
    rejected["error_reason"] = errors.loc[errors != ""].values
    valid = data.loc[errors == ""].copy()

    logger.info("MongoDB orders validation: valid=%d rejected=%d", len(valid), len(rejected))
    return valid, rejected

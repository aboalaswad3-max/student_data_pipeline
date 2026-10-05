import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("csv_source")


def extract_csv(file_path):
    """Read student data from CSV."""
    logger.info("CSV extraction started")
    data = pd.read_csv(file_path)
    logger.info("CSV records: %d", len(data))
    return data

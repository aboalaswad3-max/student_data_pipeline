import pandas as pd
from pymongo import MongoClient
from app.utils.logger import get_logger

logger = get_logger("mongo_source")


def extract_orders(uri="mongodb://localhost:27017/", database_name="sales", collection_name="orders"):
    """Extract orders from the existing MongoDB sales.orders collection."""
    logger.info("MongoDB extraction started: %s.%s", database_name, collection_name)

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[database_name][collection_name]
        records = list(collection.find({}, {"_id": 0}))
        data = pd.DataFrame(records)
        logger.info("MongoDB records: %d", len(data))
        return data
    finally:
        client.close()

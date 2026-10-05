import pandas as pd
from pymongo import MongoClient
from app.utils.logger import get_logger

logger = get_logger("mongo_writer")


def create_database(uri="mongodb://localhost:27017/", database_name="student_data", collections=None):
    """Create the MongoDB database/collections if they do not exist."""
    collections = collections or []
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        db = client[database_name]
        existing = set(db.list_collection_names())
        for name in collections:
            if name not in existing:
                db.create_collection(name)
        logger.info("MongoDB database ready: %s", database_name)
    finally:
        client.close()


def _clean_value(value):
    """Convert pandas-specific missing values into MongoDB-compatible values."""
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value.item() if hasattr(value, "item") else value


def save_dataframe(df, uri, database_name, collection_name):
    """Replace a destination collection with the processed records."""
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[database_name][collection_name]
        collection.delete_many({})

        records = [
            {column: _clean_value(value) for column, value in record.items()}
            for record in df.to_dict(orient="records")
        ]

        if records:
            collection.insert_many(records)

        logger.info("Saved %d records to MongoDB collection %s", len(records), collection_name)
    finally:
        client.close()

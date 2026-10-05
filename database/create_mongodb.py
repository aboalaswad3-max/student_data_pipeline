from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "student_data"
COLLECTIONS = ["countries_processed", "orders_processed"]


def create_mongodb():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        db = client[DATABASE_NAME]
        existing = set(db.list_collection_names())

        for collection_name in COLLECTIONS:
            if collection_name not in existing:
                db.create_collection(collection_name)

        print(f"MongoDB database ready: {DATABASE_NAME}")
        print("Collections:")
        for collection_name in COLLECTIONS:
            print(f"- {collection_name}")
    finally:
        client.close()


if __name__ == "__main__":
    create_mongodb()

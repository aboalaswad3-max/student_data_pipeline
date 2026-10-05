"""Run the two new independent sources only.

Source 1: Web Scraping -> clean -> validate -> transform -> MongoDB
Source 2: sales.orders -> clean -> validate -> transform -> MongoDB

The two sources are intentionally NOT integrated.
"""

from app.sources.web_scraping_source import extract_countries, SCRAPING_URL
from app.sources.mongo_source import extract_orders
from app.transformation.new_cleaner import clean_scraped_countries, clean_orders
from app.validation.new_quality import validate_scraped_countries, validate_orders
from app.transformation.new_transformer import transform_scraped_countries, transform_orders
from app.output.mongo_writer import create_database, save_dataframe


MONGO_URI = "mongodb://localhost:27017/"
MONGO_DATABASE = "student_data"


def run_web_scraping_pipeline():
    raw = extract_countries(SCRAPING_URL)
    cleaned = clean_scraped_countries(raw)
    valid, rejected = validate_scraped_countries(cleaned)
    final = transform_scraped_countries(valid)

    save_dataframe(final, MONGO_URI, MONGO_DATABASE, "countries_processed")

    print(f"Web Scraping: extracted={len(raw)}, valid={len(final)}, rejected={len(rejected)}")
    return final, rejected


def run_orders_pipeline():
    raw = extract_orders(
        uri=MONGO_URI,
        database_name="sales",
        collection_name="orders",
    )
    cleaned = clean_orders(raw)
    valid, rejected = validate_orders(cleaned)
    final = transform_orders(valid)

    save_dataframe(final, MONGO_URI, MONGO_DATABASE, "orders_processed")

    print(f"MongoDB orders: extracted={len(raw)}, valid={len(final)}, rejected={len(rejected)}")
    return final, rejected


def main():
    create_database(
        uri=MONGO_URI,
        database_name=MONGO_DATABASE,
        collections=["countries_processed", "orders_processed"],
    )

    run_web_scraping_pipeline()
    run_orders_pipeline()


if __name__ == "__main__":
    main()

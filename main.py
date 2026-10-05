from pathlib import Path
import time
import pandas as pd

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api

from app.sources.database_source import extract_database
from app.sources.web_scraping_source import extract_countries
from app.sources.mongo_source import extract_orders

from app.transformation.cleaner import (
    clean_student_data,
    clean_api_data,
    clean_database_data,
)
from app.transformation.new_cleaner import clean_scraped_countries, clean_orders

from app.validation.quality import (
    validate_student_source,
    validate_api_source,
    validate_database_source,
    validate_final_data,
)
from app.validation.new_quality import validate_scraped_countries, validate_orders

from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.transformation.new_transformer import transform_scraped_countries, transform_orders
from app.output.mongo_writer import create_database, save_dataframe
from app.utils.logger import get_logger

logger = get_logger("pipeline")

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data/raw/students.csv"
SQLITE_DB_PATH = BASE_DIR / "database/students.db"
API_URL = "http://127.0.0.1:8000/students"
SCRAPING_URL = "https://www.scrapethissite.com/pages/simple/"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DATABASE = "student_data"


def run_pipeline():
    start_time = time.time()
    logger.info("-----------------------------------")
    logger.info("PIPELINE EXECUTION STARTED")
    logger.info("-----------------------------------")

    # Prepare the MongoDB destination.
    create_database(
        uri=MONGO_URI,
        database_name=MONGO_DATABASE,
        collections=[
            "students_final",
            "students_rejected",
            "countries_processed",
            "orders_processed",
        ],
    )

    # ---------------------------------------------------------
    # Existing student pipeline: CSV + API + SQLite
    # ---------------------------------------------------------
    csv_raw = extract_csv(CSV_PATH)
    api_raw = extract_api(API_URL)
    db_raw = extract_database(SQLITE_DB_PATH)

    csv_clean = clean_student_data(csv_raw)
    api_clean = clean_api_data(api_raw)
    db_clean = clean_database_data(db_raw)

    csv_valid, csv_rejected = validate_student_source(csv_clean)
    api_valid, api_rejected = validate_api_source(api_clean)
    db_valid, db_rejected = validate_database_source(db_clean)

    rejected_parts = []
    for source, frame in [
        ("CSV", csv_rejected),
        ("API", api_rejected),
        ("DATABASE", db_rejected),
    ]:
        if not frame.empty:
            rejected = frame.copy()
            rejected["source"] = source
            rejected_parts.append(rejected)

    # The original three student sources continue to use their existing integration.
    integrated = integrate_data(csv_valid, api_valid, db_valid)
    transformed = transform_data(integrated)
    final_valid, final_rejected = validate_final_data(transformed)

    if not final_rejected.empty:
        final_rejected = final_rejected.copy()
        final_rejected["source"] = "FINAL_VALIDATION"
        rejected_parts.append(final_rejected)

    if rejected_parts:
        rejected_all = pd.concat(rejected_parts, ignore_index=True, sort=False)
    else:
        rejected_all = pd.DataFrame(columns=["student_id", "error_reason", "source"])

    save_dataframe(final_valid, MONGO_URI, MONGO_DATABASE, "students_final")
    save_dataframe(rejected_all, MONGO_URI, MONGO_DATABASE, "students_rejected")

    # ---------------------------------------------------------
    # New source 1: Web Scraping - independent pipeline
    # Only three fields are extracted: country, capital, population.
    # ---------------------------------------------------------
    countries_raw = extract_countries(SCRAPING_URL)
    countries_clean = clean_scraped_countries(countries_raw)
    countries_valid, countries_rejected = validate_scraped_countries(countries_clean)
    countries_final = transform_scraped_countries(countries_valid)
    save_dataframe(countries_final, MONGO_URI, MONGO_DATABASE, "countries_processed")

    # Rejected scraping rows are logged but are not mixed with another source.
    if not countries_rejected.empty:
        logger.warning("Web scraping rejected records: %d", len(countries_rejected))

    # ---------------------------------------------------------
    # New source 2: Existing MongoDB sales.orders - independent pipeline
    # No integration with the web-scraping data.
    # ---------------------------------------------------------
    orders_raw = extract_orders(
        uri=MONGO_URI,
        database_name="sales",
        collection_name="orders",
    )
    orders_clean = clean_orders(orders_raw)
    orders_valid, orders_rejected = validate_orders(orders_clean)
    orders_final = transform_orders(orders_valid)
    save_dataframe(orders_final, MONGO_URI, MONGO_DATABASE, "orders_processed")

    if not orders_rejected.empty:
        logger.warning("MongoDB orders rejected records: %d", len(orders_rejected))

    elapsed = time.time() - start_time

    logger.info("-----------------------------------")
    logger.info("PIPELINE EXECUTION SUMMARY")
    logger.info("CSV Records: %d", len(csv_raw))
    logger.info("API Records: %d", len(api_raw))
    logger.info("SQLite Records: %d", len(db_raw))
    logger.info("Integrated Student Records: %d", len(integrated))
    logger.info("Student Final Records: %d", len(final_valid))
    logger.info("Student Rejected Records: %d", len(rejected_all))
    logger.info("Scraped Country Records: %d", len(countries_raw))
    logger.info("Scraped Country Valid Records: %d", len(countries_final))
    logger.info("Scraped Country Rejected Records: %d", len(countries_rejected))
    logger.info("Mongo Orders Records: %d", len(orders_raw))
    logger.info("Mongo Orders Valid Records: %d", len(orders_final))
    logger.info("Mongo Orders Rejected Records: %d", len(orders_rejected))
    logger.info("Processing Time: %.2f seconds", elapsed)
    logger.info("-----------------------------------")

    return {
        "students_final": final_valid,
        "students_rejected": rejected_all,
        "countries_processed": countries_final,
        "orders_processed": orders_final,
    }


if __name__ == "__main__":
    run_pipeline()

import unittest
import pandas as pd
from unittest.mock import patch, Mock

from app.transformation.cleaner import clean_student_data
from app.transformation.new_cleaner import clean_scraped_countries, clean_orders
from app.validation.quality import validate_student_source, validate_api_source
from app.validation.new_quality import validate_scraped_countries, validate_orders
from app.transformation.integration import integrate_data
from app.sources.web_scraping_source import extract_countries


class PipelineTests(unittest.TestCase):

    def test_csv_loading_and_validation(self):
        data = pd.read_csv("data/raw/students.csv")
        cleaned = clean_student_data(data)
        valid, rejected = validate_student_source(cleaned)
        self.assertGreater(len(valid), 0)
        self.assertGreater(len(rejected), 0)

    def test_api_validation(self):
        data = pd.DataFrame([
            {"student_id": 1, "gpa": 3.0, "attendance": 90},
            {"student_id": 2, "gpa": 5.0, "attendance": 90},
        ])
        valid, rejected = validate_api_source(data)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)

    def test_integration(self):
        csv = pd.DataFrame([{
            "student_id": 1,
            "student_name": "A",
            "age": 20,
            "major": "CS",
            "city": "Sanaa",
        }])
        api = pd.DataFrame([{
            "student_id": 1,
            "gpa": 3.5,
            "attendance": 90,
            "status": "Active",
        }])
        db = pd.DataFrame([{
            "student_id": 1,
            "course": "Python",
            "credit_hours": 3,
            "semester": "2026-1",
            "score": 90,
        }])
        result = integrate_data(csv, api, db)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["student_id"], 1)

    def test_web_scraping_processing(self):
        data = pd.DataFrame([
            {"country": " Yemen ", "capital": "Sanaa", "population": "100"},
            {"country": "Yemen", "capital": "Sanaa", "population": "100"},
            {"country": "Test", "capital": "X", "population": "-5"},
        ])
        cleaned = clean_scraped_countries(data)
        valid, rejected = validate_scraped_countries(cleaned)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)

    def test_web_scraping_extracts_three_columns(self):
        html = """
        <div class="country">
            <h3 class="country-name">Yemen</h3>
            <span class="country-capital">Sanaa</span>
            <span class="country-population">28000000</span>
        </div>
        """
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = html

        with patch("app.sources.web_scraping_source.requests.get", return_value=response) as mock_get:
            result = extract_countries("https://example.com")

        mock_get.assert_called_once()
        self.assertEqual(list(result.columns), ["country", "capital", "population"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["country"], "Yemen")

    def test_orders_processing(self):
        data = pd.DataFrame([
            {
                "order_id": " ORD-1 ",
                "customer_id": " CUST-1 ",
                "total_amount": 25,
                "payment_method": "cash",
                "status": "pending",
                "created_at": "2026-10-05T10:00:00",
            },
            {
                "order_id": "ORD-2",
                "customer_id": "CUST-2",
                "total_amount": -15,
                "payment_method": "Cash",
                "status": "PENDING",
                "created_at": "invalid_timestamp",
            },
        ])
        cleaned = clean_orders(data)
        valid, rejected = validate_orders(cleaned)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(valid.iloc[0]["order_id"], "ORD-1")


if __name__ == "__main__":
    unittest.main()

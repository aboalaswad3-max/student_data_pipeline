import requests
import pandas as pd
from bs4 import BeautifulSoup
from app.utils.logger import get_logger

logger = get_logger("web_scraping_source")


SCRAPING_URL = "https://www.scrapethissite.com/pages/simple/"


def extract_countries(url=SCRAPING_URL, timeout=20):
    """Connect to the web page and extract exactly three fields per country."""
    logger.info("Web scraping extraction started: %s", url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Web scraping request failed: %s", exc)
        raise

    soup = BeautifulSoup(response.text, "html.parser")
    rows = []

    for country in soup.select("div.country"):
        name = country.select_one("h3.country-name")
        capital = country.select_one("span.country-capital")
        population = country.select_one("span.country-population")

        rows.append({
            "country": name.get_text(strip=True) if name else None,
            "capital": capital.get_text(strip=True) if capital else None,
            "population": population.get_text(strip=True) if population else None,
        })

    data = pd.DataFrame(rows, columns=["country", "capital", "population"])

    if data.empty:
        raise ValueError("Web scraping returned no country records")

    logger.info("Web scraping records extracted: %d", len(data))
    return data

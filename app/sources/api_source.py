import requests
import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("api_source")


def extract_api(url, timeout=5):
    """Get student academic data from a REST API."""
    logger.info("API extraction started")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        payload = response.json()

        if not payload:
            raise ValueError("API returned an empty response")

        if isinstance(payload, dict):
            payload = payload.get("data", [payload])

        data = pd.DataFrame(payload)
        logger.info("API records: %d", len(data))
        return data

    except requests.exceptions.Timeout as exc:
        logger.error("API timeout: %s", exc)
        raise
    except requests.exceptions.ConnectionError as exc:
        logger.error("API connection error: %s", exc)
        raise
    except requests.exceptions.HTTPError as exc:
        logger.error("API HTTP error: %s", exc)
        raise
    except ValueError as exc:
        logger.error("API JSON/data error: %s", exc)
        raise

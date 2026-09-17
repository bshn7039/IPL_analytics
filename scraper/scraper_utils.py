"""
Scraper Utility Functions
Contains common helper functions used across scrapers:
- get_headers(): Browser-like HTTP request headers
- safe_request(): Robust web page requests with retry logic
- polite_delay(): Anti-blocking random sleep delays
- save_raw_data(): Persist scraped data to CSV
"""
import os
import time
import random
import logging
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def get_headers():
    """Returns realistic HTTP request headers to prevent scraping blocks."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def safe_request(url, retries=3, delay=2, timeout=15):
    """
    Downloads a web page with retry and backoff logic.
    Returns requests.Response or None on complete failure.
    """
    session = requests.Session()
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching URL (attempt {attempt}/{retries}): {url}")
            response = session.get(url, headers=get_headers(), timeout=timeout)
            if response.status_code == 200:
                return response
            elif response.status_code in (403, 429):
                logger.warning(f"Rate limited or forbidden ({response.status_code}). Backing off...")
                time.sleep(delay * attempt * 2)
            else:
                logger.warning(f"Unexpected status code {response.status_code} for {url}")
        except requests.RequestException as e:
            logger.warning(f"Request error on attempt {attempt}: {e}")
            time.sleep(delay * attempt)
    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return None

def polite_delay(min_seconds=1.0, max_seconds=2.5):
    """Waits a randomized duration to avoid overwhelming servers."""
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

def save_raw_data(data, filename, raw_dir="data/raw"):
    """Saves a list of dictionaries or a DataFrame to a CSV file in data/raw."""
    os.makedirs(raw_dir, exist_ok=True)
    filepath = os.path.join(raw_dir, filename)
    if isinstance(data, pd.DataFrame):
        data.to_csv(filepath, index=False)
    elif isinstance(data, list):
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
    else:
        raise ValueError("Unsupported data type for saving. Expected list or DataFrame.")
    logger.info(f"Saved raw data ({len(data)} rows) to {filepath}")
    return filepath

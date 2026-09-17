"""
Selenium Dynamic Scraper
Automates headless browser sessions for JavaScript-rendered IPL pages
such as live standings tables and dynamic player profiles.
"""
import logging
import time
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def setup_driver(headless=True):
    """
    Instantiates a managed Chrome WebDriver instance with headless performance flags.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Selenium WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logger.warning(f"Failed to start Selenium WebDriver: {e}")
        return None

def scrape_points_table(driver, points_table_url="https://www.iplt20.com/points-table/men/2024"):
    """
    Renders dynamic JS points table and parses official standings.
    """
    if not driver:
        logger.warning("WebDriver not active. Falling back to default standings.")
        return get_fallback_points_table()

    try:
        driver.get(points_table_url)
        time.sleep(4)  # Wait for React / Angular / client hydration
        soup = BeautifulSoup(driver.page_source, "lxml")
        rows = soup.find_all("tr", class_=lambda c: c and "table" in str(c).lower())

        table_data = []
        for r in rows:
            cols = [td.get_text().strip() for td in r.find_all("td")]
            if len(cols) >= 6:
                table_data.append({
                    "team": cols[1],
                    "played": int(cols[2]) if cols[2].isdigit() else 14,
                    "won": int(cols[3]) if cols[3].isdigit() else 0,
                    "lost": int(cols[4]) if cols[4].isdigit() else 0,
                    "points": int(cols[5]) if cols[5].isdigit() else 0,
                    "nrr": cols[6] if len(cols) > 6 else "0.00"
                })
        if table_data:
            return table_data
    except Exception as e:
        logger.error(f"Selenium scraping failed: {e}")

    return get_fallback_points_table()

def get_fallback_points_table():
    """Provides representative season standings if live network or JS driver fails."""
    return [
        {"team": "KKR", "played": 14, "won": 9, "lost": 3, "points": 20, "nrr": "+1.428"},
        {"team": "SRH", "played": 14, "won": 8, "lost": 5, "points": 17, "nrr": "+0.414"},
        {"team": "RR", "played": 14, "won": 8, "lost": 5, "points": 17, "nrr": "+0.273"},
        {"team": "RCB", "played": 14, "won": 7, "lost": 7, "points": 14, "nrr": "+0.459"},
        {"team": "CSK", "played": 14, "won": 7, "lost": 7, "points": 14, "nrr": "+0.392"},
        {"team": "DC", "played": 14, "won": 7, "lost": 7, "points": 14, "nrr": "-0.377"},
        {"team": "LSG", "played": 14, "won": 7, "lost": 7, "points": 14, "nrr": "-0.667"},
        {"team": "GT", "played": 14, "won": 5, "lost": 7, "points": 12, "nrr": "-1.063"},
        {"team": "PBKS", "played": 14, "won": 5, "lost": 9, "points": 10, "nrr": "-0.354"},
        {"team": "MI", "played": 14, "won": 4, "lost": 10, "points": 8, "nrr": "-0.318"}
    ]

def close_driver(driver):
    """Safely closes the browser session and releases driver memory."""
    if driver:
        try:
            driver.quit()
            logger.info("Selenium WebDriver closed.")
        except Exception as e:
            logger.warning(f"Error while closing driver: {e}")

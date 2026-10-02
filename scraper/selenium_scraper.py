"""
IPL Official Site — Selenium Scraper
=====================================
TOOL 2 — Selenium + ChromeDriver (Dynamic/JS Scraping):
    iplt20.com loads its stats tables via JavaScript after the initial
    page load. A plain requests call returns an empty skeleton with no
    data. Selenium automates a real headless Chrome browser to:
        1. Navigate to iplt20.com/points-table/{season}
        2. Wait for the JS to render the points table
        3. Extract team standings (position, played, won, lost, pts, NRR)

This data is used to enrich the HomeScreen and Team Comparison pages
with official standings information.

Returns a DataFrame or None on failure (graceful — app still works).
"""

import time
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def _get_driver():
    """
    Initialises a headless Chrome WebDriver using webdriver-manager
    so no manual ChromeDriver installation is needed.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
    except Exception:
        # Fallback: rely on chromedriver being on PATH
        service = Service()

    options = Options()
    options.add_argument("--headless=new")          # headless — no visible window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    return webdriver.Chrome(service=service, options=options)


def scrape_points_table(season=2024, timeout=20):
    """
    Uses Selenium to scrape the IPL points table for a given season
    from iplt20.com (JavaScript-rendered page).

    Returns a DataFrame with columns:
        team_short, position, played, won, lost, tied, no_result, nrr, points

    Returns None if scraping fails (app continues without it).
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from scraper.parser import standardize_team_name

    url = f"https://www.iplt20.com/points-table/men/{season}"
    logger.info(f"[Selenium] Opening headless Chrome for: {url}")

    driver = None
    try:
        driver = _get_driver()
        driver.get(url)

        # Wait until the points table rows are rendered by JavaScript
        wait = WebDriverWait(driver, timeout)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table.ih-pt-tbl tbody tr, .ih-pt-lst-body")
            )
        )
        time.sleep(1.5)  # Extra wait for full JS hydration

        rows = []

        # ── Try standard HTML table first ────────────────────────────────────
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table.ih-pt-tbl tbody tr")

        if table_rows:
            logger.info(f"[Selenium] Found {len(table_rows)} rows in points table.")
            for idx, tr in enumerate(table_rows, start=1):
                cols = tr.find_elements(By.TAG_NAME, "td")
                if len(cols) < 7:
                    continue
                try:
                    team_raw = cols[1].text.strip()
                    rows.append({
                        "position":  idx,
                        "team_short": standardize_team_name(team_raw),
                        "played":    int(cols[2].text.strip() or 0),
                        "won":       int(cols[3].text.strip() or 0),
                        "lost":      int(cols[4].text.strip() or 0),
                        "tied":      int(cols[5].text.strip() or 0) if len(cols) > 7 else 0,
                        "no_result": int(cols[6].text.strip() or 0) if len(cols) > 8 else 0,
                        "nrr":       float(cols[-3].text.strip() or 0),
                        "points":    int(cols[-1].text.strip() or 0),
                        "season":    season,
                    })
                except (ValueError, IndexError):
                    continue

        # ── Fallback: try card/list layout ────────────────────────────────────
        if not rows:
            logger.info("[Selenium] Table not found, trying card layout...")
            items = driver.find_elements(By.CSS_SELECTOR, ".ih-pt-lst-body .ih-pt-lst-item")
            for idx, item in enumerate(items, start=1):
                try:
                    team_el  = item.find_element(By.CSS_SELECTOR, ".ih-pt-tm-nm")
                    team_raw = team_el.text.strip()
                    cells    = item.find_elements(By.CSS_SELECTOR, ".ih-pt-value")
                    played   = int(cells[0].text.strip() or 0) if len(cells) > 0 else 0
                    won      = int(cells[1].text.strip() or 0) if len(cells) > 1 else 0
                    lost     = int(cells[2].text.strip() or 0) if len(cells) > 2 else 0
                    nrr      = float(cells[3].text.strip() or 0) if len(cells) > 3 else 0.0
                    pts      = int(cells[-1].text.strip() or 0) if cells else 0
                    rows.append({
                        "position":  idx,
                        "team_short": standardize_team_name(team_raw),
                        "played":    played,
                        "won":       won,
                        "lost":      lost,
                        "tied":      0,
                        "no_result": 0,
                        "nrr":       nrr,
                        "points":    pts,
                        "season":    season,
                    })
                except Exception:
                    continue

        if not rows:
            logger.warning(f"[Selenium] No rows extracted from {url}")
            return None

        df = pd.DataFrame(rows)
        logger.info(f"[Selenium] Points table scraped: {len(df)} teams for {season}.")
        return df

    except Exception as e:
        logger.warning(f"[Selenium] Points table scraping failed: {e}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def scrape_top_batsmen_selenium(season=2024, limit=10, timeout=20):
    """
    Uses Selenium to scrape the top run-scorers list from iplt20.com/stats
    for the given season (JavaScript-rendered page).

    Returns a DataFrame or None on failure.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    url = f"https://www.iplt20.com/stats/{season}/batting"
    logger.info(f"[Selenium] Scraping top batsmen from: {url}")

    driver = None
    try:
        driver = _get_driver()
        driver.get(url)

        wait = WebDriverWait(driver, timeout)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table tbody tr, .ih-pcard")
            )
        )
        time.sleep(1.5)

        rows = []
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table.ih-stt-tbl tbody tr")
        for tr in table_rows[:limit]:
            cols = tr.find_elements(By.TAG_NAME, "td")
            if len(cols) < 6:
                continue
            try:
                rows.append({
                    "season":  season,
                    "player":  cols[1].text.strip(),
                    "team":    cols[2].text.strip(),
                    "matches": int(cols[3].text.strip() or 0),
                    "runs":    int(cols[4].text.strip() or 0),
                    "avg":     float(cols[5].text.strip() or 0),
                })
            except (ValueError, IndexError):
                continue

        return pd.DataFrame(rows) if rows else None

    except Exception as e:
        logger.warning(f"[Selenium] Batsmen scraping failed: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

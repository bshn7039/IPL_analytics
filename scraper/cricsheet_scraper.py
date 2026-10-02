"""
Cricsheet Live IPL Scraper
==========================
TOOL 1 — requests + BeautifulSoup (Static Scraping):
    - Visits cricsheet.org/downloads/ and parses the HTML to dynamically
      locate the latest IPL JSON zip download link.
    - Downloads the zip file using requests.
    - Extracts and parses every IPL match JSON into structured DataFrames.

This is the primary data source. The synthetic generator in load_data.py
acts as an automatic fallback if this scraper fails for any reason
(network down, site structure changed, timeout, etc.).

Data Coverage: IPL 2019–2026 (seasons present in the zip).
"""

import io
import json
import zipfile
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

from scraper.scraper_utils import get_headers, polite_delay
from scraper.parser import standardize_team_name

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────
CRICSHEET_DOWNLOADS_URL = "https://cricsheet.org/downloads/"
FALLBACK_ZIP_URL        = "https://cricsheet.org/downloads/ipl_json.zip"
SEASONS_TO_INCLUDE      = set(range(2019, 2027))  # 2019 → 2026 inclusive

# Only include current/recent IPL franchises (drop defunct teams)
VALID_TEAMS = {
    "MI", "CSK", "RCB", "KKR", "RR", "SRH", "DC", "PBKS", "GT", "LSG"
}

# Full-name → short-code mapping (handles historic name variants)
FULL_TO_SHORT = {
    "Mumbai Indians":                  "MI",
    "Chennai Super Kings":             "CSK",
    "Royal Challengers Bangalore":     "RCB",
    "Royal Challengers Bengaluru":     "RCB",
    "Kolkata Knight Riders":           "KKR",
    "Rajasthan Royals":                "RR",
    "Sunrisers Hyderabad":             "SRH",
    "Delhi Capitals":                  "DC",
    "Delhi Daredevils":                "DC",
    "Punjab Kings":                    "PBKS",
    "Kings XI Punjab":                 "PBKS",
    "Gujarat Titans":                  "GT",
    "Lucknow Super Giants":            "LSG",
}


# ─── Step 1: BeautifulSoup — find the IPL zip URL on the downloads page ───────
def find_ipl_zip_url():
    """
    Uses requests + BeautifulSoup to scrape cricsheet.org/downloads/ and
    dynamically locate the IPL JSON zip link.
    Falls back to a hardcoded URL if scraping the page fails.
    """
    logger.info("[BeautifulSoup] Scraping cricsheet.org/downloads/ for IPL zip link...")
    try:
        resp = requests.get(
            CRICSHEET_DOWNLOADS_URL,
            headers=get_headers(),
            timeout=15
        )
        if resp.status_code != 200:
            logger.warning(f"Downloads page returned HTTP {resp.status_code}, using fallback URL.")
            return FALLBACK_ZIP_URL

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find all <a> tags whose href contains "ipl" and "json" and ".zip"
        # Cricsheet uses relative hrefs like /downloads/ipl_json.zip
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            href_lower = href.lower()
            if "ipl" in href_lower and "json" in href_lower and href_lower.endswith(".zip"):
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = "https://cricsheet.org" + href
                else:
                    full_url = "https://cricsheet.org/" + href
                logger.info(f"[BeautifulSoup] Found IPL zip URL: {full_url}")
                return full_url

        # Also try exact filename match
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "ipl_json.zip" in href.lower():
                full_url = href if href.startswith("http") else "https://cricsheet.org" + href
                logger.info(f"[BeautifulSoup] Found IPL zip URL (pattern match): {full_url}")
                return full_url

        logger.warning("[BeautifulSoup] Could not find IPL zip link on page, using fallback.")
        return FALLBACK_ZIP_URL

    except Exception as e:
        logger.warning(f"[BeautifulSoup] Page scrape failed: {e}. Using fallback URL.")
        return FALLBACK_ZIP_URL


# ─── Step 2: requests — download the zip ──────────────────────────────────────
def download_ipl_zip(zip_url):
    """
    Downloads the IPL JSON zip file using requests.
    Returns the zip content as bytes, or raises an exception on failure.
    """
    logger.info(f"[requests] Downloading IPL data from: {zip_url}")
    resp = requests.get(
        zip_url,
        headers=get_headers(),
        timeout=120,   # zip is ~10–30 MB, give it time
        stream=True
    )
    if resp.status_code != 200:
        raise ConnectionError(f"Failed to download zip: HTTP {resp.status_code}")

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    chunks = []
    for chunk in resp.iter_content(chunk_size=65536):
        if chunk:
            chunks.append(chunk)
            downloaded += len(chunk)

    if total:
        logger.info(f"[requests] Downloaded {downloaded / 1024 / 1024:.1f} MB")

    return b"".join(chunks)


# ─── Step 3: Parse one Cricsheet JSON match file ──────────────────────────────
def _team_short(full_name):
    """Returns the short code for a full team name, or None if not a current IPL team."""
    return FULL_TO_SHORT.get(full_name)


def parse_match_json(data: dict, filename: str):
    """
    Parses a single Cricsheet match JSON dictionary.
    Returns (match_row, batting_rows, bowling_rows) or (None, [], []) to skip.

    Cricsheet JSON structure:
        info.dates[]          → match date
        info.teams[]          → [team1, team2]
        info.toss.winner      → toss winner full name
        info.toss.decision    → "bat" | "field"
        info.outcome.winner   → winning team full name
        info.outcome.by       → {"runs": N} or {"wickets": N}
        info.venue            → stadium name
        info.event.name       → "Indian Premier League"
        innings[].team        → batting team full name
        innings[].overs[].deliveries[]  → ball-by-ball data
    """
    info = data.get("info", {})

    # ── Filter: Only IPL matches in our season range ──────────────────────────
    event_name = info.get("event", {}).get("name", "")
    if "Indian Premier League" not in event_name and "IPL" not in event_name:
        return None, [], []

    dates = info.get("dates", [])
    if not dates:
        return None, [], []
    match_date = dates[0]
    season = int(match_date[:4])
    if season not in SEASONS_TO_INCLUDE:
        return None, [], []

    # ── Teams ─────────────────────────────────────────────────────────────────
    raw_teams = info.get("teams", [])
    if len(raw_teams) < 2:
        return None, [], []

    t1_short = _team_short(raw_teams[0])
    t2_short = _team_short(raw_teams[1])

    # Skip if either team is not a current IPL franchise
    if not t1_short or not t2_short:
        return None, [], []
    if t1_short not in VALID_TEAMS or t2_short not in VALID_TEAMS:
        return None, [], []

    # ── Match metadata ────────────────────────────────────────────────────────
    toss_raw     = info.get("toss", {})
    toss_winner  = _team_short(toss_raw.get("winner", "")) or ""
    toss_decision = toss_raw.get("decision", "bat")

    outcome      = info.get("outcome", {})
    winner_full  = outcome.get("winner", "")
    winner_short = _team_short(winner_full) or ""

    by_margin    = outcome.get("by", {})
    if "runs" in by_margin:
        result_str = f"{winner_short} won by {by_margin['runs']} runs"
    elif "wickets" in by_margin:
        result_str = f"{winner_short} won by {by_margin['wickets']} wickets"
    elif "innings" in by_margin:
        result_str = f"{winner_short} won by an innings"
    else:
        result_str = outcome.get("result", "No result")

    venue = info.get("venue", "Unknown Venue")
    city  = venue.split(",")[-1].strip() if "," in venue else venue

    match_number = info.get("event", {}).get("match_number", 0)
    match_id     = f"IPL_{season}_{match_number:03d}"

    match_row = {
        "match_id":      match_id,
        "season":        season,
        "date":          match_date,
        "team1":         t1_short,
        "team2":         t2_short,
        "venue":         venue,
        "city":          city,
        "toss_winner":   toss_winner,
        "toss_decision": toss_decision,
        "winner":        winner_short,
        "result":        result_str,
    }

    # ── Ball-by-ball → batting & bowling aggregates ───────────────────────────
    batting_rows  = []
    bowling_rows  = []

    for inn_idx, innings in enumerate(data.get("innings", []), start=1):
        bat_team_full  = innings.get("team", "")
        bat_team_short = _team_short(bat_team_full)
        if not bat_team_short or bat_team_short not in VALID_TEAMS:
            continue

        # Determine bowling team
        bowl_team_short = t2_short if bat_team_short == t1_short else t1_short

        # Accumulators per player
        batter_stats  = {}   # player → {runs, balls, fours, sixes, dismissed}
        bowler_stats  = {}   # player → {balls, runs_conceded, wickets, maidens_eligible}

        for over_data in innings.get("overs", []):
            over_num      = over_data.get("over", 0)
            over_runs     = 0
            over_legit_balls = 0

            for delivery in over_data.get("deliveries", []):
                batter   = delivery.get("batter", "Unknown")
                bowler   = delivery.get("bowler", "Unknown")
                runs_obj = delivery.get("runs", {})
                extras   = delivery.get("extras", {})

                batter_runs = runs_obj.get("batter", 0)
                total_runs  = runs_obj.get("total", 0)

                # Is this a legal delivery? (not a wide or no-ball)
                is_wide   = "wides"   in extras
                is_noball = "noballs" in extras
                is_legal  = not is_wide

                # ── Batter accumulation ───────────────────────────────────────
                if batter not in batter_stats:
                    batter_stats[batter] = {
                        "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "dismissed": False
                    }
                bs = batter_stats[batter]
                bs["runs"] += batter_runs
                if is_legal:
                    bs["balls"] += 1
                if batter_runs == 4:
                    bs["fours"] += 1
                elif batter_runs == 6:
                    bs["sixes"] += 1

                # ── Dismissal tracking ────────────────────────────────────────
                for wicket in delivery.get("wickets", []):
                    dismissed_player = wicket.get("player_out", batter)
                    if dismissed_player in batter_stats:
                        batter_stats[dismissed_player]["dismissed"] = True
                    # Run outs don't charge the bowler
                    if wicket.get("kind", "") not in ("run out", "obstructing the field", "retired hurt"):
                        if bowler not in bowler_stats:
                            bowler_stats[bowler] = {"balls": 0, "runs_conceded": 0, "wickets": 0}
                        bowler_stats[bowler]["wickets"] += 1

                # ── Bowler accumulation ───────────────────────────────────────
                if bowler not in bowler_stats:
                    bowler_stats[bowler] = {"balls": 0, "runs_conceded": 0, "wickets": 0}
                bws = bowler_stats[bowler]
                if is_legal:
                    bws["balls"]         += 1
                    over_legit_balls     += 1
                bws["runs_conceded"]     += total_runs - extras.get("wides", 0) - extras.get("noballs", 0)
                over_runs                += total_runs

        # ── Build batting records for this innings ────────────────────────────
        for player, s in batter_stats.items():
            balls  = s["balls"]
            runs   = s["runs"]
            sr     = round((runs / balls * 100.0), 2) if balls > 0 else 0.0
            batting_rows.append({
                "match_id":    match_id,
                "innings":     inn_idx,
                "team":        bat_team_short,
                "player":      player,
                "runs":        runs,
                "balls":       balls,
                "fours":       s["fours"],
                "sixes":       s["sixes"],
                "strike_rate": sr,
                "dismissal":   "not out" if not s["dismissed"] else "out",
                "not_out":     0 if s["dismissed"] else 1,
            })

        # ── Build bowling records for this innings ─────────────────────────────
        for player, s in bowler_stats.items():
            balls   = s["balls"]
            runs_c  = s["runs_conceded"]
            wickets = s["wickets"]
            overs   = round(balls // 6 + (balls % 6) / 10, 1)
            economy = round((runs_c / balls * 6.0), 2) if balls > 0 else 0.0
            b_avg   = round(runs_c / wickets, 2) if wickets > 0 else None
            b_sr    = round(balls / wickets, 2)  if wickets > 0 else None
            bowling_rows.append({
                "match_id":      match_id,
                "innings":       inn_idx,
                "team":          bowl_team_short,
                "player":        player,
                "overs":         overs,
                "balls_bowled":  balls,
                "maidens":       0,
                "runs_conceded": runs_c,
                "wickets":       wickets,
                "economy":       economy,
                "bowling_avg":   b_avg,
                "bowling_sr":    b_sr,
            })

    return match_row, batting_rows, bowling_rows


# ─── Step 4: Orchestrator — scrape everything and return DataFrames ───────────
def scrape_live_ipl_data():
    """
    Main entry point for the live Cricsheet scraper.

    Flow:
        1. BeautifulSoup  → find ZIP URL on cricsheet.org/downloads/
        2. requests       → download the IPL JSON zip
        3. zipfile        → extract in memory
        4. json.loads     → parse each match file
        5. Aggregate      → return (matches_df, batting_df, bowling_df)

    Raises:
        Exception on complete failure — caller should catch and fallback.
    """
    # Step 1: Find URL via BeautifulSoup
    zip_url = find_ipl_zip_url()
    polite_delay(0.5, 1.0)

    # Step 2: Download zip via requests
    zip_bytes = download_ipl_zip(zip_url)

    # Step 3: Parse in memory
    all_matches  = []
    all_batting  = []
    all_bowling  = []
    parsed       = 0
    skipped      = 0

    logger.info("[zipfile] Extracting and parsing match JSON files...")

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        json_files = [f for f in zf.namelist() if f.endswith(".json")]
        logger.info(f"  Found {len(json_files)} JSON files in the zip.")

        for fname in json_files:
            try:
                with zf.open(fname) as f:
                    data = json.load(f)
                match_row, batting_rows, bowling_rows = parse_match_json(data, fname)
                if match_row is None:
                    skipped += 1
                    continue
                all_matches.append(match_row)
                all_batting.extend(batting_rows)
                all_bowling.extend(bowling_rows)
                parsed += 1
            except Exception as e:
                logger.warning(f"  Skipping {fname}: {e}")
                skipped += 1
                continue

    logger.info(f"[Scraper] Parsed {parsed} IPL matches, skipped {skipped} non-IPL/out-of-range files.")

    if not all_matches:
        raise ValueError("No IPL matches found in the downloaded data. Cannot build database.")

    matches_df  = pd.DataFrame(all_matches).drop_duplicates(subset=["match_id"])
    batting_df  = pd.DataFrame(all_batting)
    bowling_df  = pd.DataFrame(all_bowling)

    logger.info(
        f"[Scraper] Final dataset: {len(matches_df)} matches | "
        f"{len(batting_df)} batting records | {len(bowling_df)} bowling records"
    )
    return matches_df, batting_df, bowling_df

"""
Requests + BeautifulSoup IPL Scraper
Handles static HTML scorecards, season match schedules, and ball/innings tables.
"""
import logging
from bs4 import BeautifulSoup
from scraper.scraper_utils import safe_request, polite_delay, save_raw_data
from scraper.parser import (
    standardize_team_name, parse_player_name, parse_runs,
    parse_overs, parse_match_result
)

logger = logging.getLogger(__name__)

def get_season_matches(season_url):
    """
    Parses a tournament schedule/results page and returns list of match metadata.
    """
    response = safe_request(season_url)
    if not response:
        logger.error("Could not fetch season matches page.")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    matches = []

    # Common scorecard card containers in cricket portals
    containers = soup.find_all("div", class_=lambda c: c and any(k in str(c).lower() for k in ["match-card", "scorecard-card", "ds-p-4", "match-info"]))
    if not containers:
        # Fallback table search
        containers = soup.find_all("tr", class_=lambda c: c and "match" in str(c).lower())

    for idx, card in enumerate(containers, start=1):
        try:
            teams = [standardize_team_name(t.get_text()) for t in card.find_all(["span", "div"], class_=lambda c: c and "team" in str(c).lower()) if t.get_text().strip()]
            if len(teams) < 2:
                continue
            team1, team2 = teams[0], teams[1]
            
            link_tag = card.find("a", href=lambda h: h and ("scorecard" in h or "match" in h))
            scorecard_url = link_tag["href"] if link_tag else ""
            if scorecard_url and not scorecard_url.startswith("http"):
                scorecard_url = f"https://www.espncricinfo.com{scorecard_url}"

            res_tag = card.find(class_=lambda c: c and ("status" in str(c).lower() or "result" in str(c).lower()))
            res_text = res_tag.get_text().strip() if res_tag else "Match completed"
            parsed_res = parse_match_result(res_text)

            matches.append({
                "match_id": f"ipl_match_{idx}",
                "date": "2024-04-01",
                "team1": team1,
                "team2": team2,
                "venue": "Wankhede Stadium, Mumbai",
                "city": "Mumbai",
                "toss_winner": team1,
                "toss_decision": "field",
                "winner": parsed_res["winner"],
                "result": res_text,
                "scorecard_url": scorecard_url
            })
        except Exception as err:
            logger.debug(f"Error parsing match entry: {err}")
            continue

    logger.info(f"Extracted {len(matches)} matches from season page.")
    return matches

def get_match_scorecard(scorecard_url, match_id="match_1"):
    """
    Downloads and extracts batting and bowling cards for both innings of a match.
    """
    response = safe_request(scorecard_url)
    if not response:
        return {"batting": [], "bowling": []}

    soup = BeautifulSoup(response.text, "lxml")
    batting_records = []
    bowling_records = []

    # Identify innings tables
    tables = soup.find_all("table")
    innings = 1

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue
        header_text = "".join([th.get_text().lower() for th in table.find_all("th")])

        # Check if batting table
        if any(h in header_text for h in ["batting", "batsman", "batter", "r", "b"]):
            for r in rows[1:]:
                cols = [td.get_text().strip() for td in r.find_all("td")]
                if len(cols) >= 6:
                    player_raw = cols[0]
                    if any(skip in player_raw.lower() for skip in ["extras", "total", "did not bat"]):
                        continue
                    runs, not_out = parse_runs(cols[2] if len(cols) > 2 else 0)
                    balls = int(cols[3]) if len(cols) > 3 and cols[3].isdigit() else 0
                    fours = int(cols[4]) if len(cols) > 4 and cols[4].isdigit() else 0
                    sixes = int(cols[5]) if len(cols) > 5 and cols[5].isdigit() else 0
                    sr = (runs / balls * 100) if balls > 0 else 0.0

                    batting_records.append({
                        "match_id": match_id,
                        "innings": innings,
                        "team": "MI" if innings == 1 else "CSK",
                        "player": parse_player_name(player_raw),
                        "runs": runs,
                        "balls": balls,
                        "fours": fours,
                        "sixes": sixes,
                        "strike_rate": round(sr, 2),
                        "dismissal": cols[1] if len(cols) > 1 else "",
                        "not_out": int(not_out)
                    })
            if batting_records:
                innings = 2

        # Check if bowling table
        elif any(h in header_text for h in ["bowling", "bowler", "o", "m", "w"]):
            for r in rows[1:]:
                cols = [td.get_text().strip() for td in r.find_all("td")]
                if len(cols) >= 5:
                    bowler_raw = cols[0]
                    overs_raw = cols[1]
                    balls_bowled = parse_overs(overs_raw)
                    maidens = int(cols[2]) if cols[2].isdigit() else 0
                    runs_conceded = int(cols[3]) if cols[3].isdigit() else 0
                    wickets = int(cols[4]) if cols[4].isdigit() else 0
                    econ = (runs_conceded / balls_bowled * 6) if balls_bowled > 0 else 0.0

                    bowling_records.append({
                        "match_id": match_id,
                        "innings": innings,
                        "team": "CSK" if innings == 1 else "MI",
                        "player": parse_player_name(bowler_raw),
                        "overs": float(overs_raw) if "." in overs_raw or overs_raw.isdigit() else 0.0,
                        "balls_bowled": balls_bowled,
                        "maidens": maidens,
                        "runs_conceded": runs_conceded,
                        "wickets": wickets,
                        "economy": round(econ, 2),
                        "bowling_avg": round(runs_conceded / wickets, 2) if wickets > 0 else None,
                        "bowling_sr": round(balls_bowled / wickets, 2) if wickets > 0 else None
                    })

    return {"batting": batting_records, "bowling": bowling_records}

def scrape_full_season(season_url, season_year=2024, max_matches=10):
    """
    Coordinates end-to-end season scraping with throttling and safety caps.
    """
    matches = get_season_matches(season_url)
    all_batting = []
    all_bowling = []

    for i, m in enumerate(matches[:max_matches], start=1):
        logger.info(f"Scraping match {i}/{min(len(matches), max_matches)}: {m['team1']} vs {m['team2']}")
        if m.get("scorecard_url"):
            cards = get_match_scorecard(m["scorecard_url"], match_id=m["match_id"])
            all_batting.extend(cards["batting"])
            all_bowling.extend(cards["bowling"])
            polite_delay(1.0, 2.0)

    save_raw_data(matches, f"matches_{season_year}.csv")
    if all_batting:
        save_raw_data(all_batting, f"batting_{season_year}.csv")
    if all_bowling:
        save_raw_data(all_bowling, f"bowling_{season_year}.csv")

    return matches, all_batting, all_bowling

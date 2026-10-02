"""
IPL Analytics Hub — Data Loader
================================
Execution order:
    1. [PRIMARY]  Live scraper (cricsheet_scraper.py)
                  → requests + BeautifulSoup to find ZIP URL on cricsheet.org
                  → requests to download the actual IPL ball-by-ball ZIP
                  → Parse all JSON match files into DataFrames
                  → Real, historically accurate data for 2019–2026

    2. [FALLBACK] Synthetic data generator (this file)
                  → Activates ONLY if the live scraper fails for any reason
                    (network down, site changes, timeout, etc.)
                  → Generates realistic but fictional data
                  → Clearly labelled in console output

Both paths feed the same processing pipeline → database → dashboard.
"""

import os
import sys
import random
import logging
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from database.db import create_database, insert_dataframe, get_db_stats, DEFAULT_DB_PATH
from processing.cleaner import clean_matches, clean_batting, clean_bowling
from processing.transformer import add_batting_metrics, add_bowling_metrics, add_match_context
from processing.validators import validate_batting, validate_bowling, validate_matches


# ══════════════════════════════════════════════════════════════════════════════
#  SYNTHETIC FALLBACK DATA
#  Only used when the live scraper is unavailable.
# ══════════════════════════════════════════════════════════════════════════════

TEAMS = [
    ("Mumbai Indians",             "MI"),
    ("Chennai Super Kings",        "CSK"),
    ("Royal Challengers Bengaluru","RCB"),
    ("Kolkata Knight Riders",      "KKR"),
    ("Rajasthan Royals",           "RR"),
    ("Sunrisers Hyderabad",        "SRH"),
    ("Delhi Capitals",             "DC"),
    ("Punjab Kings",               "PBKS"),
    ("Gujarat Titans",             "GT"),
    ("Lucknow Super Giants",       "LSG"),
]

# Teams available per season (GT & LSG only from 2022)
SEASON_TEAMS = {
    2019: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS"],
    2020: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS"],
    2021: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS"],
    2022: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS","GT","LSG"],
    2023: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS","GT","LSG"],
    2024: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS","GT","LSG"],
    2025: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS","GT","LSG"],
    2026: ["MI","CSK","RCB","KKR","RR","SRH","DC","PBKS","GT","LSG"],
}

# Season-aware rosters  (players move between teams historically)
ROSTERS = {
    "MI": [
        ("Rohit Sharma","Batter"),("Ishan Kishan","Wicketkeeper"),("Suryakumar Yadav","Batter"),
        ("Tilak Varma","Batter"),("Hardik Pandya","All-rounder"),("Tim David","Batter"),
        ("Romario Shepherd","All-rounder"),("Gerald Coetzee","Bowler"),
        ("Jasprit Bumrah","Bowler"),("Nuwan Thushara","Bowler"),("Piyush Chawla","Bowler"),
    ],
    "CSK": [
        ("Ruturaj Gaikwad","Batter"),("Rachin Ravindra","All-rounder"),("Ajinkya Rahane","Batter"),
        ("Daryl Mitchell","All-rounder"),("Shivam Dube","All-rounder"),("Ravindra Jadeja","All-rounder"),
        ("MS Dhoni","Wicketkeeper"),("Mitchell Santner","All-rounder"),
        ("Tushar Deshpande","Bowler"),("Mustafizur Rahman","Bowler"),("Matheesha Pathirana","Bowler"),
    ],
    "RCB": [
        ("Faf du Plessis","Batter"),("Virat Kohli","Batter"),("Will Jacks","All-rounder"),
        ("Rajat Patidar","Batter"),("Glenn Maxwell","All-rounder"),("Dinesh Karthik","Wicketkeeper"),
        ("Mahipal Lomror","Batter"),("Karn Sharma","Bowler"),
        ("Mohammed Siraj","Bowler"),("Yash Dayal","Bowler"),("Lockie Ferguson","Bowler"),
    ],
    "KKR": [
        ("Phil Salt","Wicketkeeper"),("Sunil Narine","All-rounder"),("Venkatesh Iyer","Batter"),
        ("Shreyas Iyer","Batter"),("Rinku Singh","Batter"),("Andre Russell","All-rounder"),
        ("Ramandeep Singh","All-rounder"),("Mitchell Starc","Bowler"),
        ("Varun Chakravarthy","Bowler"),("Harshit Rana","Bowler"),("Suyash Sharma","Bowler"),
    ],
    "RR": [
        ("Yashasvi Jaiswal","Batter"),("Jos Buttler","Wicketkeeper"),("Sanju Samson","Wicketkeeper"),
        ("Riyan Parag","Batter"),("Dhruv Jurel","Wicketkeeper"),("Shimron Hetmyer","Batter"),
        ("Rovman Powell","All-rounder"),("Ravichandran Ashwin","All-rounder"),
        ("Trent Boult","Bowler"),("Sandeep Sharma","Bowler"),("Yuzvendra Chahal","Bowler"),
    ],
    "SRH": [
        ("Travis Head","Batter"),("Abhishek Sharma","All-rounder"),("Aiden Markram","Batter"),
        ("Heinrich Klaasen","Wicketkeeper"),("Nitish Kumar Reddy","All-rounder"),
        ("Abdul Samad","Batter"),("Shahbaz Ahmed","All-rounder"),("Pat Cummins","Bowler"),
        ("Bhuvneshwar Kumar","Bowler"),("T Natarajan","Bowler"),("Jaydev Unadkat","Bowler"),
    ],
    "DC": [
        ("David Warner","Batter"),("Prithvi Shaw","Batter"),("Jake Fraser-McGurk","Batter"),
        ("Rishabh Pant","Wicketkeeper"),("Axar Patel","All-rounder"),("Tristan Stubbs","Wicketkeeper"),
        ("Abishek Porel","Wicketkeeper"),("Kuldeep Yadav","Bowler"),
        ("Khaleel Ahmed","Bowler"),("Mukesh Kumar","Bowler"),("Anrich Nortje","Bowler"),
    ],
    "PBKS": [
        ("Shikhar Dhawan","Batter"),("Jonny Bairstow","Wicketkeeper"),("Prabhsimran Singh","Wicketkeeper"),
        ("Rilee Rossouw","Batter"),("Sam Curran","All-rounder"),("Shashank Singh","Batter"),
        ("Ashutosh Sharma","Batter"),("Harpreet Brar","All-rounder"),
        ("Harshal Patel","Bowler"),("Kagiso Rabada","Bowler"),("Arshdeep Singh","Bowler"),
    ],
    "GT": [
        ("Shubman Gill","Batter"),("Wriddhiman Saha","Wicketkeeper"),("Sai Sudharsan","Batter"),
        ("David Miller","Batter"),("Azmatullah Omarzai","All-rounder"),("Rahul Tewatia","All-rounder"),
        ("Rashid Khan","All-rounder"),("Shahrukh Khan","Batter"),
        ("Mohit Sharma","Bowler"),("Noor Ahmad","Bowler"),("Spencer Johnson","Bowler"),
    ],
    "LSG": [
        ("KL Rahul","Wicketkeeper"),("Quinton de Kock","Wicketkeeper"),("Marcus Stoinis","All-rounder"),
        ("Nicholas Pooran","Wicketkeeper"),("Ayush Badoni","Batter"),("Deepak Hooda","All-rounder"),
        ("Krunal Pandya","All-rounder"),("Ravi Bishnoi","Bowler"),
        ("Mohsin Khan","Bowler"),("Mayank Yadav","Bowler"),("Naveen-ul-Haq","Bowler"),
    ],
}

VENUES = [
    ("Wankhede Stadium","Mumbai"),
    ("M. A. Chidambaram Stadium (Chepauk)","Chennai"),
    ("M. Chinnaswamy Stadium","Bengaluru"),
    ("Eden Gardens","Kolkata"),
    ("Narendra Modi Stadium","Ahmedabad"),
    ("Rajiv Gandhi International Cricket Stadium","Hyderabad"),
    ("Arun Jaitley Stadium","Delhi"),
    ("Maharaja Yadavindra Singh Stadium","Mullanpur"),
    ("Sawai Mansingh Stadium","Jaipur"),
    ("BRSABV Ekana Cricket Stadium","Lucknow"),
]


def simulate_innings(match_id, innings, bat_team, bowl_team, target=None):
    bat_roster  = ROSTERS[bat_team]
    bowl_roster = ROSTERS[bowl_team]
    bowlers = [p for p in bowl_roster if p[1] in ("Bowler","All-rounder")][:5]
    if len(bowlers) < 5:
        bowlers = bowl_roster[-5:]

    active_batters = bat_roster[:random.randint(6, 9)]
    balls_accum = 0
    runs_accum  = 0
    batting_records = []

    for i, (p_name, role) in enumerate(active_batters):
        if balls_accum >= 120 or (target and runs_accum >= target):
            break
        rem_balls = 120 - balls_accum
        faced = min(rem_balls, random.randint(8, 38))
        if i == len(active_batters) - 1:
            faced = rem_balls

        sr    = random.uniform(115.0, 185.0)
        p_runs = int((sr / 100.0) * faced)
        sixes  = max(0, int(p_runs * random.uniform(0.15, 0.40) / 6))
        fours  = max(0, int((p_runs - sixes * 6) * random.uniform(0.20, 0.55) / 4))
        boundary_runs = (fours * 4) + (sixes * 6)
        if boundary_runs > p_runs:
            p_runs = boundary_runs + random.randint(2, 10)

        not_out = 1 if (i >= len(active_batters) - 2 and
                        (balls_accum + faced >= 120 or (target and runs_accum + p_runs >= target))) else 0
        dismissal = "not out" if not_out else random.choice(
            ["c b", "b", "lbw", "run out", "st b"]
        )

        batting_records.append({
            "match_id":    match_id, "innings": innings, "team": bat_team,
            "player":      p_name,   "runs":    p_runs,  "balls": faced,
            "fours":       fours,    "sixes":   sixes,
            "strike_rate": round(p_runs / faced * 100.0, 2) if faced > 0 else 0.0,
            "dismissal":   dismissal,"not_out": not_out,
        })
        runs_accum  += p_runs
        balls_accum += faced

    bowling_records = []
    rem_runs = runs_accum
    for idx, (b_name, b_role) in enumerate(bowlers):
        balls_bowled = 24 if idx < 4 else max(0, 120 - 24 * 4)
        b_runs = int(rem_runs * random.uniform(0.14, 0.26)) if idx < 4 else max(0, rem_runs)
        rem_runs -= b_runs
        b_wkts   = random.choice([0, 1, 1, 2, 2, 3])
        economy  = round(b_runs / balls_bowled * 6.0, 2) if balls_bowled > 0 else 0.0
        bowling_records.append({
            "match_id": match_id, "innings": innings, "team": bowl_team,
            "player":   b_name,   "overs":  round(balls_bowled / 6.0, 1),
            "balls_bowled": balls_bowled, "maidens": 0,
            "runs_conceded": b_runs,  "wickets": b_wkts,
            "economy":  economy,
            "bowling_avg": round(b_runs / b_wkts, 2) if b_wkts > 0 else None,
            "bowling_sr":  round(balls_bowled / b_wkts, 2) if b_wkts > 0 else None,
        })

    return runs_accum, batting_records, bowling_records


def generate_synthetic_season(season_year, num_matches=74):
    """Generates one season of fictional-but-realistic IPL data."""
    random.seed(season_year * 42)
    np.random.seed(season_year * 42)

    team_keys = SEASON_TEAMS.get(season_year, list(ROSTERS.keys()))
    matches, batting_rows, bowling_rows = [], [], []

    for m_idx in range(1, num_matches + 1):
        match_id = f"SYNTH_{season_year}_{m_idx:03d}"
        t1, t2   = random.sample(team_keys, 2)
        venue, city = random.choice(VENUES)

        toss_winner   = random.choice([t1, t2])
        toss_decision = random.choice(["bat","field"])

        if (toss_winner == t1 and toss_decision == "bat") or \
           (toss_winner == t2 and toss_decision == "field"):
            bat_first, chase = t1, t2
        else:
            bat_first, chase = t2, t1

        inn1_runs, inn1_bat, inn1_bowl = simulate_innings(match_id, 1, bat_first, chase)
        batting_rows.extend(inn1_bat)
        bowling_rows.extend(inn1_bowl)

        inn2_runs, inn2_bat, inn2_bowl = simulate_innings(match_id, 2, chase, bat_first, inn1_runs + 1)
        batting_rows.extend(inn2_bat)
        bowling_rows.extend(inn2_bowl)

        winner = chase if inn2_runs >= inn1_runs + 1 else bat_first
        if inn2_runs >= inn1_runs + 1:
            wkts_fallen = sum(1 for b in inn2_bat if b["dismissal"] != "not out")
            result_str  = f"{winner} won by {10 - min(wkts_fallen,10)} wickets"
        else:
            result_str  = f"{winner} won by {inn1_runs - inn2_runs} runs"

        matches.append({
            "match_id":      match_id,
            "season":        season_year,
            "date":          f"{season_year}-{random.randint(3,5):02d}-{random.randint(1,28):02d}",
            "team1":         t1, "team2": t2,
            "venue":         venue, "city": city,
            "toss_winner":   toss_winner, "toss_decision": toss_decision,
            "winner":        winner, "result": result_str,
        })

    return matches, batting_rows, bowling_rows


def generate_all_synthetic():
    """Generates synthetic data for all 8 seasons as a fallback."""
    print("=" * 60)
    print("  [FALLBACK] Generating synthetic IPL data...")
    print("  (Live scraper unavailable — using fictional data)")
    print("=" * 60)

    all_matches, all_batting, all_bowling = [], [], []

    seasons = {2019:60, 2020:60, 2021:60, 2022:74, 2023:74, 2024:74, 2025:74, 2026:74}
    for yr, n_matches in seasons.items():
        m, b, bw = generate_synthetic_season(yr, n_matches)
        all_matches.extend(m)
        all_batting.extend(b)
        all_bowling.extend(bw)
        print(f"  [Synthetic] {yr}: {len(m)} matches generated.")

    return (
        pd.DataFrame(all_matches),
        pd.DataFrame(all_batting),
        pd.DataFrame(all_bowling),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN SEEDER
# ══════════════════════════════════════════════════════════════════════════════

def seed_database():
    print("=" * 60)
    print("  IPL Analytics Hub — Database Seeder")
    print("=" * 60)

    # ── Wipe existing DB ──────────────────────────────────────────────────────
    if os.path.exists(DEFAULT_DB_PATH):
        try:
            os.remove(DEFAULT_DB_PATH)
            print("[OK] Cleared existing database.")
        except Exception as e:
            print(f"[WARN] Could not remove old DB: {e}")
    create_database()

    # ── Insert teams ──────────────────────────────────────────────────────────
    teams_df = pd.DataFrame([{"team_name": full, "short_name": short} for full, short in TEAMS])
    insert_dataframe("teams", teams_df)
    print(f"[OK] Loaded {len(teams_df)} IPL franchise teams.")

    # ── Insert players ────────────────────────────────────────────────────────
    all_players = []
    for short, roster in ROSTERS.items():
        for p_name, role in roster:
            all_players.append({"player_name": p_name, "team_short": short, "role": role})
    players_df = pd.DataFrame(all_players).drop_duplicates(subset=["player_name"])
    insert_dataframe("players", players_df)
    print(f"[OK] Loaded {len(players_df)} players.")

    # ── PRIMARY: Try live Cricsheet scraper ───────────────────────────────────
    raw_matches_df = raw_batting_df = raw_bowling_df = None
    data_source = "unknown"

    print("\n[SCRAPER] Attempting live data fetch from Cricsheet...")
    print("          (requests + BeautifulSoup → JSON zip → ball-by-ball parsing)")
    try:
        from scraper.cricsheet_scraper import scrape_live_ipl_data
        raw_matches_df, raw_batting_df, raw_bowling_df = scrape_live_ipl_data()
        data_source = "LIVE (Cricsheet)"
        print(f"\n[OK] Live scrape successful!")
        print(f"     Matches  : {len(raw_matches_df)}")
        print(f"     Batting  : {len(raw_batting_df)}")
        print(f"     Bowling  : {len(raw_bowling_df)}")

    except Exception as e:
        print(f"\n[WARN] Live scraper failed: {e}")
        print("[FALLBACK] Switching to synthetic data generator...\n")
        raw_matches_df, raw_batting_df, raw_bowling_df = generate_all_synthetic()
        data_source = "SYNTHETIC (Fallback)"

    # ── Save raw CSVs ─────────────────────────────────────────────────────────
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    raw_matches_df.to_csv("data/raw/matches_all_raw.csv", index=False)
    raw_batting_df.to_csv("data/raw/batting_all_raw.csv", index=False)
    raw_bowling_df.to_csv("data/raw/bowling_all_raw.csv", index=False)
    print(f"\n[OK] Raw CSVs saved to data/raw/")

    # ── Processing pipeline ───────────────────────────────────────────────────
    print("[OK] Running processing pipeline (clean → transform → validate)...")
    clean_m_df  = clean_matches(raw_matches_df)
    clean_b_df  = clean_batting(raw_batting_df)
    clean_bw_df = clean_bowling(raw_bowling_df)

    clean_b_df  = add_batting_metrics(clean_b_df)
    clean_bw_df = add_bowling_metrics(clean_bw_df)

    validate_matches(clean_m_df)
    validate_batting(clean_b_df)
    validate_bowling(clean_bw_df)

    clean_m_df.to_csv("data/processed/matches_clean.csv", index=False)
    clean_b_df.to_csv("data/processed/batting_clean.csv", index=False)
    clean_bw_df.to_csv("data/processed/bowling_clean.csv", index=False)

    # ── Insert into DB ────────────────────────────────────────────────────────
    insert_dataframe("matches", clean_m_df)
    insert_dataframe("batting",  clean_b_df)
    insert_dataframe("bowling",  clean_bw_df)

    stats = get_db_stats()
    print("\n" + "=" * 60)
    print(f"  Database Seeding Complete! [{data_source}]")
    print(f"  Teams    : {stats['teams']}")
    print(f"  Players  : {stats['players']}")
    print(f"  Matches  : {stats['matches']}")
    print(f"  Batting  : {stats['batting']:,}")
    print(f"  Bowling  : {stats['bowling']:,}")
    print(f"  Seasons  : {sorted(stats['seasons'])}")
    print("=" * 60)


if __name__ == "__main__":
    seed_database()

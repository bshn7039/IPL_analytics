"""
IPL Data Loader & Synthetic Seeder
Generates authentic multi-season IPL data (2023, 2024, 2025),
cleans and transforms it via the processing pipeline,
and commits it into SQLite and processed CSVs.
"""
import os
import sys
import random
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database.db import create_database, insert_dataframe, get_db_stats, DEFAULT_DB_PATH
from processing.cleaner import clean_matches, clean_batting, clean_bowling
from processing.transformer import add_batting_metrics, add_bowling_metrics, add_match_context
from processing.validators import validate_batting, validate_bowling, validate_matches

# Canonical IPL Teams
TEAMS = [
    ("Mumbai Indians", "MI"),
    ("Chennai Super Kings", "CSK"),
    ("Royal Challengers Bengaluru", "RCB"),
    ("Kolkata Knight Riders", "KKR"),
    ("Rajasthan Royals", "RR"),
    ("Sunrisers Hyderabad", "SRH"),
    ("Delhi Capitals", "DC"),
    ("Punjab Kings", "PBKS"),
    ("Gujarat Titans", "GT"),
    ("Lucknow Super Giants", "LSG")
]

# Authentic Roster
ROSTERS = {
    "MI": [
        ("Rohit Sharma", "Batter"), ("Ishan Kishan", "Wicketkeeper"), ("Suryakumar Yadav", "Batter"),
        ("Tilak Varma", "Batter"), ("Hardik Pandya", "All-rounder"), ("Tim David", "Batter"),
        ("Romario Shepherd", "All-rounder"), ("Mohammad Nabi", "All-rounder"), ("Gerald Coetzee", "Bowler"),
        ("Piyush Chawla", "Bowler"), ("Jasprit Bumrah", "Bowler"), ("Nuwan Thushara", "Bowler")
    ],
    "CSK": [
        ("Ruturaj Gaikwad", "Batter"), ("Rachin Ravindra", "All-rounder"), ("Ajinkya Rahane", "Batter"),
        ("Daryl Mitchell", "All-rounder"), ("Shivam Dube", "All-rounder"), ("Ravindra Jadeja", "All-rounder"),
        ("MS Dhoni", "Wicketkeeper"), ("Mitchell Santner", "All-rounder"), ("Shardul Thakur", "Bowler"),
        ("Tushar Deshpande", "Bowler"), ("Mustafizur Rahman", "Bowler"), ("Matheesha Pathirana", "Bowler")
    ],
    "RCB": [
        ("Faf du Plessis", "Batter"), ("Virat Kohli", "Batter"), ("Will Jacks", "All-rounder"),
        ("Rajat Patidar", "Batter"), ("Glenn Maxwell", "All-rounder"), ("Cameron Green", "All-rounder"),
        ("Dinesh Karthik", "Wicketkeeper"), ("Mahipal Lomror", "Batter"), ("Karn Sharma", "Bowler"),
        ("Lockie Ferguson", "Bowler"), ("Mohammed Siraj", "Bowler"), ("Yash Dayal", "Bowler")
    ],
    "KKR": [
        ("Phil Salt", "Wicketkeeper"), ("Sunil Narine", "All-rounder"), ("Venkatesh Iyer", "Batter"),
        ("Shreyas Iyer", "Batter"), ("Rinku Singh", "Batter"), ("Andre Russell", "All-rounder"),
        ("Ramandeep Singh", "All-rounder"), ("Mitchell Starc", "Bowler"), ("Harshit Rana", "Bowler"),
        ("Vaibhav Arora", "Bowler"), ("Varun Chakravarthy", "Bowler"), ("Suyash Sharma", "Bowler")
    ],
    "RR": [
        ("Yashasvi Jaiswal", "Batter"), ("Jos Buttler", "Wicketkeeper"), ("Sanju Samson", "Wicketkeeper"),
        ("Riyan Parag", "Batter"), ("Dhruv Jurel", "Wicketkeeper"), ("Shimron Hetmyer", "Batter"),
        ("Rovman Powell", "All-rounder"), ("Ravichandran Ashwin", "All-rounder"), ("Trent Boult", "Bowler"),
        ("Avesh Khan", "Bowler"), ("Sandeep Sharma", "Bowler"), ("Yuzvendra Chahal", "Bowler")
    ],
    "SRH": [
        ("Travis Head", "Batter"), ("Abhishek Sharma", "All-rounder"), ("Rahul Tripathi", "Batter"),
        ("Aiden Markram", "Batter"), ("Heinrich Klaasen", "Wicketkeeper"), ("Nitish Kumar Reddy", "All-rounder"),
        ("Abdul Samad", "Batter"), ("Shahbaz Ahmed", "All-rounder"), ("Pat Cummins", "Bowler"),
        ("Bhuvneshwar Kumar", "Bowler"), ("Jaydev Unadkat", "Bowler"), ("T Natarajan", "Bowler")
    ],
    "DC": [
        ("David Warner", "Batter"), ("Prithvi Shaw", "Batter"), ("Jake Fraser-McGurk", "Batter"),
        ("Rishabh Pant", "Wicketkeeper"), ("Tristan Stubbs", "Wicketkeeper"), ("Axar Patel", "All-rounder"),
        ("Abishek Porel", "Wicketkeeper"), ("Kuldeep Yadav", "Bowler"), ("Khaleel Ahmed", "Bowler"),
        ("Mukesh Kumar", "Bowler"), ("Ishant Sharma", "Bowler"), ("Anrich Nortje", "Bowler")
    ],
    "PBKS": [
        ("Shikhar Dhawan", "Batter"), ("Jonny Bairstow", "Wicketkeeper"), ("Prabhsimran Singh", "Wicketkeeper"),
        ("Rilee Rossouw", "Batter"), ("Sam Curran", "All-rounder"), ("Jitesh Sharma", "Wicketkeeper"),
        ("Shashank Singh", "Batter"), ("Ashutosh Sharma", "Batter"), ("Harpreet Brar", "All-rounder"),
        ("Harshal Patel", "Bowler"), ("Kagiso Rabada", "Bowler"), ("Arshdeep Singh", "Bowler")
    ],
    "GT": [
        ("Shubman Gill", "Batter"), ("Wriddhiman Saha", "Wicketkeeper"), ("Sai Sudharsan", "Batter"),
        ("David Miller", "Batter"), ("Azmatullah Omarzai", "All-rounder"), ("Rahul Tewatia", "All-rounder"),
        ("Rashid Khan", "All-rounder"), ("Shahrukh Khan", "Batter"), ("Mohit Sharma", "Bowler"),
        ("Noor Ahmad", "Bowler"), ("Spencer Johnson", "Bowler"), ("Umesh Yadav", "Bowler")
    ],
    "LSG": [
        ("KL Rahul", "Wicketkeeper"), ("Quinton de Kock", "Wicketkeeper"), ("Marcus Stoinis", "All-rounder"),
        ("Nicholas Pooran", "Wicketkeeper"), ("Ayush Badoni", "Batter"), ("Deepak Hooda", "All-rounder"),
        ("Krunal Pandya", "All-rounder"), ("Ravi Bishnoi", "Bowler"), ("Mohsin Khan", "Bowler"),
        ("Mayank Yadav", "Bowler"), ("Yash Thakur", "Bowler"), ("Naveen-ul-Haq", "Bowler")
    ]
}

VENUES = [
    ("Wankhede Stadium", "Mumbai"),
    ("M. A. Chidambaram Stadium (Chepauk)", "Chennai"),
    ("M. Chinnaswamy Stadium", "Bengaluru"),
    ("Eden Gardens", "Kolkata"),
    ("Narendra Modi Stadium", "Ahmedabad"),
    ("Rajiv Gandhi International Cricket Stadium", "Hyderabad"),
    ("Arun Jaitley Stadium", "Delhi"),
    ("Maharaja Yadavindra Singh Stadium", "Mullanpur"),
    ("Sawai Mansingh Stadium", "Jaipur"),
    ("BRSABV Ekana Cricket Stadium", "Lucknow")
]

def generate_season_data(season_year, num_matches=74):
    """Generates realistic match cards, batting, and bowling logs."""
    random.seed(season_year * 42)
    np.random.seed(season_year * 42)

    matches = []
    batting_rows = []
    bowling_rows = []

    team_keys = [t[1] for t in TEAMS]

    for m_idx in range(1, num_matches + 1):
        match_id = f"IPL_{season_year}_{m_idx:03d}"
        t1, t2 = random.sample(team_keys, 2)
        venue, city = random.choice(VENUES)
        
        toss_winner = random.choice([t1, t2])
        toss_decision = random.choice(["bat", "field"])
        
        if (toss_winner == t1 and toss_decision == "bat") or (toss_winner == t2 and toss_decision == "field"):
            bat_first_team, chase_team = t1, t2
        else:
            bat_first_team, chase_team = t2, t1

        # Simulate Innings 1
        inn1_runs, inn1_batting, inn1_bowling = simulate_innings(
            match_id, 1, bat_first_team, chase_team, target=None
        )
        batting_rows.extend(inn1_batting)
        bowling_rows.extend(inn1_bowling)

        # Simulate Innings 2
        inn2_runs, inn2_batting, inn2_bowling = simulate_innings(
            match_id, 2, chase_team, bat_first_team, target=inn1_runs + 1
        )
        batting_rows.extend(inn2_batting)
        bowling_rows.extend(inn2_bowling)

        if inn2_runs >= inn1_runs + 1:
            winner = chase_team
            wickets_fallen = sum(1 for b in inn2_batting if b["dismissal"] != "not out")
            wkts_left = 10 - min(wickets_fallen, 10)
            result_str = f"{chase_team} won by {wkts_left} wickets"
        elif inn1_runs > inn2_runs:
            winner = bat_first_team
            run_margin = inn1_runs - inn2_runs
            result_str = f"{bat_first_team} won by {run_margin} runs"
        else:
            winner = chase_team
            result_str = f"{chase_team} won via Super Over"

        date_str = f"{season_year}-{random.randint(3, 5):02d}-{random.randint(1, 28):02d}"

        matches.append({
            "match_id": match_id,
            "season": season_year,
            "date": date_str,
            "team1": t1,
            "team2": t2,
            "venue": venue,
            "city": city,
            "toss_winner": toss_winner,
            "toss_decision": toss_decision,
            "winner": winner,
            "result": result_str
        })

    return matches, batting_rows, bowling_rows

def simulate_innings(match_id, innings, bat_team, bowl_team, target=None):
    bat_roster = ROSTERS[bat_team]
    bowl_roster = ROSTERS[bowl_team]

    batters_count = random.randint(6, 9)
    active_batters = bat_roster[:batters_count]
    bowlers = [p for p in bowl_roster if p[1] in ["Bowler", "All-rounder"]][:5]
    if len(bowlers) < 5:
        bowlers = bowl_roster[-5:]

    balls_budget = 120
    runs_accum = 0
    balls_accum = 0
    batting_records = []

    for i, (p_name, role) in enumerate(active_batters):
        if balls_accum >= 120 or (target and runs_accum >= target):
            break
        
        rem_balls = 120 - balls_accum
        faced = min(rem_balls, random.randint(8, 38))
        if i == len(active_batters) - 1:
            faced = rem_balls

        sr = random.uniform(115.0, 185.0)
        p_runs = int((sr / 100.0) * faced)
        
        sixes = max(0, int(p_runs * random.uniform(0.15, 0.40) / 6))
        fours = max(0, int((p_runs - (sixes * 6)) * random.uniform(0.20, 0.55) / 4))
        boundary_runs = (fours * 4) + (sixes * 6)
        if boundary_runs > p_runs:
            p_runs = boundary_runs + random.randint(2, 10)

        not_out = 1 if (i >= len(active_batters) - 2 and (balls_accum + faced >= 120 or (target and runs_accum + p_runs >= target))) else 0
        dismissal = "not out" if not_out else random.choice(["c Dhoni b Bumrah", "b Cummins", "c & b Narine", "lbw b Chahal", "run out"])

        batting_records.append({
            "match_id": match_id,
            "innings": innings,
            "team": bat_team,
            "player": p_name,
            "runs": p_runs,
            "balls": faced,
            "fours": fours,
            "sixes": sixes,
            "strike_rate": round((p_runs / faced * 100.0), 2) if faced > 0 else 0.0,
            "dismissal": dismissal,
            "not_out": not_out
        })
        runs_accum += p_runs
        balls_accum += faced

    bowling_records = []
    rem_runs = runs_accum
    for idx, (b_name, b_role) in enumerate(bowlers):
        overs_to_bowl = 4.0 if idx < 4 else (120 - 4 * 6 * 4) / 6.0
        balls_bowled = int(overs_to_bowl * 6)
        b_runs = int(rem_runs * (random.uniform(0.14, 0.26))) if idx < 4 else max(0, rem_runs)
        rem_runs -= b_runs
        b_wkts = random.choice([0, 1, 1, 2, 2, 3])
        b_maidens = 1 if (random.random() < 0.10 and b_runs < 25) else 0

        bowling_records.append({
            "match_id": match_id,
            "innings": innings,
            "team": bowl_team,
            "player": b_name,
            "overs": round(balls_bowled / 6.0, 1),
            "balls_bowled": balls_bowled,
            "maidens": b_maidens,
            "runs_conceded": b_runs,
            "wickets": b_wkts,
            "economy": round((b_runs / balls_bowled * 6.0), 2) if balls_bowled > 0 else 0.0,
            "bowling_avg": round(b_runs / b_wkts, 2) if b_wkts > 0 else None,
            "bowling_sr": round(balls_bowled / b_wkts, 2) if b_wkts > 0 else None
        })

    return runs_accum, batting_records, bowling_records

def seed_database():
    print("==================================================")
    print("Initializing IPL Analytics Hub Database Engine...")
    print("==================================================")
    
    if os.path.exists(DEFAULT_DB_PATH):
        try:
            os.remove(DEFAULT_DB_PATH)
        except Exception:
            pass
    create_database()

    teams_df = pd.DataFrame([{"team_name": full, "short_name": short} for full, short in TEAMS])
    insert_dataframe("teams", teams_df)
    print(f"[OK] Loaded {len(teams_df)} IPL franchise teams.")

    all_players = []
    for short, roster in ROSTERS.items():
        for p_name, role in roster:
            all_players.append({"player_name": p_name, "team_short": short, "role": role})
    players_df = pd.DataFrame(all_players).drop_duplicates(subset=["player_name"])
    insert_dataframe("players", players_df)
    print(f"[OK] Loaded {len(players_df)} official players.")

    seasons = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    all_matches = []
    all_batting = []
    all_bowling = []

    for yr in seasons:
        match_count = 60 if yr in [2019, 2020, 2021] else 74
        m, b, bw = generate_season_data(yr, num_matches=match_count)
        all_matches.extend(m)
        all_batting.extend(b)
        all_bowling.extend(bw)
        print(f"[OK] Season {yr}: {len(m)} matches, {len(b)} batting cards, {len(bw)} bowling cards.")

    raw_matches_df = pd.DataFrame(all_matches)
    raw_batting_df = pd.DataFrame(all_batting)
    raw_bowling_df = pd.DataFrame(all_bowling)

    raw_matches_df.to_csv("data/raw/matches_all_raw.csv", index=False)
    raw_batting_df.to_csv("data/raw/batting_all_raw.csv", index=False)
    raw_bowling_df.to_csv("data/raw/bowling_all_raw.csv", index=False)

    clean_m_df = clean_matches(raw_matches_df)
    clean_b_df = clean_batting(raw_batting_df)
    clean_bw_df = clean_bowling(raw_bowling_df)

    clean_b_df = add_batting_metrics(clean_b_df)
    clean_bw_df = add_bowling_metrics(clean_bw_df)

    validate_matches(clean_m_df)
    validate_batting(clean_b_df)
    validate_bowling(clean_bw_df)

    clean_m_df.to_csv("data/processed/matches_clean.csv", index=False)
    clean_b_df.to_csv("data/processed/batting_clean.csv", index=False)
    clean_bw_df.to_csv("data/processed/bowling_clean.csv", index=False)

    insert_dataframe("matches", clean_m_df)
    insert_dataframe("batting", clean_b_df)
    insert_dataframe("bowling", clean_bw_df)

    stats = get_db_stats()
    print("--------------------------------------------------")
    print(f"Database Seeding Complete!")
    print(f"Teams: {stats['teams']}")
    print(f"Players: {stats['players']}")
    print(f"Matches: {stats['matches']}")
    print(f"Batting Records: {stats['batting']}")
    print(f"Bowling Records: {stats['bowling']}")
    print(f"Active Seasons: {stats['seasons']}")
    print("==================================================")

if __name__ == "__main__":
    seed_database()

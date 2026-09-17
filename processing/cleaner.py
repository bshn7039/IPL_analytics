"""
Data Cleaning Module
Cleans raw scraped match, batting, and bowling datasets:
- Standardizes team abbreviations
- Handles missing and anomalous values
- Formats datetimes and casts numeric types
- Removes duplicates and non-player records (Extras, Totals, DNB)
"""
import pandas as pd
import numpy as np
from scraper.parser import standardize_team_name, parse_player_name

def clean_matches(df_or_path):
    """
    Cleans matches DataFrame or reads from CSV path.
    """
    df = pd.read_csv(df_or_path) if isinstance(df_or_path, str) else df_or_path.copy()

    # Drop duplicate matches based on match_id or date+teams
    if "match_id" in df.columns:
        df = df.drop_duplicates(subset=["match_id"])
    else:
        df = df.drop_duplicates()

    # Standardize team names
    for col in ["team1", "team2", "winner", "toss_winner"]:
        if col in df.columns:
            df[col] = df[col].apply(standardize_team_name)

    # Date normalization
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df["date"] = df["date"].fillna("2024-04-01")

    # Fill missing values
    if "winner" in df.columns:
        df["winner"] = df["winner"].fillna("No Result")
    if "toss_decision" in df.columns:
        df["toss_decision"] = df["toss_decision"].fillna("field").str.lower()
    if "venue" in df.columns:
        df["venue"] = df["venue"].fillna("Wankhede Stadium, Mumbai")
    if "city" in df.columns:
        df["city"] = df["city"].fillna("Mumbai")
    if "season" in df.columns:
        df["season"] = pd.to_numeric(df["season"], errors="coerce").fillna(2024).astype(int)
    else:
        df["season"] = 2024

    return df.reset_index(drop=True)

def clean_batting(df_or_path):
    """
    Cleans batting DataFrame or reads from CSV path.
    """
    df = pd.read_csv(df_or_path) if isinstance(df_or_path, str) else df_or_path.copy()

    # Deduplicate
    dedup_subset = [c for c in ["match_id", "innings", "player"] if c in df.columns]
    if dedup_subset:
        df = df.drop_duplicates(subset=dedup_subset)

    # Clean player names and filter non-batsman rows
    if "player" in df.columns:
        df["player"] = df["player"].apply(parse_player_name)
        # Exclude system/aggregate rows
        invalid_mask = df["player"].str.lower().str.contains(r"extras|total|did not bat|penalty", regex=True, na=False)
        df = df[~invalid_mask & (df["player"] != "") & df["player"].notna()]

    # Standardize team names
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)

    # Convert numeric fields
    for col in ["runs", "balls", "fours", "sixes", "innings"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Handle not_out
    if "not_out" not in df.columns:
        if "dismissal" in df.columns:
            df["not_out"] = df["dismissal"].astype(str).str.lower().str.contains("not out").astype(int)
        else:
            df["not_out"] = 0
    else:
        df["not_out"] = pd.to_numeric(df["not_out"], errors="coerce").fillna(0).astype(int)

    # Dismissal text
    if "dismissal" in df.columns:
        df["dismissal"] = df["dismissal"].fillna("not out")

    return df.reset_index(drop=True)

def clean_bowling(df_or_path):
    """
    Cleans bowling DataFrame or reads from CSV path.
    """
    df = pd.read_csv(df_or_path) if isinstance(df_or_path, str) else df_or_path.copy()

    # Deduplicate
    dedup_subset = [c for c in ["match_id", "innings", "player"] if c in df.columns]
    if dedup_subset:
        df = df.drop_duplicates(subset=dedup_subset)

    # Clean bowler names
    if "player" in df.columns:
        df["player"] = df["player"].apply(parse_player_name)
        df = df[(df["player"] != "") & df["player"].notna()]

    # Standardize bowling team name
    if "team" in df.columns:
        df["team"] = df["team"].apply(standardize_team_name)

    # Numeric conversions
    for col in ["maidens", "runs_conceded", "wickets", "innings"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "overs" in df.columns:
        df["overs"] = pd.to_numeric(df["overs"], errors="coerce").fillna(0.0).astype(float)

    # Convert overs to balls_bowled accurately
    if "balls_bowled" not in df.columns or df["balls_bowled"].isna().any():
        def calc_balls(row):
            ov = float(row.get("overs", 0.0))
            whole_overs = int(ov)
            rem = round((ov - whole_overs) * 10)
            return whole_overs * 6 + rem
        df["balls_bowled"] = df.apply(calc_balls, axis=1).astype(int)

    return df.reset_index(drop=True)

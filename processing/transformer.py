"""
Feature Transformation & Derived Cricket Metrics
Calculates advanced batting & bowling metrics using Pandas & NumPy.
"""
import pandas as pd
import numpy as np

def add_batting_metrics(batting_df):
    """
    Computes Strike Rate, Boundary Distribution, Fifties, and Centuries.
    """
    df = batting_df.copy()
    
    # Strike rate
    df["strike_rate"] = np.where(
        df["balls"] > 0,
        np.round((df["runs"] / df["balls"]) * 100.0, 2),
        0.0
    )

    # Boundary metrics
    df["boundary_runs"] = (df["fours"] * 4) + (df["sixes"] * 6)
    df["boundary_percentage"] = np.where(
        df["runs"] > 0,
        np.round((df["boundary_runs"] / df["runs"]) * 100.0, 2),
        0.0
    )

    # Milestones
    df["is_fifty"] = ((df["runs"] >= 50) & (df["runs"] < 100)).astype(int)
    df["is_hundred"] = (df["runs"] >= 100).astype(int)

    return df

def add_bowling_metrics(bowling_df):
    """
    Computes Economy Rate, Bowling Average, and Bowling Strike Rate.
    """
    df = bowling_df.copy()

    # Economy: runs conceded per 6 legal balls
    df["economy"] = np.where(
        df["balls_bowled"] > 0,
        np.round((df["runs_conceded"] / df["balls_bowled"]) * 6.0, 2),
        0.0
    )

    # Bowling Average: runs conceded per wicket
    df["bowling_avg"] = np.where(
        df["wickets"] > 0,
        np.round(df["runs_conceded"] / df["wickets"], 2),
        np.nan
    )

    # Bowling Strike Rate: balls bowled per wicket
    df["bowling_sr"] = np.where(
        df["wickets"] > 0,
        np.round(df["balls_bowled"] / df["wickets"], 2),
        np.nan
    )

    return df

def add_match_context(batting_or_bowling_df, matches_df):
    """
    Merges match metadata (season, date, venue, winner, toss) into player cards.
    """
    if "match_id" not in batting_or_bowling_df.columns or "match_id" not in matches_df.columns:
        return batting_or_bowling_df

    cols_to_merge = ["match_id", "season", "venue", "city", "winner", "toss_winner", "toss_decision"]
    available_cols = [c for c in cols_to_merge if c in matches_df.columns]

    merged = batting_or_bowling_df.merge(matches_df[available_cols], on="match_id", how="left")
    
    # Add winning flag
    if "winner" in merged.columns and "team" in merged.columns:
        merged["is_winner"] = (merged["team"] == merged["winner"]).astype(int)
    else:
        merged["is_winner"] = 0

    return merged

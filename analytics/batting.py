"""
Batting Analytics Module
Provides statistical aggregations, leaderboards, and situational splits for batting data.
"""
import pandas as pd
import numpy as np
from database.db import query

def get_team_batting_summary(team, season=None):
    """
    Computes team-level batting KPIs:
    Total runs, matches, average score, strike rate, boundaries, highest & lowest innings totals.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (team, season) if season else (team,)

    sql = f"""
    SELECT 
        b.match_id,
        b.innings,
        SUM(b.runs) as innings_runs,
        SUM(b.balls) as innings_balls,
        SUM(b.fours) as innings_fours,
        SUM(b.sixes) as innings_sixes
    FROM batting b
    JOIN matches m ON b.match_id = m.match_id
    WHERE b.team = ? {season_filter}
    GROUP BY b.match_id, b.innings
    """
    df = query(sql, params)

    if df.empty:
        return {
            "total_runs": 0,
            "matches": 0,
            "avg_score": 0.0,
            "total_fours": 0,
            "total_sixes": 0,
            "strike_rate": 0.0,
            "highest_score": 0,
            "lowest_score": 0,
            "boundary_pct": 0.0
        }

    total_runs = int(df["innings_runs"].sum())
    matches_count = len(df["match_id"].unique())
    total_balls = int(df["innings_balls"].sum())
    total_fours = int(df["innings_fours"].sum())
    total_sixes = int(df["innings_sixes"].sum())
    avg_score = round(total_runs / matches_count, 1) if matches_count > 0 else 0.0
    sr = round((total_runs / total_balls * 100.0), 2) if total_balls > 0 else 0.0
    highest = int(df["innings_runs"].max())
    lowest = int(df["innings_runs"].min())
    boundary_runs = (total_fours * 4) + (total_sixes * 6)
    boundary_pct = round((boundary_runs / total_runs * 100.0), 1) if total_runs > 0 else 0.0

    return {
        "total_runs": total_runs,
        "matches": matches_count,
        "avg_score": avg_score,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "strike_rate": sr,
        "highest_score": highest,
        "lowest_score": lowest,
        "boundary_pct": boundary_pct
    }

def get_top_batsmen(team=None, season=None, limit=10):
    """
    Generates leaderboard of top batsmen with aggregate runs, average, SR, and milestones.
    """
    conditions = []
    params = []
    if team:
        conditions.append("b.team = ?")
        params.append(team)
    if season:
        conditions.append("m.season = ?")
        params.append(season)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
    SELECT 
        b.player,
        b.team,
        COUNT(b.id) as innings,
        SUM(b.runs) as runs,
        SUM(b.balls) as balls,
        SUM(b.fours) as fours,
        SUM(b.sixes) as sixes,
        SUM(b.not_out) as not_outs,
        MAX(b.runs) as highest_score,
        SUM(b.is_fifty) as fifties,
        SUM(b.is_hundred) as hundreds
    FROM batting b
    JOIN matches m ON b.match_id = m.match_id
    {where_clause}
    GROUP BY b.player
    ORDER BY runs DESC
    LIMIT ?
    """
    params.append(limit)
    df = query(sql, tuple(params))

    if df.empty:
        return df

    # Calculate average & strike rate
    dismissals = df["innings"] - df["not_outs"]
    df["average"] = np.where(dismissals > 0, np.round(df["runs"] / dismissals, 2), df["runs"].astype(float))
    df["strike_rate"] = np.where(df["balls"] > 0, np.round((df["runs"] / df["balls"]) * 100.0, 2), 0.0)

    return df[["player", "team", "innings", "runs", "average", "strike_rate", "fours", "sixes", "fifties", "hundreds", "highest_score"]]

def get_batting_by_match(team, season=None):
    """
    Returns sequence of match scores and outcomes for trend visualization.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (team, season) if season else (team,)

    sql = f"""
    SELECT 
        m.match_id,
        m.date,
        CASE WHEN m.team1 = ? THEN m.team2 ELSE m.team1 END as opponent,
        m.winner,
        SUM(b.runs) as team_score,
        SUM(b.fours) as fours,
        SUM(b.sixes) as sixes
    FROM matches m
    JOIN batting b ON m.match_id = b.match_id AND b.team = ?
    WHERE (m.team1 = ? OR m.team2 = ?) {season_filter}
    GROUP BY m.match_id
    ORDER BY m.date ASC
    """
    full_params = (team, team, team, team, season) if season else (team, team, team, team)
    df = query(sql, full_params)
    if not df.empty:
        df["match_num"] = range(1, len(df) + 1)
        df["result"] = np.where(df["winner"] == team, "Won", "Lost")
    return df

def get_batting_first_vs_chasing(team, season=None):
    """
    Compares batting first (innings 1) vs chasing (innings 2) effectiveness.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (team, season) if season else (team,)

    sql = f"""
    SELECT 
        b.innings,
        b.match_id,
        SUM(b.runs) as innings_runs,
        m.winner
    FROM batting b
    JOIN matches m ON b.match_id = m.match_id
    WHERE b.team = ? {season_filter}
    GROUP BY b.innings, b.match_id
    """
    df = query(sql, params)
    if df.empty:
        return {
            "bat_first_avg": 0, "bat_first_win_pct": 0, "bat_first_matches": 0,
            "chasing_avg": 0, "chasing_win_pct": 0, "chasing_matches": 0
        }

    inn1 = df[df["innings"] == 1]
    inn2 = df[df["innings"] == 2]

    inn1_wins = (inn1["winner"] == team).sum()
    inn2_wins = (inn2["winner"] == team).sum()

    return {
        "bat_first_avg": round(inn1["innings_runs"].mean(), 1) if not inn1.empty else 0.0,
        "bat_first_win_pct": round((inn1_wins / len(inn1) * 100.0), 1) if not inn1.empty else 0.0,
        "bat_first_matches": len(inn1),
        "chasing_avg": round(inn2["innings_runs"].mean(), 1) if not inn2.empty else 0.0,
        "chasing_win_pct": round((inn2_wins / len(inn2) * 100.0), 1) if not inn2.empty else 0.0,
        "chasing_matches": len(inn2)
    }

def get_player_batting_stats(player_name, season=None):
    """
    Retrieves full career or seasonal batting profile for a specific player.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (player_name, season) if season else (player_name,)

    sql = f"""
    SELECT 
        b.player,
        COUNT(b.id) as innings,
        SUM(b.runs) as runs,
        SUM(b.balls) as balls,
        SUM(b.fours) as fours,
        SUM(b.sixes) as sixes,
        SUM(b.not_out) as not_outs,
        MAX(b.runs) as highest_score,
        SUM(b.is_fifty) as fifties,
        SUM(b.is_hundred) as hundreds
    FROM batting b
    JOIN matches m ON b.match_id = m.match_id
    WHERE b.player = ? {season_filter}
    GROUP BY b.player
    """
    df = query(sql, params)
    if df.empty:
        return None

    row = df.iloc[0].to_dict()
    dismissals = row["innings"] - row["not_outs"]
    row["average"] = round(row["runs"] / dismissals, 2) if dismissals > 0 else float(row["runs"])
    row["strike_rate"] = round((row["runs"] / row["balls"] * 100.0), 2) if row["balls"] > 0 else 0.0
    return row

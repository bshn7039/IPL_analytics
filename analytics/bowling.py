"""
Bowling Analytics Module
Provides bowling summaries, wicket leaderboards, economy rate profiles, and player records.
"""
import pandas as pd
import numpy as np
from database.db import query

def get_team_bowling_summary(team, season=None):
    """
    Calculates team-level bowling KPIs:
    Total wickets taken, runs conceded, legal overs, overall economy, and average.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (team, season) if season else (team,)

    sql = f"""
    SELECT 
        SUM(bw.wickets) as total_wickets,
        SUM(bw.runs_conceded) as total_runs_conceded,
        SUM(bw.balls_bowled) as total_balls_bowled,
        SUM(bw.maidens) as total_maidens
    FROM bowling bw
    JOIN matches m ON bw.match_id = m.match_id
    WHERE bw.team = ? {season_filter}
    """
    df = query(sql, params)

    if df.empty or df["total_balls_bowled"].iloc[0] is None:
        return {
            "total_wickets": 0,
            "runs_conceded": 0,
            "balls_bowled": 0,
            "overs": 0.0,
            "economy": 0.0,
            "bowling_avg": 0.0,
            "bowling_sr": 0.0,
            "maidens": 0
        }

    wickets = int(df["total_wickets"].iloc[0] or 0)
    runs = int(df["total_runs_conceded"].iloc[0] or 0)
    balls = int(df["total_balls_bowled"].iloc[0] or 0)
    maidens = int(df["total_maidens"].iloc[0] or 0)
    overs = round(balls / 6.0, 1)

    economy = round((runs / balls * 6.0), 2) if balls > 0 else 0.0
    bowling_avg = round(runs / wickets, 2) if wickets > 0 else 0.0
    bowling_sr = round(balls / wickets, 1) if wickets > 0 else 0.0

    return {
        "total_wickets": wickets,
        "runs_conceded": runs,
        "balls_bowled": balls,
        "overs": overs,
        "economy": economy,
        "bowling_avg": bowling_avg,
        "bowling_sr": bowling_sr,
        "maidens": maidens
    }

def get_top_bowlers(team=None, season=None, limit=10):
    """
    Generates leaderboard of bowlers ranked by wickets, economy, and strike rate.
    """
    conditions = []
    params = []
    if team:
        conditions.append("bw.team = ?")
        params.append(team)
    if season:
        conditions.append("m.season = ?")
        params.append(season)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
    SELECT 
        bw.player,
        bw.team,
        COUNT(DISTINCT bw.match_id) as matches,
        SUM(bw.balls_bowled) as balls_bowled,
        SUM(bw.runs_conceded) as runs_conceded,
        SUM(bw.wickets) as wickets,
        SUM(bw.maidens) as maidens
    FROM bowling bw
    JOIN matches m ON bw.match_id = m.match_id
    {where_clause}
    GROUP BY bw.player
    HAVING wickets > 0 OR balls_bowled >= 24
    ORDER BY wickets DESC, runs_conceded ASC
    LIMIT ?
    """
    params.append(limit)
    df = query(sql, tuple(params))

    if df.empty:
        return df

    df["overs"] = np.round(df["balls_bowled"] / 6.0, 1)
    df["economy"] = np.where(df["balls_bowled"] > 0, np.round((df["runs_conceded"] / df["balls_bowled"]) * 6.0, 2), 0.0)
    df["bowling_avg"] = np.where(df["wickets"] > 0, np.round(df["runs_conceded"] / df["wickets"], 2), np.nan)
    df["bowling_sr"] = np.where(df["wickets"] > 0, np.round(df["balls_bowled"] / df["wickets"], 1), np.nan)

    return df[["player", "team", "matches", "overs", "maidens", "runs_conceded", "wickets", "economy", "bowling_avg", "bowling_sr"]]

def get_bowling_by_match(team, season=None):
    """
    Tracks match-by-match wickets taken and runs conceded.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (team, season) if season else (team,)

    sql = f"""
    SELECT 
        m.match_id,
        m.date,
        CASE WHEN m.team1 = ? THEN m.team2 ELSE m.team1 END as opponent,
        m.winner,
        SUM(bw.wickets) as wickets_taken,
        SUM(bw.runs_conceded) as runs_conceded,
        SUM(bw.balls_bowled) as balls_bowled
    FROM matches m
    JOIN bowling bw ON m.match_id = bw.match_id AND bw.team = ?
    WHERE (m.team1 = ? OR m.team2 = ?) {season_filter}
    GROUP BY m.match_id
    ORDER BY m.date ASC
    """
    full_params = (team, team, team, team, season) if season else (team, team, team, team)
    df = query(sql, full_params)
    if not df.empty:
        df["match_num"] = range(1, len(df) + 1)
        df["economy"] = np.where(df["balls_bowled"] > 0, np.round(df["runs_conceded"] / df["balls_bowled"] * 6.0, 2), 0.0)
    return df

def get_player_bowling_stats(player_name, season=None):
    """
    Retrieves full bowling career or seasonal profile for an individual bowler.
    """
    season_filter = "AND m.season = ?" if season else ""
    params = (player_name, season) if season else (player_name,)

    sql = f"""
    SELECT 
        bw.player,
        COUNT(DISTINCT bw.match_id) as matches,
        SUM(bw.balls_bowled) as balls_bowled,
        SUM(bw.runs_conceded) as runs_conceded,
        SUM(bw.wickets) as wickets,
        SUM(bw.maidens) as maidens
    FROM bowling bw
    JOIN matches m ON bw.match_id = m.match_id
    WHERE bw.player = ? {season_filter}
    GROUP BY bw.player
    """
    df = query(sql, params)
    if df.empty:
        return None

    row = df.iloc[0].to_dict()
    balls = row["balls_bowled"]
    wkts = row["wickets"]
    runs = row["runs_conceded"]
    row["overs"] = round(balls / 6.0, 1)
    row["economy"] = round((runs / balls * 6.0), 2) if balls > 0 else 0.0
    row["bowling_avg"] = round(runs / wkts, 2) if wkts > 0 else None
    row["bowling_sr"] = round(balls / wkts, 1) if wkts > 0 else None
    return row

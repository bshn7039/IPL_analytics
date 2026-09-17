"""
Team Analytics Module
Consolidates team overview KPIs, seasonal win/loss tables, and Team Strength Score modeling.
"""
import pandas as pd
import numpy as np
from database.db import query
from analytics.batting import get_team_batting_summary
from analytics.bowling import get_team_bowling_summary

def get_team_overview(team, season=None):
    """
    Consolidates team win/loss records, batting averages, and bowling metrics.
    """
    season_filter = "AND season = ?" if season else ""
    params = (team, team, season) if season else (team, team)

    sql = f"""
    SELECT 
        COUNT(*) as matches_played,
        SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) as wins
    FROM matches
    WHERE (team1 = ? OR team2 = ?) {season_filter}
    """
    m_df = query(sql, (team,) + params)

    played = int(m_df["matches_played"].iloc[0] or 0)
    wins = int(m_df["wins"].iloc[0] or 0)
    losses = max(0, played - wins)
    win_rate = round((wins / played * 100.0), 1) if played > 0 else 0.0

    batting_stats = get_team_batting_summary(team, season)
    bowling_stats = get_team_bowling_summary(team, season)

    return {
        "team": team,
        "season": season or "All Seasons",
        "matches": played,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_score": batting_stats["avg_score"],
        "total_runs": batting_stats["total_runs"],
        "total_sixes": batting_stats["total_sixes"],
        "total_fours": batting_stats["total_fours"],
        "batting_sr": batting_stats["strike_rate"],
        "wickets": bowling_stats["total_wickets"],
        "economy": bowling_stats["economy"],
        "bowling_avg": bowling_stats["bowling_avg"]
    }

def get_all_teams_table(season=None):
    """
    Compiles complete league table with played, wins, losses, win%, avg score, and economy.
    """
    teams_df = query("SELECT short_name, team_name FROM teams ORDER BY short_name ASC")
    rows = []
    for _, t in teams_df.iterrows():
        short = t["short_name"]
        full = t["team_name"]
        ov = get_team_overview(short, season)
        if ov["matches"] > 0:
            rows.append({
                "Team": short,
                "Franchise": full,
                "Matches": ov["matches"],
                "Wins": ov["wins"],
                "Losses": ov["losses"],
                "Win %": ov["win_rate"],
                "Avg Score": ov["avg_score"],
                "Economy": ov["economy"],
                "Wickets": ov["wickets"],
                "Sixes": ov["total_sixes"]
            })
    res_df = pd.DataFrame(rows)
    if not res_df.empty:
        res_df = res_df.sort_values(by=["Wins", "Win %", "Avg Score"], ascending=False).reset_index(drop=True)
    return res_df

def get_team_strength_score(team, season=None):
    """
    Computes a 0-100 index based on:
    - Batting Performance (30%)
    - Bowling Economy & Wickets (30%)
    - Win Percentage (20%)
    - Boundary Frequency (10%)
    - Defending Efficiency (10%)
    """
    league = get_all_teams_table(season)
    if league.empty or team not in league["Team"].values:
        return 75.0

    target = league[league["Team"] == team].iloc[0]

    def min_max_norm(val, series, reverse=False):
        s_min, s_max = series.min(), series.max()
        if s_max == s_min:
            return 50.0
        norm = (val - s_min) / (s_max - s_min) * 100.0
        return 100.0 - norm if reverse else norm

    bat_score = min_max_norm(target["Avg Score"], league["Avg Score"])
    # Lower economy is better
    bowl_score = min_max_norm(target["Economy"], league["Economy"], reverse=True)
    win_score = target["Win %"]
    boundary_score = min_max_norm(target["Sixes"], league["Sixes"])
    wicket_score = min_max_norm(target["Wickets"], league["Wickets"])

    composite = (
        (bat_score * 0.30) +
        (bowl_score * 0.30) +
        (win_score * 0.20) +
        (boundary_score * 0.10) +
        (wicket_score * 0.10)
    )
    return round(float(np.clip(composite, 40.0, 98.0)), 1)

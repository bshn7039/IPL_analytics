"""
Comparison Analytics Module
Executes side-by-side comparative modeling for teams and players,
evaluating head-to-head records and strength differentials.
"""
from database.db import query
from analytics.team import get_team_overview, get_team_strength_score
from analytics.batting import get_player_batting_stats
from analytics.bowling import get_player_bowling_stats

def compare_teams(team_a, team_b, season=None):
    """
    Computes comparative profile for Team A vs Team B, including head-to-head records.
    """
    stats_a = get_team_overview(team_a, season)
    stats_b = get_team_overview(team_b, season)
    score_a = get_team_strength_score(team_a, season)
    score_b = get_team_strength_score(team_b, season)

    # Head-to-head match history
    season_filter = "AND season = ?" if season else ""
    params = (team_a, team_b, team_b, team_a, season) if season else (team_a, team_b, team_b, team_a)

    h2h_sql = f"""
    SELECT match_id, season, date, venue, winner, result
    FROM matches
    WHERE ((team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?)) {season_filter}
    ORDER BY date DESC
    """
    h2h_df = query(h2h_sql, params)

    h2h_wins_a = (h2h_df["winner"] == team_a).sum() if not h2h_df.empty else 0
    h2h_wins_b = (h2h_df["winner"] == team_b).sum() if not h2h_df.empty else 0

    # Dynamic verdict generator
    verdicts = []
    if stats_a["avg_score"] > stats_b["avg_score"] + 5:
        verdicts.append(f"{team_a} showcases a noticeably superior batting firepower (+{round(stats_a['avg_score'] - stats_b['avg_score'], 1)} runs/match).")
    elif stats_b["avg_score"] > stats_a["avg_score"] + 5:
        verdicts.append(f"{team_b} boasts stronger run-accumulation stability (+{round(stats_b['avg_score'] - stats_a['avg_score'], 1)} runs/match).")

    if stats_a["economy"] < stats_b["economy"] - 0.4:
        verdicts.append(f"{team_a} maintains tighter run containment in bowling (Economy: {stats_a['economy']} vs {stats_b['economy']}).")
    elif stats_b["economy"] < stats_a["economy"] - 0.4:
        verdicts.append(f"{team_b} holds greater bowling discipline (Economy: {stats_b['economy']} vs {stats_a['economy']}).")

    if not verdicts:
        verdicts.append("Both franchises display closely balanced tactical metrics across batting and bowling disciplines.")

    return {
        "team_a": team_a,
        "team_b": team_b,
        "stats_a": stats_a,
        "stats_b": stats_b,
        "score_a": score_a,
        "score_b": score_b,
        "h2h_matches": len(h2h_df),
        "h2h_wins_a": int(h2h_wins_a),
        "h2h_wins_b": int(h2h_wins_b),
        "h2h_df": h2h_df,
        "verdict": " ".join(verdicts)
    }

def compare_players(player_a, player_b, season=None):
    """
    Performs head-to-head individual player metric comparison.
    """
    bat_a = get_player_batting_stats(player_a, season)
    bat_b = get_player_batting_stats(player_b, season)
    bowl_a = get_player_bowling_stats(player_a, season)
    bowl_b = get_player_bowling_stats(player_b, season)

    return {
        "player_a": player_a,
        "player_b": player_b,
        "bat_a": bat_a,
        "bat_b": bat_b,
        "bowl_a": bowl_a,
        "bowl_b": bowl_b
    }

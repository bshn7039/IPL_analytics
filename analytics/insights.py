"""
Automated Cricket Intelligence & Insight Engine
Generates dynamic, rule-based performance assessments and tactical takeaways.
"""
from analytics.team import get_team_overview, get_team_strength_score
from analytics.batting import get_top_batsmen, get_batting_first_vs_chasing
from analytics.bowling import get_top_bowlers

def generate_team_insights(team, season=None):
    """
    Synthesizes multi-dimensional telemetry into actionable tactical bullet points.
    """
    ov = get_team_overview(team, season)
    strength = get_team_strength_score(team, season)
    bat_split = get_batting_first_vs_chasing(team, season)
    top_bat = get_top_batsmen(team, season, limit=1)
    top_bowl = get_top_bowlers(team, season, limit=1)

    insights = []

    # 1. Overall form & strength
    if strength >= 80.0:
        insights.append(f"Championship Contender Profile: {team} boasts an elite Team Strength Index of {strength}/100 with a {ov['win_rate']}% win rate.")
    elif strength >= 65.0:
        insights.append(f"Competitive Mid-Table Dynamic: {team} holds a respectable {strength}/100 rating, demonstrating balanced fundamentals.")
    else:
        insights.append(f"Rebuilding Cycle: {team} is operating at a {strength}/100 strength rating, facing volatility in key match phases.")

    # 2. Batting First vs Chasing
    if bat_split["chasing_win_pct"] > bat_split["bat_first_win_pct"] + 10:
        insights.append(f"Chasing Specialists: Team demonstrates higher composure chasing targets ({bat_split['chasing_win_pct']}% win rate vs {bat_split['bat_first_win_pct']}% defending).")
    elif bat_split["bat_first_win_pct"] > bat_split["chasing_win_pct"] + 10:
        insights.append(f"Target Setting Dominance: Franchise excels at scoreboard pressure, winning {bat_split['bat_first_win_pct']}% of matches when setting totals.")
    else:
        insights.append(f"Tactical Neutrality: Team maintains balanced win rates across both innings ({bat_split['bat_first_win_pct']}% bat 1st vs {bat_split['chasing_win_pct']}% chase).")

    # 3. Batting contributor
    if not top_bat.empty:
        mvp = top_bat.iloc[0]
        share = round((mvp['runs'] / ov['total_runs'] * 100.0), 1) if ov['total_runs'] > 0 else 0
        insights.append(f"Top Batting Anchor: {mvp['player']} leads with {mvp['runs']} runs (SR {mvp['strike_rate']}), representing {share}% of franchise run output.")

    # 4. Bowling unit effectiveness
    if ov["economy"] < 8.2:
        insights.append(f"Defensive Resilience: Outstanding bowling containment with a league-best {ov['economy']} economy rate.")
    elif ov["economy"] > 9.2:
        insights.append(f"Death Over Vulnerability: High concession rate ({ov['economy']} economy) indicates late-innings defensive gaps.")
    else:
        insights.append(f"Standard Bowling Control: Sustaining an average economy of {ov['economy']} across all phases.")

    # 5. Bowling MVP
    if not top_bowl.empty:
        lead_b = top_bowl.iloc[0]
        insights.append(f"Strike Bowler: {lead_b['player']} spearheads the attack with {lead_b['wickets']} wickets (Econ: {lead_b['economy']}).")

    return insights

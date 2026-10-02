"""
👤 Page 4: Player Comparison
Individual head-to-head benchmarking for batters, bowlers, and all-rounders
with 5-dimensional skill spider charts and metric tables.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import query
from analytics.comparison import compare_players
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles
from visualization.comparison_charts import plot_player_comparison_bars

st.set_page_config(page_title="Player Comparison | IPL Hub", page_icon="👤", layout="wide")
apply_custom_styles()

st.markdown("# 👤 Individual Player Head-to-Head Benchmarking")
st.markdown("Compare scoring dynamics, boundary frequencies, consistency averages, and bowling figures.")

# ── Pull players directly from the batting & bowling tables (real scraped names) ──
bat_players_df = query("""
    SELECT DISTINCT b.player, b.team,
        SUM(b.runs) as total_runs,
        COUNT(b.id) as innings
    FROM batting b
    GROUP BY b.player, b.team
    HAVING innings >= 3
    ORDER BY total_runs DESC
""")

bowl_players_df = query("""
    SELECT DISTINCT bw.player, bw.team,
        SUM(bw.wickets) as total_wickets,
        COUNT(DISTINCT bw.match_id) as matches
    FROM bowling bw
    GROUP BY bw.player, bw.team
    HAVING matches >= 2
    ORDER BY total_wickets DESC
""")

all_players_df = query("""
    SELECT DISTINCT player, team FROM batting
    UNION
    SELECT DISTINCT player, team FROM bowling
    ORDER BY player ASC
""")

# Role filter — based on whether they appear more in batting or bowling data
role_filter = st.radio(
    "Filter Players by Role:",
    ["All Players", "Top Batsmen (by runs)", "Top Bowlers (by wickets)"],
    horizontal=True
)

if role_filter == "Top Batsmen (by runs)":
    player_list = bat_players_df["player"].tolist()
elif role_filter == "Top Bowlers (by wickets)":
    player_list = bowl_players_df["player"].tolist()
else:
    player_list = all_players_df["player"].tolist()

if not player_list:
    st.warning("No player data found. Please run load_data.py first.")
    st.stop()

# ── Player selectors ─────────────────────────────────────────────────────────
p_col1, p_col2 = st.columns(2)

# Smart defaults — pick well-known players if present
preferred_a = ["V Kohli", "RG Sharma", "MS Dhoni", "Rohit Sharma", "Virat Kohli"]
preferred_b = ["RG Sharma", "V Kohli", "KD Karthik", "Rohit Sharma", "MS Dhoni"]

def find_default(prefs, lst, exclude=None):
    for p in prefs:
        if p in lst and p != exclude:
            return p
    return lst[0] if lst else ""

with p_col1:
    default_a = find_default(preferred_a, player_list)
    player_a = st.selectbox("Select Player A", player_list,
                            index=player_list.index(default_a) if default_a in player_list else 0)

with p_col2:
    default_b = find_default(preferred_b, player_list, exclude=player_a)
    player_b = st.selectbox("Select Player B", player_list,
                            index=player_list.index(default_b) if default_b in player_list else min(1, len(player_list)-1))

# ── Get team for each player from batting table ───────────────────────────────
def get_player_team(player_name):
    """Get the most recent team a player batted/bowled for."""
    res = query("""
        SELECT team, COUNT(*) as cnt FROM batting
        WHERE player = ? GROUP BY team ORDER BY cnt DESC LIMIT 1
    """, (player_name,))
    if not res.empty:
        return res.iloc[0]["team"]
    res2 = query("""
        SELECT team, COUNT(*) as cnt FROM bowling
        WHERE player = ? GROUP BY team ORDER BY cnt DESC LIMIT 1
    """, (player_name,))
    if not res2.empty:
        return res2.iloc[0]["team"]
    return "MI"

team_a = get_player_team(player_a)
team_b = get_player_team(player_b)
team_meta_a = get_franchise_meta(team_a)
team_meta_b = get_franchise_meta(team_b)

# ── Get comparison stats ─────────────────────────────────────────────────────
cmp_res = compare_players(player_a, player_b)
bat_a  = cmp_res["bat_a"]
bat_b  = cmp_res["bat_b"]
bowl_a = cmp_res["bowl_a"]
bowl_b = cmp_res["bowl_b"]

st.markdown("---")

# ── Profile Cards ────────────────────────────────────────────────────────────
c_a, c_b = st.columns(2)
with c_a:
    bat_info_a = f"{bat_a.get('runs', 0):,} runs in {bat_a.get('innings', 0)} innings" if bat_a else "No batting data"
    bowl_info_a = f"{bowl_a.get('wickets', 0)} wickets in {bowl_a.get('matches', 0)} matches" if bowl_a else ""
    st.markdown(f"""<div class="analytics-card" style="border-left:5px solid {team_meta_a['accent']}; padding:1.3rem 1.6rem;">
<div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">{team_meta_a['emoji']} {team_meta_a['full_name']} ({team_a})</div>
<h2 style="margin:0.2rem 0; color:#FFFFFF; font-weight:800;">{player_a}</h2>
<div style="color:#94A3B8; font-size:0.9rem; margin-top:0.3rem;">{bat_info_a}</div>
{"<div style='color:#94A3B8; font-size:0.9rem;'>" + bowl_info_a + "</div>" if bowl_info_a else ""}
</div>""", unsafe_allow_html=True)

with c_b:
    bat_info_b = f"{bat_b.get('runs', 0):,} runs in {bat_b.get('innings', 0)} innings" if bat_b else "No batting data"
    bowl_info_b = f"{bowl_b.get('wickets', 0)} wickets in {bowl_b.get('matches', 0)} matches" if bowl_b else ""
    st.markdown(f"""<div class="analytics-card" style="border-left:5px solid {team_meta_b['accent']}; padding:1.3rem 1.6rem;">
<div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">{team_meta_b['emoji']} {team_meta_b['full_name']} ({team_b})</div>
<h2 style="margin:0.2rem 0; color:#FFFFFF; font-weight:800;">{player_b}</h2>
<div style="color:#94A3B8; font-size:0.9rem; margin-top:0.3rem;">{bat_info_b}</div>
{"<div style='color:#94A3B8; font-size:0.9rem;'>" + bowl_info_b + "</div>" if bowl_info_b else ""}
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Batting Comparison ───────────────────────────────────────────────────────
st.subheader("🏏 Batting Head-to-Head Breakdown")

if bat_a or bat_b:
    bc1, bc2 = st.columns([1.4, 1.2])
    with bc1:
        st.plotly_chart(plot_player_comparison_bars(bat_a, bat_b, player_a, player_b), use_container_width=True)

    with bc2:
        categories = ["Volume", "Consistency", "Strike Rate", "Sixes Rate", "Milestones"]

        def norm_p(b):
            if not b:
                return [10, 10, 10, 10, 10]
            v   = min(100.0, max(10.0, b.get("runs", 0) / 700 * 100))
            c   = min(100.0, max(10.0, b.get("average", 0) / 55 * 100))
            s   = min(100.0, max(10.0, (b.get("strike_rate", 100) - 100) / (180 - 100) * 100))
            six = min(100.0, max(10.0, b.get("sixes", 0) / 35 * 100))
            m   = min(100.0, max(10.0, (b.get("fifties", 0) * 20) + (b.get("hundreds", 0) * 40)))
            return [v, c, s, six, m]

        va   = norm_p(bat_a) + [norm_p(bat_a)[0]]
        vb   = norm_p(bat_b) + [norm_p(bat_b)[0]]
        cat_l = categories + [categories[0]]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=va, theta=cat_l, fill="toself", name=player_a,
                                         line_color=team_meta_a["accent"]))
        fig_r.add_trace(go.Scatterpolar(r=vb, theta=cat_l, fill="toself", name=player_b,
                                         line_color=team_meta_b["accent"]))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template="plotly_dark",
            paper_bgcolor="#11151F",
            title="Batting Skill Radar",
            margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(fig_r, use_container_width=True)

    bat_comparison = pd.DataFrame([
        {"Metric": "Innings Played",  player_a: bat_a.get("innings", 0) if bat_a else "—",      player_b: bat_b.get("innings", 0) if bat_b else "—"},
        {"Metric": "Career Runs",     player_a: f"{bat_a.get('runs', 0):,}" if bat_a else "—",  player_b: f"{bat_b.get('runs', 0):,}" if bat_b else "—"},
        {"Metric": "Batting Average", player_a: bat_a.get("average", 0) if bat_a else "—",      player_b: bat_b.get("average", 0) if bat_b else "—"},
        {"Metric": "Strike Rate",     player_a: bat_a.get("strike_rate", 0) if bat_a else "—",  player_b: bat_b.get("strike_rate", 0) if bat_b else "—"},
        {"Metric": "Fours (4s)",      player_a: bat_a.get("fours", 0) if bat_a else "—",        player_b: bat_b.get("fours", 0) if bat_b else "—"},
        {"Metric": "Sixes (6s)",      player_a: bat_a.get("sixes", 0) if bat_a else "—",        player_b: bat_b.get("sixes", 0) if bat_b else "—"},
        {"Metric": "Fifties (50s)",   player_a: bat_a.get("fifties", 0) if bat_a else "—",      player_b: bat_b.get("fifties", 0) if bat_b else "—"},
        {"Metric": "Hundreds (100s)", player_a: bat_a.get("hundreds", 0) if bat_a else "—",     player_b: bat_b.get("hundreds", 0) if bat_b else "—"},
        {"Metric": "Highest Score",   player_a: bat_a.get("highest_score", 0) if bat_a else "—",player_b: bat_b.get("highest_score", 0) if bat_b else "—"},
    ])
    st.table(bat_comparison.set_index("Metric"))
else:
    st.info(f"No batting data found for {player_a} or {player_b}.")

# ── Bowling Comparison ───────────────────────────────────────────────────────
if bowl_a or bowl_b:
    st.markdown("---")
    st.subheader("🎯 Bowling Head-to-Head Breakdown")
    bowl_comparison = pd.DataFrame([
        {"Metric": "Matches Bowled",        player_a: bowl_a.get("matches", 0) if bowl_a else "—",       player_b: bowl_b.get("matches", 0) if bowl_b else "—"},
        {"Metric": "Overs Bowled",          player_a: bowl_a.get("overs", 0) if bowl_a else "—",         player_b: bowl_b.get("overs", 0) if bowl_b else "—"},
        {"Metric": "Wickets Taken",         player_a: bowl_a.get("wickets", 0) if bowl_a else "—",       player_b: bowl_b.get("wickets", 0) if bowl_b else "—"},
        {"Metric": "Economy Rate (RPO)",    player_a: bowl_a.get("economy", 0) if bowl_a else "—",       player_b: bowl_b.get("economy", 0) if bowl_b else "—"},
        {"Metric": "Bowling Average",       player_a: bowl_a.get("bowling_avg", "N/A") if bowl_a else "—", player_b: bowl_b.get("bowling_avg", "N/A") if bowl_b else "—"},
        {"Metric": "Strike Rate (Balls/Wkt)",player_a: bowl_a.get("bowling_sr", "N/A") if bowl_a else "—", player_b: bowl_b.get("bowling_sr", "N/A") if bowl_b else "—"},
        {"Metric": "Maidens Bowled",        player_a: bowl_a.get("maidens", 0) if bowl_a else "—",       player_b: bowl_b.get("maidens", 0) if bowl_b else "—"},
    ])
    st.table(bowl_comparison.set_index("Metric"))

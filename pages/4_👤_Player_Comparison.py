"""
Page 4: Player Comparison
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

st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #0D1827 0%, #101D30 60%, #091422 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(99, 102, 241, 0.18);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 280px; height: 100%;
    background: radial-gradient(circle at right, rgba(99, 102, 241, 0.1) 0%, transparent 65%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #818CF8;
    margin-bottom: 0.5rem;
}
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.6rem 0;
}
.player-profile-card {
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    border-radius: 14px;
    padding: 1.5rem 1.6rem;
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
    transition: all 0.25s ease;
    height: 100%;
}
.stat-table-wrapper {
    background: linear-gradient(160deg, #0E1626 0%, #0A1020 100%);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.chart-wrapper {
    background: linear-gradient(160deg, #0E1626 0%, #0A1020 100%);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 1rem 1.2rem 0.5rem;
    margin-bottom: 1rem;
}
.chart-title {
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    margin-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 0.5rem;
}
.role-chip {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    background: rgba(129, 140, 248, 0.12);
    color: #A5B4FC;
    border: 1px solid rgba(129, 140, 248, 0.25);
    margin-right: 0.4rem;
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">Analytics Module 04</div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">Player Head-to-Head Benchmarking</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">Compare scoring dynamics, boundary frequencies, consistency averages, bowling figures, and skill radar profiles.</p>
</div>
""", unsafe_allow_html=True)

# ── Pull players from batting & bowling tables (real scraped names) ────────────
bat_players_df = query("""
SELECT b.player,
    SUM(b.runs) as total_runs,
    COUNT(*) as innings_count
FROM batting b
GROUP BY b.player
HAVING COUNT(*) >= 1
ORDER BY total_runs DESC
""")

bowl_players_df = query("""
SELECT bw.player,
    SUM(bw.wickets) as total_wickets,
    COUNT(DISTINCT bw.match_id) as match_count
FROM bowling bw
GROUP BY bw.player
HAVING COUNT(DISTINCT bw.match_id) >= 1
ORDER BY total_wickets DESC
""")

all_players_df = query("""
SELECT DISTINCT player FROM batting
UNION
SELECT DISTINCT player FROM bowling
ORDER BY player ASC
""")

if all_players_df.empty:
    all_players_df = query("SELECT DISTINCT player_name as player FROM players ORDER BY player_name ASC")

# ── Role Filter ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Filter Players by Role</div>', unsafe_allow_html=True)
role_filter = st.radio(
    "Filter Players by Role:",
    ["All Players", "Top Batsmen (by runs)", "Top Bowlers (by wickets)"],
    horizontal=True,
    label_visibility="collapsed"
)

if role_filter == "Top Batsmen (by runs)" and not bat_players_df.empty:
    player_list = bat_players_df["player"].tolist()
elif role_filter == "Top Bowlers (by wickets)" and not bowl_players_df.empty:
    player_list = bowl_players_df["player"].tolist()
elif not all_players_df.empty:
    player_list = all_players_df["player"].tolist()
else:
    player_list = []

if not player_list:
    st.error("No player data found in database. Ensure load_data.py has run and database/ipl.db is present.")
    st.info("Restart using: `streamlit run app.py` from the `d:\\IPL_statistics` directory.")
    st.stop()

# ── Player Selectors ─────────────────────────────────────────────────────────
p_col1, p_col2 = st.columns(2)

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

# ── Get team for each player ──────────────────────────────────────────────────
def get_player_team(player_name):
    res = query("SELECT team, COUNT(*) as cnt FROM batting WHERE player = ? GROUP BY team ORDER BY cnt DESC LIMIT 1", (player_name,))
    if not res.empty:
        return res.iloc[0]["team"]
    res2 = query("SELECT team, COUNT(*) as cnt FROM bowling WHERE player = ? GROUP BY team ORDER BY cnt DESC LIMIT 1", (player_name,))
    if not res2.empty:
        return res2.iloc[0]["team"]
    return "MI"

team_a = get_player_team(player_a)
team_b = get_player_team(player_b)
team_meta_a = get_franchise_meta(team_a)
team_meta_b = get_franchise_meta(team_b)

# ── Comparison Stats ──────────────────────────────────────────────────────────
cmp_res = compare_players(player_a, player_b)
bat_a  = cmp_res["bat_a"]
bat_b  = cmp_res["bat_b"]
bowl_a = cmp_res["bowl_a"]
bowl_b = cmp_res["bowl_b"]

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Player Profile Cards ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Player Profiles</div>', unsafe_allow_html=True)
c_a, c_b = st.columns(2)

with c_a:
    bat_info_a = f"{bat_a.get('runs', 0):,} runs in {bat_a.get('innings', 0)} innings" if bat_a else "No batting data"
    bowl_info_a = f"{bowl_a.get('wickets', 0)} wickets in {bowl_a.get('matches', 0)} matches" if bowl_a else None
    st.markdown(f"""
<div class="player-profile-card" style="border-left:5px solid {team_meta_a['accent']};">
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">{team_meta_a['emoji']} {team_meta_a['full_name']} · {team_a}</div>
<h2 style="margin:0.3rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:1.6rem; letter-spacing:-0.02em;">{player_a}</h2>
<div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem;">
<span class="role-chip">Batting</span>
{"<span class='role-chip'>Bowling</span>" if bowl_a else ""}
</div>
<div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.5rem;">
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; margin-bottom:0.3rem;">Batting</div>
<div style="color:#E2E8F0; font-size:0.9rem;">{bat_info_a}</div>
</div>
{"<div style='background:rgba(255,255,255,0.04); border-radius:8px; padding:0.75rem 1rem;'><div style='font-size:0.7rem; font-family:Space Mono,monospace; color:#64748B; text-transform:uppercase; margin-bottom:0.3rem;'>Bowling</div><div style='color:#E2E8F0; font-size:0.9rem;'>" + bowl_info_a + "</div></div>" if bowl_info_a else ""}
</div>
""", unsafe_allow_html=True)

with c_b:
    bat_info_b = f"{bat_b.get('runs', 0):,} runs in {bat_b.get('innings', 0)} innings" if bat_b else "No batting data"
    bowl_info_b = f"{bowl_b.get('wickets', 0)} wickets in {bowl_b.get('matches', 0)} matches" if bowl_b else None
    st.markdown(f"""
<div class="player-profile-card" style="border-left:5px solid {team_meta_b['accent']};">
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">{team_meta_b['emoji']} {team_meta_b['full_name']} · {team_b}</div>
<h2 style="margin:0.3rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:1.6rem; letter-spacing:-0.02em;">{player_b}</h2>
<div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem;">
<span class="role-chip">Batting</span>
{"<span class='role-chip'>Bowling</span>" if bowl_b else ""}
</div>
<div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.5rem;">
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; margin-bottom:0.3rem;">Batting</div>
<div style="color:#E2E8F0; font-size:0.9rem;">{bat_info_b}</div>
</div>
{"<div style='background:rgba(255,255,255,0.04); border-radius:8px; padding:0.75rem 1rem;'><div style='font-size:0.7rem; font-family:Space Mono,monospace; color:#64748B; text-transform:uppercase; margin-bottom:0.3rem;'>Bowling</div><div style='color:#E2E8F0; font-size:0.9rem;'>" + bowl_info_b + "</div></div>" if bowl_info_b else ""}
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Batting Head-to-Head ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Batting Head-to-Head Breakdown</div>', unsafe_allow_html=True)

if bat_a or bat_b:
    bc1, bc2 = st.columns([1.4, 1.2])
    with bc1:
        st.markdown('<div class="chart-wrapper"><div class="chart-title">Batting Metrics Comparison — Bar Chart</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_player_comparison_bars(bat_a, bat_b, player_a, player_b), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
                                         line_color=team_meta_a["accent"], fillcolor=team_meta_a["accent"] + "30"))
        fig_r.add_trace(go.Scatterpolar(r=vb, theta=cat_l, fill="toself", name=player_b,
                                         line_color=team_meta_b["accent"], fillcolor=team_meta_b["accent"] + "30"))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.08)", color="#64748B"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", color="#94A3B8"),
                bgcolor="#0E1626"
            ),
            template="plotly_dark",
            paper_bgcolor="#0E1626",
            plot_bgcolor="#0E1626",
            font_color="#94A3B8",
            title=dict(text="Batting Skill Radar", font_color="#CBD5E1", font_size=13),
            margin=dict(l=30, r=30, t=45, b=30),
            legend=dict(font_color="#94A3B8", bgcolor="rgba(0,0,0,0)")
        )
        st.markdown('<div class="chart-wrapper"><div class="chart-title">5-Axis Batting Skill Radar</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Batting Table
    st.markdown('<div class="section-label" style="margin-top:0.5rem;">Batting Statistics Matrix</div>', unsafe_allow_html=True)
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

# ── Bowling Head-to-Head ──────────────────────────────────────────────────────
if bowl_a or bowl_b:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Bowling Head-to-Head Breakdown</div>', unsafe_allow_html=True)
    bowl_comparison = pd.DataFrame([
        {"Metric": "Matches Bowled",         player_a: bowl_a.get("matches", 0) if bowl_a else "—",           player_b: bowl_b.get("matches", 0) if bowl_b else "—"},
        {"Metric": "Overs Bowled",           player_a: bowl_a.get("overs", 0) if bowl_a else "—",             player_b: bowl_b.get("overs", 0) if bowl_b else "—"},
        {"Metric": "Wickets Taken",          player_a: bowl_a.get("wickets", 0) if bowl_a else "—",           player_b: bowl_b.get("wickets", 0) if bowl_b else "—"},
        {"Metric": "Economy Rate (RPO)",     player_a: bowl_a.get("economy", 0) if bowl_a else "—",           player_b: bowl_b.get("economy", 0) if bowl_b else "—"},
        {"Metric": "Bowling Average",        player_a: bowl_a.get("bowling_avg", "N/A") if bowl_a else "—",  player_b: bowl_b.get("bowling_avg", "N/A") if bowl_b else "—"},
        {"Metric": "Strike Rate (Balls/Wkt)",player_a: bowl_a.get("bowling_sr", "N/A") if bowl_a else "—",   player_b: bowl_b.get("bowling_sr", "N/A") if bowl_b else "—"},
        {"Metric": "Maidens Bowled",         player_a: bowl_a.get("maidens", 0) if bowl_a else "—",           player_b: bowl_b.get("maidens", 0) if bowl_b else "—"},
    ])
    st.table(bowl_comparison.set_index("Metric"))

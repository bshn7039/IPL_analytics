"""
👤 Module 04: Player Head-to-Head Benchmarking — IPL Telemetry Pro
Individual head-to-head benchmarking for batters, bowlers, and all-rounders
with 5-dimensional skill spider charts, metric tables, and situational splits.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import query
from analytics.comparison import compare_players
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles, render_sidebar_system_status
from visualization.comparison_charts import plot_player_comparison_bars

st.set_page_config(page_title="Player Comparison | IPL Telemetry Pro", page_icon="👤", layout="wide")
apply_custom_styles()
render_sidebar_system_status()

# ── Pull players from batting & bowling tables ──
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

# ── Top Bar: Role Filters & Selectors ──
st.markdown('<div class="section-label" style="color:#818CF8;">Player Cohort Filter</div>', unsafe_allow_html=True)
r_col1, r_col2 = st.columns([2.5, 1.5])
with r_col1:
    role_filter = st.radio(
        "Filter Players by Role:",
        ["All Players", "Top Batsmen (by runs)", "Top Bowlers (by wickets)"],
        horizontal=True,
        label_visibility="collapsed"
    )
with r_col2:
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:flex-end; gap:0.6rem; height:100%;">
        <span class="telemetry-chip-purple">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#A855F7; box-shadow:0 0 8px #A855F7;"></span>
            PLAYER RADAR TELEMETRY
        </span>
        <span class="telemetry-chip">CAREER METRICS</span>
    </div>
    """, unsafe_allow_html=True)

if role_filter == "Top Batsmen (by runs)" and not bat_players_df.empty:
    player_list = bat_players_df["player"].tolist()
elif role_filter == "Top Bowlers (by wickets)" and not bowl_players_df.empty:
    player_list = bowl_players_df["player"].tolist()
elif not all_players_df.empty:
    player_list = all_players_df["player"].tolist()
else:
    player_list = []

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

# Get team for each player
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

# ── Page Header ──
st.markdown(f"""
<div class="page-header" style="border-left: 6px solid #818CF8;">
    <div class="section-label" style="color:#A5B4FC;">ANALYTICS MODULE 04 • PLAYER HEAD-TO-HEAD BENCHMARKING</div>
    <h1 style="margin:0 0 0.4rem; font-size:2.2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">
        Player Head-to-Head Benchmarking: {player_a} vs {player_b}
    </h1>
    <p style="margin:0; color:#94A3B8; font-size:0.92rem;">
        Scoring dynamics, boundary frequencies, consistency averages, bowling figures, and multi-dimensional skill radar profiles.
    </p>
</div>
""", unsafe_allow_html=True)

cmp_res = compare_players(player_a, player_b)
bat_a  = cmp_res["bat_a"]
bat_b  = cmp_res["bat_b"]
bowl_a = cmp_res["bowl_a"]
bowl_b = cmp_res["bowl_b"]

# ── Side-by-Side Player Profile Hero Cards ──
st.markdown('<div class="section-label" style="color:#818CF8;">Player Profile Direct Benchmarks</div>', unsafe_allow_html=True)
c_a, c_b = st.columns(2)

with c_a:
    bat_info_a = f"{bat_a.get('runs', 0):,} runs in {bat_a.get('innings', 0)} innings (Avg {bat_a.get('average', 0)} · SR {bat_a.get('strike_rate', 0)})" if bat_a else "No batting record"
    bowl_info_a = f"{bowl_a.get('wickets', 0)} wickets in {bowl_a.get('matches', 0)} matches (Econ {bowl_a.get('economy', 0)})" if bowl_a else None
    st.markdown(f"""
    <div class="player-profile-card" style="border-left: 5px solid {team_meta_a['accent']};">
        <div style="font-size:0.75rem; font-family:'Space Mono',monospace; color:#94A3B8; text-transform:uppercase;">
            {team_meta_a['emoji']} {team_meta_a['full_name']} · {team_a}
        </div>
        <h2 style="margin:0.2rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:1.8rem; letter-spacing:-0.02em;">{player_a}</h2>
        <div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem;">
            <span class="telemetry-chip">🏏 Batsman</span>
            {"<span class='telemetry-chip-red'>🎯 Bowler</span>" if bowl_a else ""}
            <span class="telemetry-chip-amber">HS: {bat_a.get('highest_score', 0) if bat_a else '—'}</span>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem; margin-bottom:0.6rem;">
            <div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase;">Batting Performance</div>
            <div style="color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;">{bat_info_a}</div>
        </div>
        {"<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem;'><div style='font-size:0.7rem; font-family:Space Mono,monospace; color:#64748B; text-transform:uppercase;'>Bowling Figures</div><div style='color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;'>" + bowl_info_a + "</div></div>" if bowl_info_a else ""}
    </div>
    """, unsafe_allow_html=True)

with c_b:
    bat_info_b = f"{bat_b.get('runs', 0):,} runs in {bat_b.get('innings', 0)} innings (Avg {bat_b.get('average', 0)} · SR {bat_b.get('strike_rate', 0)})" if bat_b else "No batting record"
    bowl_info_b = f"{bowl_b.get('wickets', 0)} wickets in {bowl_b.get('matches', 0)} matches (Econ {bowl_b.get('economy', 0)})" if bowl_b else None
    st.markdown(f"""
    <div class="player-profile-card" style="border-left: 5px solid {team_meta_b['accent']};">
        <div style="font-size:0.75rem; font-family:'Space Mono',monospace; color:#94A3B8; text-transform:uppercase;">
            {team_meta_b['emoji']} {team_meta_b['full_name']} · {team_b}
        </div>
        <h2 style="margin:0.2rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:1.8rem; letter-spacing:-0.02em;">{player_b}</h2>
        <div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem;">
            <span class="telemetry-chip">🏏 Batsman</span>
            {"<span class='telemetry-chip-red'>🎯 Bowler</span>" if bowl_b else ""}
            <span class="telemetry-chip-amber">HS: {bat_b.get('highest_score', 0) if bat_b else '—'}</span>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem; margin-bottom:0.6rem;">
            <div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase;">Batting Performance</div>
            <div style="color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;">{bat_info_b}</div>
        </div>
        {"<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem;'><div style='font-size:0.7rem; font-family:Space Mono,monospace; color:#64748B; text-transform:uppercase;'>Bowling Figures</div><div style='color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;'>" + bowl_info_b + "</div></div>" if bowl_info_b else ""}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Dual Visualizations Row ──
if bat_a or bat_b:
    bc1, bc2 = st.columns([1.4, 1.2])
    with bc1:
        st.markdown('<div class="chart-wrapper"><div class="chart-title"><span>📊 Direct Stat Variance — Grouped Metrics</span><span class="telemetry-chip">BARS</span></div>', unsafe_allow_html=True)
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
                                         line=dict(color=team_meta_a["accent"], width=2.5),
                                         fillcolor=team_meta_a["accent"] + "30"))
        fig_r.add_trace(go.Scatterpolar(r=vb, theta=cat_l, fill="toself", name=player_b,
                                         line=dict(color=team_meta_b["accent"], width=2.5),
                                         fillcolor=team_meta_b["accent"] + "30"))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.08)", color="#64748B", tickfont=dict(family="Space Mono", size=9)),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", color="#FFFFFF", tickfont=dict(family="Space Mono", size=10)),
                bgcolor="rgba(0,0,0,0)"
            ),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif", color="#DAE2FD"),
            margin=dict(l=30, r=30, t=30, b=30),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(family="Space Mono", size=11, color="#DAE2FD"))
        )
        st.markdown('<div class="chart-wrapper"><div class="chart-title"><span>🕸️ 5-Dimensional Skill Spider Radar</span><span class="telemetry-chip-purple">SKILL RADAR</span></div>', unsafe_allow_html=True)
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Batting Table
    st.markdown('<div class="section-label" style="color:#818CF8; margin-top:0.8rem;">Batting Statistics Matrix Breakdown</div>', unsafe_allow_html=True)
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

# Bowling Table if bowlers
if bowl_a or bowl_b:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="color:#EF4444;">Bowling Statistics Matrix Breakdown</div>', unsafe_allow_html=True)
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

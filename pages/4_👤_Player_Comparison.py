"""
👤 Module 04: Player Head-to-Head Benchmarking — IPL Analytics
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
from visualization.comparison_charts import plot_player_comparison_bars, plot_player_bowling_comparison_bars

st.set_page_config(page_title="Player Comparison | IPL Analytics", page_icon="👤", layout="wide")
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

preferred_a = ["V Kohli", "RG Sharma", "MS Dhoni", "Rohit Sharma", "Virat Kohli", "JJ Bumrah", "YS Chahal"]
preferred_b = ["RG Sharma", "V Kohli", "KD Karthik", "Rohit Sharma", "MS Dhoni", "Rashid Khan", "Kuldeep Yadav"]

def find_default(prefs, lst, exclude=None):
    for p in prefs:
        if p in lst and p != exclude:
            return p
    for item in lst:
        if item != exclude:
            return item
    return lst[0] if lst else ""

with p_col1:
    default_a = find_default(preferred_a, player_list)
    player_a = st.selectbox("Select Player A", player_list,
                            index=player_list.index(default_a) if default_a in player_list else 0)

with p_col2:
    default_b = find_default(preferred_b, player_list, exclude=player_a)
    default_b_idx = player_list.index(default_b) if default_b in player_list else min(1, max(0, len(player_list)-1))
    player_b = st.selectbox("Select Player B", player_list, index=default_b_idx)

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
bat_a  = cmp_res.get("bat_a")
bat_b  = cmp_res.get("bat_b")
bowl_a = cmp_res.get("bowl_a")
bowl_b = cmp_res.get("bowl_b")

# ── Side-by-Side Player Profile Hero Cards ──
st.markdown('<div class="section-label" style="color:#818CF8;">Player Profile Direct Benchmarks</div>', unsafe_allow_html=True)
c_a, c_b = st.columns(2)

with c_a:
    bat_info_a = f"{bat_a.get('runs', 0):,} runs in {bat_a.get('innings', 0)} innings (Avg {bat_a.get('average', 0)} · SR {bat_a.get('strike_rate', 0)})" if bat_a else "No batting record logged"
    bowl_info_a = f"{bowl_a.get('wickets', 0)} wickets in {bowl_a.get('matches', 0)} matches (Econ {bowl_a.get('economy', 0)})" if bowl_a else None
    bowl_markup_a = f"<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem;'><div style='font-size:0.7rem; font-family:Space Mono,monospace; color:#64748B; text-transform:uppercase;'>Bowling Figures</div><div style='color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;'>{bowl_info_a}</div></div>" if bowl_info_a else ""

    st.markdown(f"""
    <div class="player-profile-card" style="border-left: 5px solid {team_meta_a['accent']};">
        <div style="font-size:0.75rem; font-family:'Space Mono',monospace; color:#94A3B8; text-transform:uppercase;">
            {team_meta_a['emoji']} {team_meta_a['full_name']} · {team_a}
        </div>
        <h2 style="margin:0.2rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:1.8rem; letter-spacing:-0.02em;">{player_a}</h2>
        <div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem;">
            {"<span class='telemetry-chip'>🏏 Batsman</span>" if bat_a else ""}
            {"<span class='telemetry-chip-red'>🎯 Bowler</span>" if bowl_a else ""}
            <span class="telemetry-chip-amber">HS: {bat_a.get('highest_score', 0) if bat_a else '—'}</span>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem; margin-bottom:0.6rem;">
            <div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase;">Batting Performance</div>
            <div style="color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;">{bat_info_a}</div>
        </div>
        {bowl_markup_a}
    </div>
    """, unsafe_allow_html=True)

with c_b:
    bat_info_b = f"{bat_b.get('runs', 0):,} runs in {bat_b.get('innings', 0)} innings (Avg {bat_b.get('average', 0)} · SR {bat_b.get('strike_rate', 0)})" if bat_b else "No batting record logged"
    bowl_info_b = f"{bowl_b.get('wickets', 0)} wickets in {bowl_b.get('matches', 0)} matches (Econ {bowl_b.get('economy', 0)})" if bowl_b else None
    bowl_markup_b = f"<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem;'><div style='font-size:0.7rem; font-family:Space Mono,monospace; color:#64748B; text-transform:uppercase;'>Bowling Figures</div><div style='color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;'>{bowl_info_b}</div></div>" if bowl_info_b else ""

    st.markdown(f"""
    <div class="player-profile-card" style="border-left: 5px solid {team_meta_b['accent']};">
        <div style="font-size:0.75rem; font-family:'Space Mono',monospace; color:#94A3B8; text-transform:uppercase;">
            {team_meta_b['emoji']} {team_meta_b['full_name']} · {team_b}
        </div>
        <h2 style="margin:0.2rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:1.8rem; letter-spacing:-0.02em;">{player_b}</h2>
        <div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem;">
            {"<span class='telemetry-chip'>🏏 Batsman</span>" if bat_b else ""}
            {"<span class='telemetry-chip-red'>🎯 Bowler</span>" if bowl_b else ""}
            <span class="telemetry-chip-amber">HS: {bat_b.get('highest_score', 0) if bat_b else '—'}</span>
        </div>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1.1rem; margin-bottom:0.6rem;">
            <div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase;">Batting Performance</div>
            <div style="color:#FFFFFF; font-size:1rem; font-weight:700; margin-top:0.2rem;">{bat_info_b}</div>
        </div>
        {bowl_markup_b}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Dual Visualizations Row ──
bc1, bc2 = st.columns([1.4, 1.2])

has_batting = bool(bat_a or bat_b)
has_bowling = bool(bowl_a or bowl_b)

with bc1:
    if has_batting:
        st.markdown('<div class="chart-wrapper"><div class="chart-title"><span>📊 Direct Stat Variance — Batting Metrics</span><span class="telemetry-chip">BARS</span></div>', unsafe_allow_html=True)
        st.plotly_chart(plot_player_comparison_bars(bat_a, bat_b, player_a, player_b), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    elif has_bowling:
        st.markdown('<div class="chart-wrapper"><div class="chart-title"><span>🎯 Direct Stat Variance — Bowling Metrics</span><span class="telemetry-chip-red">BOWLING</span></div>', unsafe_allow_html=True)
        st.plotly_chart(plot_player_bowling_comparison_bars(bowl_a, bowl_b, player_a, player_b), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with bc2:
    if has_batting:
        categories = ["Volume", "Consistency", "Strike Rate", "Sixes Rate", "Milestones"]
        def norm_p(b):
            if not b:
                return [10.0, 10.0, 10.0, 10.0, 10.0]
            v   = min(100.0, max(10.0, b.get("runs", 0) / 700 * 100))
            c   = min(100.0, max(10.0, b.get("average", 0) / 55 * 100))
            s   = min(100.0, max(10.0, (b.get("strike_rate", 100) - 100) / (180 - 100) * 100))
            six = min(100.0, max(10.0, b.get("sixes", 0) / 35 * 100))
            m   = min(100.0, max(10.0, (b.get("fifties", 0) * 20) + (b.get("hundreds", 0) * 40)))
            return [v, c, s, six, m]

        va   = norm_p(bat_a) + [norm_p(bat_a)[0]]
        vb   = norm_p(bat_b) + [norm_p(bat_b)[0]]
        cat_l = categories + [categories[0]]
        radar_title = "🕸️ 5-Dimensional Batting Skill Radar"
    else:
        categories = ["Wickets", "Economy", "Strike Rate", "Maidens", "Volume"]
        def norm_bw(bw):
            if not bw:
                return [10.0, 10.0, 10.0, 10.0, 10.0]
            w   = min(100.0, max(10.0, bw.get("wickets", 0) / 100 * 100))
            econ = bw.get("economy", 8.5)
            e   = min(100.0, max(10.0, (11.0 - econ) / (11.0 - 6.5) * 100))
            sr  = bw.get("bowling_sr", 24.0) or 24.0
            s   = min(100.0, max(10.0, (30.0 - sr) / (30.0 - 14.0) * 100))
            m   = min(100.0, max(10.0, bw.get("maidens", 0) / 5 * 100))
            vol = min(100.0, max(10.0, bw.get("matches", 0) / 100 * 100))
            return [w, e, s, m, vol]

        va   = norm_bw(bowl_a) + [norm_bw(bowl_a)[0]]
        vb   = norm_bw(bowl_b) + [norm_bw(bowl_b)[0]]
        cat_l = categories + [categories[0]]
        radar_title = "🕸️ 5-Dimensional Bowling Skill Radar"

    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=va, theta=cat_l, fill="toself", name=player_a,
        line=dict(color=team_meta_a["accent"], width=2.5),
        fillcolor="rgba(129, 140, 248, 0.22)"
    ))
    fig_r.add_trace(go.Scatterpolar(
        r=vb, theta=cat_l, fill="toself", name=player_b,
        line=dict(color=team_meta_b["accent"], width=2.5),
        fillcolor="rgba(6, 182, 212, 0.22)"
    ))
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
    st.markdown(f'<div class="chart-wrapper"><div class="chart-title"><span>{radar_title}</span><span class="telemetry-chip-purple">SKILL RADAR</span></div>', unsafe_allow_html=True)
    st.plotly_chart(fig_r, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Batting Table ──
col_a = f"{player_a} (A)" if player_a == player_b else player_a
col_b = f"{player_b} (B)" if player_a == player_b else player_b

if bat_a or bat_b:
    st.markdown('<div class="section-label" style="color:#818CF8; margin-top:0.8rem;">Batting Statistics Matrix Breakdown</div>', unsafe_allow_html=True)
    
    val_inng_a = str(bat_a.get("innings", 0)) if bat_a else "—"
    val_inng_b = str(bat_b.get("innings", 0)) if bat_b else "—"
    
    val_runs_a = f"{bat_a.get('runs', 0):,}" if bat_a else "—"
    val_runs_b = f"{bat_b.get('runs', 0):,}" if bat_b else "—"
    
    val_avg_a = f"{float(bat_a.get('average', 0)):.2f}" if bat_a else "—"
    val_avg_b = f"{float(bat_b.get('average', 0)):.2f}" if bat_b else "—"
    
    val_sr_a = f"{float(bat_a.get('strike_rate', 0)):.2f}" if bat_a else "—"
    val_sr_b = f"{float(bat_b.get('strike_rate', 0)):.2f}" if bat_b else "—"
    
    val_4s_a = str(bat_a.get("fours", 0)) if bat_a else "—"
    val_4s_b = str(bat_b.get("fours", 0)) if bat_b else "—"
    
    val_6s_a = str(bat_a.get("sixes", 0)) if bat_a else "—"
    val_6s_b = str(bat_b.get("sixes", 0)) if bat_b else "—"
    
    val_50s_a = str(bat_a.get("fifties", 0)) if bat_a else "—"
    val_50s_b = str(bat_b.get("fifties", 0)) if bat_b else "—"
    
    val_100s_a = str(bat_a.get("hundreds", 0)) if bat_a else "—"
    val_100s_b = str(bat_b.get("hundreds", 0)) if bat_b else "—"
    
    val_hs_a = str(bat_a.get("highest_score", 0)) if bat_a else "—"
    val_hs_b = str(bat_b.get("highest_score", 0)) if bat_b else "—"

    bat_comparison = pd.DataFrame([
        {"Metric": "Innings Played",  col_a: val_inng_a,  col_b: val_inng_b},
        {"Metric": "Career Runs",     col_a: val_runs_a,  col_b: val_runs_b},
        {"Metric": "Batting Average", col_a: val_avg_a,   col_b: val_avg_b},
        {"Metric": "Strike Rate",     col_a: val_sr_a,    col_b: val_sr_b},
        {"Metric": "Fours (4s)",      col_a: val_4s_a,    col_b: val_4s_b},
        {"Metric": "Sixes (6s)",      col_a: val_6s_a,    col_b: val_6s_b},
        {"Metric": "Fifties (50s)",   col_a: val_50s_a,   col_b: val_50s_b},
        {"Metric": "Hundreds (100s)", col_a: val_100s_a,  col_b: val_100s_b},
        {"Metric": "Highest Score",   col_a: val_hs_a,    col_b: val_hs_b},
    ])
    st.table(bat_comparison.set_index("Metric"))

# ── Bowling Table ──
if bowl_a or bowl_b:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="color:#EF4444;">Bowling Statistics Matrix Breakdown</div>', unsafe_allow_html=True)
    
    val_m_a = str(bowl_a.get("matches", 0)) if bowl_a else "—"
    val_m_b = str(bowl_b.get("matches", 0)) if bowl_b else "—"
    
    val_ov_a = f"{float(bowl_a.get('overs', 0)):.1f}" if bowl_a else "—"
    val_ov_b = f"{float(bowl_b.get('overs', 0)):.1f}" if bowl_b else "—"
    
    val_wk_a = str(bowl_a.get("wickets", 0)) if bowl_a else "—"
    val_wk_b = str(bowl_b.get("wickets", 0)) if bowl_b else "—"
    
    val_ec_a = f"{float(bowl_a.get('economy', 0)):.2f}" if bowl_a else "—"
    val_ec_b = f"{float(bowl_b.get('economy', 0)):.2f}" if bowl_b else "—"
    
    val_ba_a = f"{float(bowl_a['bowling_avg']):.2f}" if (bowl_a and bowl_a.get("bowling_avg") is not None) else "—"
    val_ba_b = f"{float(bowl_b['bowling_avg']):.2f}" if (bowl_b and bowl_b.get("bowling_avg") is not None) else "—"
    
    val_sr_a = f"{float(bowl_a['bowling_sr']):.1f}" if (bowl_a and bowl_a.get("bowling_sr") is not None) else "—"
    val_sr_b = f"{float(bowl_b['bowling_sr']):.1f}" if (bowl_b and bowl_b.get("bowling_sr") is not None) else "—"
    
    val_md_a = str(bowl_a.get("maidens", 0)) if bowl_a else "—"
    val_md_b = str(bowl_b.get("maidens", 0)) if bowl_b else "—"

    bowl_comparison = pd.DataFrame([
        {"Metric": "Matches Bowled",         col_a: val_m_a,  col_b: val_m_b},
        {"Metric": "Overs Bowled",           col_a: val_ov_a, col_b: val_ov_b},
        {"Metric": "Wickets Taken",          col_a: val_wk_a, col_b: val_wk_b},
        {"Metric": "Economy Rate (RPO)",     col_a: val_ec_a, col_b: val_ec_b},
        {"Metric": "Bowling Average",        col_a: val_ba_a, col_b: val_ba_b},
        {"Metric": "Strike Rate (Balls/Wkt)",col_a: val_sr_a, col_b: val_sr_b},
        {"Metric": "Maidens Bowled",         col_a: val_md_a, col_b: val_md_b},
    ])
    st.table(bowl_comparison.set_index("Metric"))

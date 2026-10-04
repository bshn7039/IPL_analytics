"""
Page 1: Batting Analytics
Deep-dive examination of individual run production, scoring velocity, boundary rates,
and target-setting vs target-chasing effectiveness.
"""
import streamlit as st
import plotly.express as px
from database.db import query
from analytics.batting import (
    get_team_batting_summary, get_top_batsmen, get_batting_first_vs_chasing
)
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles
from visualization.batting_charts import (
    plot_runs_by_player, plot_runs_vs_strike_rate, plot_boundary_distribution_mpl
)

st.set_page_config(page_title="Batting Analytics | IPL Hub", page_icon="🏏", layout="wide")
apply_custom_styles()

st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #0D1527 0%, #131E35 60%, #0B1222 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(56, 189, 248, 0.18);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 280px; height: 100%;
    background: radial-gradient(circle at right, rgba(56, 189, 248, 0.1) 0%, transparent 65%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #38BDF8;
    margin-bottom: 0.5rem;
}
.kpi-card {
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
    text-align: center;
    transition: all 0.25s ease;
}
.kpi-card:hover {
    border-color: rgba(56, 189, 248, 0.35);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -6px rgba(56, 189, 248, 0.15);
}
.kpi-label {
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
}
.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
    margin: 0.2rem 0;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 500;
}
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.6rem 0;
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
.split-card {
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">Analytics Module 01</div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">Batting Performance Analytics</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">Run production efficiency, boundary velocity, scoring consistency, and situational split analysis across all seasons.</p>
</div>
""", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────────────────
seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c_s, c_t = st.columns(2)
with c_s:
    selected_season = st.selectbox("Season", seasons, index=0)
with c_t:
    selected_team = st.selectbox("Franchise", teams, index=0)

meta = get_franchise_meta(selected_team)
summary = get_team_batting_summary(selected_team, selected_season)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Franchise Batting Telemetry</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)

kpi_data = [
    (k1, "Total Runs", f"{summary['total_runs']:,}", "across all innings"),
    (k2, "Innings Average", f"{summary['avg_score']}", "runs per inning"),
    (k3, "Strike Rate", f"{summary['strike_rate']}", "runs per 100 balls"),
    (k4, "Fours Hit", f"{summary['total_fours']}", "boundary 4s"),
    (k5, "Sixes Hit", f"{summary['total_sixes']}", "boundary 6s"),
    (k6, "Boundary %", f"{summary['boundary_pct']}%", "runs from boundaries"),
]

for col, label, value, sub in kpi_data:
    with col:
        st.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">{label}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-sub">{sub}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Batting MVP Spotlight ─────────────────────────────────────────────────────
top_bat_df = get_top_batsmen(selected_team, selected_season, limit=25)
if not top_bat_df.empty:
    mvp = top_bat_df.iloc[0]
    st.markdown(f"""
<div class="analytics-card" style="border-left:5px solid {meta['accent']}; padding:1.5rem 1.8rem; margin-bottom:1.5rem;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
<div>
<div class="section-label" style="color:{meta['accent']};">Leading Run Scorer — {selected_season}</div>
<h2 style="margin:0.2rem 0 0.4rem; color:#FFFFFF; font-weight:800; font-size:1.7rem;">{mvp['player']}</h2>
<div style="display:flex; gap:1rem; flex-wrap:wrap;">
<span class="telemetry-chip">{mvp['innings']} innings</span>
<span class="telemetry-chip">HS: {mvp['highest_score']}</span>
<span class="telemetry-chip">{mvp['fifties']} fifties</span>
<span class="telemetry-chip">{mvp['hundreds']} hundreds</span>
</div>
</div>
<div style="text-align:right;">
<div style="font-size:2.4rem; font-weight:800; color:{meta['accent']}; font-variant-numeric:tabular-nums;">{mvp['runs']:,}</div>
<div style="font-size:0.8rem; font-family:'Space Mono',monospace; color:#94A3B8; margin-top:0.2rem;">RUNS SCORED</div>
<div style="color:#38BDF8; font-weight:700; font-size:1rem; margin-top:0.3rem;">Avg {mvp['average']} &nbsp;·&nbsp; SR {mvp['strike_rate']}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── Charts Row ───────────────────────────────────────────────────────────────
ch1, ch2 = st.columns([1.6, 1.1])
with ch1:
    st.markdown('<div class="chart-wrapper"><div class="chart-title">Top Run Scorers — Horizontal Leaderboard</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_runs_by_player(top_bat_df.head(10)), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with ch2:
    st.markdown('<div class="chart-wrapper"><div class="chart-title">Boundary Run Distribution</div>', unsafe_allow_html=True)
    mpl_fig = plot_boundary_distribution_mpl(summary["total_fours"], summary["total_sixes"], summary["total_runs"])
    st.pyplot(mpl_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Scatter Matrix ────────────────────────────────────────────────────────────
st.markdown('<div class="chart-wrapper"><div class="chart-title">Scoring Volume vs Aggression Matrix — Runs vs Strike Rate</div>', unsafe_allow_html=True)
st.plotly_chart(plot_runs_vs_strike_rate(top_bat_df), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Leaderboard Table ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label" style="margin-top:1rem;">Complete Batting Leaderboard</div>', unsafe_allow_html=True)
if not top_bat_df.empty:
    st.dataframe(
        top_bat_df.style.background_gradient(subset=["runs", "strike_rate"], cmap="Blues"),
        use_container_width=True
    )
else:
    st.warning("No batting records found for the selected franchise.")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Situational Split ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Situational Dynamics — Batting First vs Chasing</div>', unsafe_allow_html=True)
split = get_batting_first_vs_chasing(selected_team, selected_season)

sp1, sp2 = st.columns(2)
with sp1:
    st.markdown(f"""
<div class="split-card" style="border-left:4px solid #38BDF8;">
<div class="section-label" style="color:#38BDF8;">Setting Target (Bat First)</div>
<div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.8rem;">
<div>
<div style="color:#94A3B8; font-size:0.85rem;">Matches Setting Score</div>
<div style="color:#FFFFFF; font-size:1.5rem; font-weight:800; font-variant-numeric:tabular-nums;">{split['bat_first_matches']}</div>
</div>
<div>
<div style="color:#94A3B8; font-size:0.85rem;">Average Target</div>
<div style="color:#FFFFFF; font-size:1.5rem; font-weight:800; font-variant-numeric:tabular-nums;">{split['bat_first_avg']}</div>
</div>
<div style="text-align:right;">
<div style="color:#94A3B8; font-size:0.85rem;">Win Rate</div>
<div style="color:#38BDF8; font-size:2rem; font-weight:800;">{split['bat_first_win_pct']}%</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

with sp2:
    st.markdown(f"""
<div class="split-card" style="border-left:4px solid #F97316;">
<div class="section-label" style="color:#F97316;">Chasing Target (Bat Second)</div>
<div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.8rem;">
<div>
<div style="color:#94A3B8; font-size:0.85rem;">Matches Chasing</div>
<div style="color:#FFFFFF; font-size:1.5rem; font-weight:800; font-variant-numeric:tabular-nums;">{split['chasing_matches']}</div>
</div>
<div>
<div style="color:#94A3B8; font-size:0.85rem;">Average Chase</div>
<div style="color:#FFFFFF; font-size:1.5rem; font-weight:800; font-variant-numeric:tabular-nums;">{split['chasing_avg']}</div>
</div>
<div style="text-align:right;">
<div style="color:#94A3B8; font-size:0.85rem;">Win Rate</div>
<div style="color:#F97316; font-size:2rem; font-weight:800;">{split['chasing_win_pct']}%</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

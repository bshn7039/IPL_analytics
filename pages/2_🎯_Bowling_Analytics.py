"""
Page 2: Bowling Analytics
Detailed evaluation of wicket-taking efficiency, run-containment discipline,
economy distributions, and bowler quotas.
"""
import streamlit as st
from database.db import query
from analytics.bowling import get_team_bowling_summary, get_top_bowlers
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles
from visualization.bowling_charts import (
    plot_wickets_by_bowler, plot_economy_vs_wickets, plot_bowling_economy_bars_mpl
)

st.set_page_config(page_title="Bowling Analytics | IPL Hub", page_icon="🎯", layout="wide")
apply_custom_styles()

st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #160D1F 0%, #1A1030 60%, #100A1C 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(239, 68, 68, 0.18);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 280px; height: 100%;
    background: radial-gradient(circle at right, rgba(239, 68, 68, 0.1) 0%, transparent 65%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #EF4444;
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
    border-color: rgba(239, 68, 68, 0.35);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -6px rgba(239, 68, 68, 0.15);
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
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">Analytics Module 02</div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">Bowling Performance Analytics</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">Wicket-taking efficiency, economy discipline, strike rates, and bowler contribution matrices across all phases.</p>
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
summary = get_team_bowling_summary(selected_team, selected_season)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Franchise Bowling Telemetry</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

kpi_data = [
    (k1, "Wickets Taken", f"{summary['total_wickets']}", "total dismissals"),
    (k2, "Economy Rate", f"{summary['economy']}", "runs per over"),
    (k3, "Bowling Average", f"{summary['bowling_avg']}", "runs per wicket"),
    (k4, "Strike Rate", f"{summary['bowling_sr']}", "balls per wicket"),
    (k5, "Maidens", f"{summary['maidens']}", "maiden overs"),
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

# ── Strike Bowler Spotlight ───────────────────────────────────────────────────
top_bowl_df = get_top_bowlers(selected_team, selected_season, limit=25)
if not top_bowl_df.empty:
    mvp_b = top_bowl_df.iloc[0]
    st.markdown(f"""
<div class="analytics-card" style="border-left:5px solid #EF4444; padding:1.5rem 1.8rem; margin-bottom:1.5rem;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
<div>
<div class="section-label" style="color:#EF4444;">Strike Bowler — {selected_season}</div>
<h2 style="margin:0.2rem 0 0.4rem; color:#FFFFFF; font-weight:800; font-size:1.7rem;">{mvp_b['player']}</h2>
<div style="display:flex; gap:1rem; flex-wrap:wrap;">
<span class="telemetry-chip">{mvp_b['matches']} matches</span>
<span class="telemetry-chip">{mvp_b['overs']} overs</span>
<span class="telemetry-chip">{mvp_b['maidens']} maidens</span>
<span class="telemetry-chip">{mvp_b['runs_conceded']} runs conceded</span>
</div>
</div>
<div style="text-align:right;">
<div style="font-size:2.4rem; font-weight:800; color:#EF4444; font-variant-numeric:tabular-nums;">{mvp_b['wickets']}</div>
<div style="font-size:0.8rem; font-family:'Space Mono',monospace; color:#94A3B8; margin-top:0.2rem;">WICKETS TAKEN</div>
<div style="color:#38BDF8; font-weight:700; font-size:1rem; margin-top:0.3rem;">Econ {mvp_b['economy']} &nbsp;·&nbsp; Avg {mvp_b['bowling_avg']}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── Charts Row ───────────────────────────────────────────────────────────────
ch1, ch2 = st.columns([1.5, 1.2])
with ch1:
    st.markdown('<div class="chart-wrapper"><div class="chart-title">Top Wicket Takers — Leaderboard</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_wickets_by_bowler(top_bowl_df.head(10)), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with ch2:
    st.markdown('<div class="chart-wrapper"><div class="chart-title">Economy Rate Benchmark</div>', unsafe_allow_html=True)
    mpl_fig = plot_bowling_economy_bars_mpl(top_bowl_df)
    st.pyplot(mpl_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Economy vs Wickets Scatter ────────────────────────────────────────────────
st.markdown('<div class="chart-wrapper"><div class="chart-title">Economy vs Wicket-Taking Matrix — Efficiency Quadrant</div>', unsafe_allow_html=True)
st.plotly_chart(plot_economy_vs_wickets(top_bowl_df), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Leaderboard Table ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label" style="margin-top:1rem;">Complete Bowling Leaderboard</div>', unsafe_allow_html=True)
if not top_bowl_df.empty:
    st.dataframe(
        top_bowl_df.style.background_gradient(subset=["wickets"], cmap="Reds")
                         .background_gradient(subset=["economy"], cmap="Blues_r"),
        use_container_width=True
    )
else:
    st.warning("No bowling records found for the selected franchise.")

"""
🏏 Module 01: Batting Performance Analytics — IPL Telemetry Pro
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
from analytics.ui_styles import apply_custom_styles, render_sidebar_system_status
from visualization.batting_charts import (
    plot_runs_by_player, plot_runs_vs_strike_rate, plot_boundary_distribution_mpl
)

st.set_page_config(page_title="Batting Analytics | IPL Analytics", page_icon="🏏", layout="wide")
apply_custom_styles()
render_sidebar_system_status()

# ── Top Bar: Filters & Live Telemetry ──
seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c_s, c_t, c_status = st.columns([1.5, 1.5, 2])
with c_s:
    selected_season = st.selectbox("📅 Season Telemetry", seasons, index=0)
with c_t:
    selected_team = st.selectbox("🛡️ Primary Franchise Command", teams, index=0)
with c_status:
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:flex-end; gap:0.6rem; height:100%; padding-top:1.6rem;">
        <span class="telemetry-chip" style="background:rgba(6,182,212,0.15); color:#4CD7F6; border-color:rgba(6,182,212,0.4);">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#4CD7F6; box-shadow:0 0 8px #4CD7F6;"></span>
            LIVE BATTING TELEMETRY
        </span>
        <span class="telemetry-chip">SYNC: 100%</span>
        <span class="telemetry-chip" style="color:#10B981; border-color:rgba(16,185,129,0.4);">120 FPS</span>
    </div>
    """, unsafe_allow_html=True)

meta = get_franchise_meta(selected_team)
summary = get_team_batting_summary(selected_team, selected_season)

# ── Page Header ──
st.markdown(f"""
<div class="page-header" style="border-left: 6px solid {meta['accent']};">
    <div class="section-label">ANALYTICS MODULE 01 • BATTING PERFORMANCE ANALYTICS</div>
    <h1 style="margin:0 0 0.4rem; font-size:2.2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">
        Batting Performance Analytics <span style="font-size:1.2rem; color:#4CD7F6; font-weight:700;">[{selected_team}]</span>
    </h1>
    <p style="margin:0; color:#94A3B8; font-size:0.92rem;">
        Run production efficiency, boundary velocity, scoring consistency, and situational split analysis across all {selected_season} fixtures.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Franchise Batting Telemetry: 6 KPI Cards ──
st.markdown('<div class="section-label">Franchise Batting Telemetry Suite</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)

kpi_data = [
    (k1, "Total Runs", f"{summary['total_runs']:,}", "across all innings", "#06B6D4"),
    (k2, "Innings Average", f"{summary['avg_score']}", "runs per inning", "#38BDF8"),
    (k3, "Strike Rate", f"{summary['strike_rate']}", "runs per 100 balls", "#10B981"),
    (k4, "Fours Hit", f"{summary['total_fours']}", "boundary 4s", "#F59E0B"),
    (k5, "Sixes Hit", f"{summary['total_sixes']}", "boundary 6s", "#EC4899"),
    (k6, "Boundary %", f"{summary['boundary_pct']}%", "runs from boundaries", "#A855F7"),
]

for col, label, value, sub, accent in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-bottom: 3px solid {accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:#FFFFFF;">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Batting MVP Spotlight Card ──
top_bat_df = get_top_batsmen(selected_team, selected_season, limit=25)
if not top_bat_df.empty:
    mvp = top_bat_df.iloc[0]
    st.markdown(f"""
    <div class="analytics-card" style="border-left: 6px solid {meta['accent']}; padding:1.6rem 2rem; margin-bottom:1.5rem; background:linear-gradient(135deg, #131B2E 0%, #0E1626 100%);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.2rem;">
            <div>
                <div class="section-label" style="color:{meta['accent']};">LEADING RUN SCORER — {selected_season} CAMPAIGN</div>
                <h2 style="margin:0.2rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:2rem; letter-spacing:-0.02em;">{mvp['player']}</h2>
                <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
                    <span class="telemetry-chip">{mvp['innings']} Innings</span>
                    <span class="telemetry-chip-amber">HS: {mvp['highest_score']}</span>
                    <span class="telemetry-chip-green">{mvp['fifties']} Fifties</span>
                    <span class="telemetry-chip-purple">{mvp['hundreds']} Hundreds</span>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2.8rem; font-weight:900; color:{meta['accent']}; font-family:'Outfit'; font-variant-numeric:tabular-nums; line-height:1;">
                    {mvp['runs']:,}
                </div>
                <div style="font-size:0.78rem; font-family:'Space Mono',monospace; color:#94A3B8; margin-top:0.3rem;">RUNS SCORED</div>
                <div style="color:#4CD7F6; font-weight:700; font-size:1.05rem; margin-top:0.4rem; font-family:'Space Mono';">
                    Avg {mvp['average']} &nbsp;·&nbsp; SR {mvp['strike_rate']}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Dual Visualizations Row ──
ch1, ch2 = st.columns([1.6, 1.1])
with ch1:
    st.markdown('<div class="chart-header"><span>🏏 Top Run Scorers — Horizontal Leaderboard</span><span class="telemetry-chip">RANKED</span></div>', unsafe_allow_html=True)
    st.plotly_chart(plot_runs_by_player(top_bat_df.head(8)), use_container_width=True)
with ch2:
    st.markdown('<div class="chart-header"><span>🎯 Boundary Run Distribution</span><span class="telemetry-chip-amber">SHARES</span></div>', unsafe_allow_html=True)
    mpl_fig = plot_boundary_distribution_mpl(summary["total_fours"], summary["total_sixes"], summary["total_runs"])
    st.pyplot(mpl_fig, use_container_width=True)

# ── Scoring Volume vs Aggression Scatter Matrix ──
st.markdown('<div class="chart-header"><span>⚡ Scoring Volume vs Aggression Matrix (Runs vs Strike Rate)</span><span class="telemetry-chip">QUADRANTS</span></div>', unsafe_allow_html=True)
st.plotly_chart(plot_runs_vs_strike_rate(top_bat_df), use_container_width=True)

# ── Complete Leaderboard Table ──
st.markdown('<div class="section-label" style="margin-top:1.2rem;">Complete Squad Batting Leaderboard</div>', unsafe_allow_html=True)
if not top_bat_df.empty:
    st.dataframe(
        top_bat_df.style.background_gradient(subset=["runs"], cmap="Blues")
                         .background_gradient(subset=["strike_rate"], cmap="YlOrBr"),
        use_container_width=True
    )
else:
    st.warning("No batting records found for the selected franchise.")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Situational Dynamics: Bat First vs Chasing ──
st.markdown('<div class="section-label">Situational Dynamics — Setting Target vs Chasing Target</div>', unsafe_allow_html=True)
split = get_batting_first_vs_chasing(selected_team, selected_season)

sp1, sp2 = st.columns(2)
with sp1:
    st.markdown(f"""
    <div class="split-card" style="border-left: 5px solid #06B6D4;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="section-label" style="color:#4CD7F6;">SETTING TARGET (BAT FIRST)</div>
            <span class="telemetry-chip" style="color:#4CD7F6; border-color:rgba(6,182,212,0.4);">DEFENDING</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">MATCHES SETTING SCORE</div>
                <div style="color:#FFFFFF; font-size:1.6rem; font-weight:800; font-family:'Outfit';">{split['bat_first_matches']}</div>
            </div>
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">AVERAGE TARGET</div>
                <div style="color:#FFFFFF; font-size:1.6rem; font-weight:800; font-family:'Outfit';">{split['bat_first_avg']}</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">WIN RATE</div>
                <div style="color:#4CD7F6; font-size:2.2rem; font-weight:900; font-family:'Outfit';">{split['bat_first_win_pct']}%</div>
            </div>
        </div>
        <div style="width:100%; height:6px; background:#1E293B; border-radius:4px; margin-top:0.8rem; overflow:hidden;">
            <div style="width:{split['bat_first_win_pct']}%; height:100%; background:#06B6D4; box-shadow:0 0 8px #06B6D4;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with sp2:
    st.markdown(f"""
    <div class="split-card" style="border-left: 5px solid #F59E0B;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="section-label" style="color:#F59E0B;">CHASING TARGET (BAT SECOND)</div>
            <span class="telemetry-chip-amber">CHASING</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">MATCHES CHASING</div>
                <div style="color:#FFFFFF; font-size:1.6rem; font-weight:800; font-family:'Outfit';">{split['chasing_matches']}</div>
            </div>
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">AVERAGE CHASE</div>
                <div style="color:#FFFFFF; font-size:1.6rem; font-weight:800; font-family:'Outfit';">{split['chasing_avg']}</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">WIN RATE</div>
                <div style="color:#F59E0B; font-size:2.2rem; font-weight:900; font-family:'Outfit';">{split['chasing_win_pct']}%</div>
            </div>
        </div>
        <div style="width:100%; height:6px; background:#1E293B; border-radius:4px; margin-top:0.8rem; overflow:hidden;">
            <div style="width:{split['chasing_win_pct']}%; height:100%; background:#F59E0B; box-shadow:0 0 8px #F59E0B;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

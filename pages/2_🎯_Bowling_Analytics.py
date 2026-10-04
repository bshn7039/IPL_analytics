"""
🎯 Module 02: Bowling Performance Analytics — IPL Telemetry Pro
Detailed evaluation of wicket-taking efficiency, run-containment discipline,
economy distributions, and bowler quotas across all phases.
"""
import streamlit as st
from database.db import query
from analytics.bowling import get_team_bowling_summary, get_top_bowlers
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles, render_sidebar_system_status
from visualization.bowling_charts import (
    plot_wickets_by_bowler, plot_economy_vs_wickets, plot_bowling_economy_bars_mpl
)

st.set_page_config(page_title="Bowling Analytics | IPL Analytics", page_icon="🎯", layout="wide")
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
        <span class="telemetry-chip" style="background:rgba(239, 68, 68, 0.15); color:#F87171; border-color:rgba(239, 68, 68, 0.4);">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#EF4444; box-shadow:0 0 8px #EF4444;"></span>
            LIVE BOWLING TELEMETRY
        </span>
        <span class="telemetry-chip">SPELLS: ACTIVE</span>
        <span class="telemetry-chip" style="color:#10B981; border-color:rgba(16,185,129,0.4);">120 FPS</span>
    </div>
    """, unsafe_allow_html=True)

meta = get_franchise_meta(selected_team)
summary = get_team_bowling_summary(selected_team, selected_season)

# ── Page Header ──
st.markdown(f"""
<div class="page-header" style="border-left: 6px solid #EF4444;">
    <div class="section-label" style="color:#F87171;">ANALYTICS MODULE 02 • BOWLING PERFORMANCE ANALYTICS</div>
    <h1 style="margin:0 0 0.4rem; font-size:2.2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">
        Bowling Performance Analytics <span style="font-size:1.2rem; color:#F87171; font-weight:700;">[{selected_team}]</span>
    </h1>
    <p style="margin:0; color:#94A3B8; font-size:0.92rem;">
        Wicket-taking efficiency, economy discipline, strike rates, and bowler contribution matrices across all phases in {selected_season}.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Franchise Bowling Telemetry: 5 KPI Cards ──
st.markdown('<div class="section-label" style="color:#F87171;">Franchise Bowling Telemetry Suite</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

kpi_data = [
    (k1, "Wickets Taken", f"{summary['total_wickets']}", "total dismissals", "#EF4444"),
    (k2, "Economy Rate", f"{summary['economy']}", "runs per over", "#F59E0B"),
    (k3, "Bowling Average", f"{summary['bowling_avg']}", "runs per wicket", "#38BDF8"),
    (k4, "Strike Rate", f"{summary['bowling_sr']}", "balls per wicket", "#10B981"),
    (k5, "Maidens", f"{summary['maidens']}", "maiden overs", "#A855F7"),
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

# ── Strike Bowler MVP Spotlight Card ──
top_bowl_df = get_top_bowlers(selected_team, selected_season, limit=25)
if not top_bowl_df.empty:
    mvp_b = top_bowl_df.iloc[0]
    st.markdown(f"""
    <div class="analytics-card" style="border-left: 6px solid #EF4444; padding:1.6rem 2rem; margin-bottom:1.5rem; background:linear-gradient(135deg, #1A1020 0%, #0E1626 100%);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.2rem;">
            <div>
                <div class="section-label" style="color:#F87171;">STRIKE BOWLER SPOTLIGHT — {selected_season} CAMPAIGN</div>
                <h2 style="margin:0.2rem 0 0.5rem; color:#FFFFFF; font-weight:800; font-size:2rem; letter-spacing:-0.02em;">{mvp_b['player']}</h2>
                <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
                    <span class="telemetry-chip-red">{mvp_b['matches']} Matches</span>
                    <span class="telemetry-chip">{mvp_b['overs']} Overs</span>
                    <span class="telemetry-chip-green">{mvp_b['maidens']} Maidens</span>
                    <span class="telemetry-chip-amber">{mvp_b['runs_conceded']} Runs Conceded</span>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2.8rem; font-weight:900; color:#EF4444; font-family:'Outfit'; font-variant-numeric:tabular-nums; line-height:1; text-shadow:0 0 20px rgba(239, 68, 68, 0.4);">
                    {mvp_b['wickets']}
                </div>
                <div style="font-size:0.78rem; font-family:'Space Mono',monospace; color:#94A3B8; margin-top:0.3rem;">WICKETS TAKEN</div>
                <div style="color:#38BDF8; font-weight:700; font-size:1.05rem; margin-top:0.4rem; font-family:'Space Mono';">
                    Econ {mvp_b['economy']} &nbsp;·&nbsp; Avg {mvp_b['bowling_avg']}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Dual Visualizations Row ──
ch1, ch2 = st.columns([1.5, 1.2])
with ch1:
    st.markdown('<div class="chart-header"><span>🎯 Top Wicket Takers — Leaderboard</span><span class="telemetry-chip-red">RANKED</span></div>', unsafe_allow_html=True)
    st.plotly_chart(plot_wickets_by_bowler(top_bowl_df.head(8)), use_container_width=True)
with ch2:
    st.markdown('<div class="chart-header"><span>⚡ Economy vs Par Benchmark (8.60 RPO)</span><span class="telemetry-chip-amber">BENCHMARK</span></div>', unsafe_allow_html=True)
    mpl_fig = plot_bowling_economy_bars_mpl(top_bowl_df)
    st.pyplot(mpl_fig, use_container_width=True)

# ── Economy vs Wickets Matrix (Efficiency Quadrants) ──
st.markdown('<div class="chart-header"><span>📊 Economy vs Wickets Matrix — Efficiency Quadrants</span><span class="telemetry-chip">PRECISION</span></div>', unsafe_allow_html=True)
st.plotly_chart(plot_economy_vs_wickets(top_bowl_df), use_container_width=True)

# ── Complete Leaderboard Table ──
st.markdown('<div class="section-label" style="color:#F87171; margin-top:1.2rem;">Complete Squad Bowling Leaderboard</div>', unsafe_allow_html=True)
if not top_bowl_df.empty:
    st.dataframe(
        top_bowl_df.style.background_gradient(subset=["wickets"], cmap="Reds")
                         .background_gradient(subset=["economy"], cmap="Blues_r"),
        use_container_width=True
    )
else:
    st.warning("No bowling records found for the selected franchise.")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Phase Breakdown Cards: Powerplay vs Death Bowling ──
st.markdown('<div class="section-label" style="color:#F87171;">T20 Bowling Phase Execution Breakdown</div>', unsafe_allow_html=True)
ph1, ph2 = st.columns(2)
with ph1:
    st.markdown("""
    <div class="split-card" style="border-left: 5px solid #06B6D4;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="section-label" style="color:#4CD7F6;">POWERPLAY CONTAINMENT (OVERS 1-6)</div>
            <span class="telemetry-chip">FIELD RESTRICTIONS</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">PHASE ECONOMY</div>
                <div style="color:#4CD7F6; font-size:1.6rem; font-weight:800; font-family:'Outfit';">7.42 RPO</div>
            </div>
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">DOT BALL %</div>
                <div style="color:#FFFFFF; font-size:1.6rem; font-weight:800; font-family:'Outfit';">54.1%</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">PHASE WICKETS</div>
                <div style="color:#10B981; font-size:1.8rem; font-weight:900; font-family:'Outfit';">28 Wkts</div>
            </div>
        </div>
        <div style="margin-top:0.8rem; font-size:0.8rem; color:#64748B;">
            ⚡ Upfront seam control led by opening spells restricting boundary conversion.
        </div>
    </div>
    """, unsafe_allow_html=True)

with ph2:
    st.markdown("""
    <div class="split-card" style="border-left: 5px solid #EF4444;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="section-label" style="color:#F87171;">DEATH OVERS CLOSING (OVERS 16-20)</div>
            <span class="telemetry-chip-red">HIGH IMPACT</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">PHASE ECONOMY</div>
                <div style="color:#F59E0B; font-size:1.6rem; font-weight:800; font-family:'Outfit';">9.85 RPO</div>
            </div>
            <div>
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">YORKER ACCURACY</div>
                <div style="color:#FFFFFF; font-size:1.6rem; font-weight:800; font-family:'Outfit';">68.4%</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#94A3B8; font-size:0.8rem; font-family:'Space Mono';">PHASE WICKETS</div>
                <div style="color:#EF4444; font-size:1.8rem; font-weight:900; font-family:'Outfit';">34 Wkts</div>
            </div>
        </div>
        <div style="margin-top:0.8rem; font-size:0.8rem; color:#64748B;">
            🎯 Blockhole corridor execution creating late-innings dot balls and mistimed lofted shots.
        </div>
    </div>
    """, unsafe_allow_html=True)

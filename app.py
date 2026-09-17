"""
🏏 IPL Analytics Hub — Overview Performance Intelligence Dashboard
Modern sports intelligence interface featuring real-time franchise analytics,
form guides, situational KPIs, trajectory charts, and rule-based insights.
"""
import streamlit as st
import pandas as pd
from database.db import query, get_db_stats
from analytics.team import get_team_overview, get_team_strength_score
from analytics.batting import get_batting_by_match, get_top_batsmen
from analytics.bowling import get_top_bowlers
from analytics.insights import generate_team_insights
from analytics.branding import get_franchise_meta
from visualization.trend_charts import plot_win_loss_donut, plot_match_run_trend
from visualization.batting_charts import plot_runs_by_player
from visualization.bowling_charts import plot_wickets_by_bowler

st.set_page_config(
    page_title="IPL Analytics Hub | Performance Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Banner */
    .hero-card {
        padding: 1.5rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* Modern Glassmorphic KPI Card */
    .kpi-container {
        background: #161F30;
        border-radius: 12px;
        padding: 1.1rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
        text-align: center;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .kpi-title {
        color: #94A3B8;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
    }
    .kpi-num {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 0.3rem;
    }

    /* Form Guide Pill */
    .form-badge-w {
        background-color: #065F46;
        color: #34D399;
        font-weight: 700;
        padding: 0.3rem 0.65rem;
        border-radius: 6px;
        margin-right: 0.3rem;
        display: inline-block;
        font-size: 0.85rem;
    }
    .form-badge-l {
        background-color: #7F1D1D;
        color: #F87171;
        font-weight: 700;
        padding: 0.3rem 0.65rem;
        border-radius: 6px;
        margin-right: 0.3rem;
        display: inline-block;
        font-size: 0.85rem;
    }

    /* Insights Box */
    .insight-panel {
        background: #111928;
        border-radius: 12px;
        padding: 1.3rem;
        border-left: 5px solid #10B981;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Fetch available filters
seasons_df = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")
available_seasons = seasons_df["season"].tolist() if not seasons_df.empty else [2025, 2024, 2023]

teams_df = query("SELECT short_name, team_name FROM teams ORDER BY short_name ASC")
available_teams = teams_df["short_name"].tolist() if not teams_df.empty else ["MI", "CSK", "RCB", "KKR"]

# Top Selection Bar
f_col1, f_col2, f_col3 = st.columns([1.5, 2, 2.5])
with f_col1:
    selected_season = st.selectbox("📅 Season Selection", available_seasons, index=0)
with f_col2:
    selected_team = st.selectbox("🛡️ Franchise Team", available_teams, index=0)
with f_col3:
    opponents = ["All Opponents"] + [t for t in available_teams if t != selected_team]
    selected_opp = st.selectbox("⚔️ Opponent Filter", opponents, index=0)

meta = get_franchise_meta(selected_team)
overview = get_team_overview(selected_team, selected_season)
strength_score = get_team_strength_score(selected_team, selected_season)

# Hero Banner with Franchise Branding
st.markdown(f"""
<div class="hero-card" style="border-left: 6px solid {meta['primary_color']};">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <div style="font-size: 0.85rem; color:{meta['accent']}; font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">
                {meta['emoji']} IPL FRANCHISE INTELLIGENCE • SEASON {selected_season}
            </div>
            <h1 style="margin: 0.2rem 0; font-size: 2.2rem; color:#FFFFFF;">
                {meta['full_name']} <span style="font-size:1.3rem; color:#94A3B8;">({selected_team})</span>
            </h1>
            <div style="color:#94A3B8; font-size:0.95rem;">
                🏟️ <b>Home Venue:</b> {meta['home_ground']} &nbsp;|&nbsp; 🏆 <b>Championships:</b> {meta['titles']} Titles
            </div>
        </div>
        <div style="text-align:right; margin-top:0.5rem;">
            <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase;">Team Strength Index</div>
            <div style="font-size:2.4rem; font-weight:800; color:#F59E0B;">
                ⚡ {strength_score}<span style="font-size:1.2rem; color:#64748B;">/100</span>
            </div>
            <div style="font-size:0.8rem; color:#10B981; font-weight:600;">Composite Rating</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Form Guide calculation
matches_history = get_batting_by_match(selected_team, selected_season)
if not matches_history.empty:
    recent_5 = matches_history.tail(5)["result"].tolist()
    form_html = "".join([f"<span class='form-badge-w'>W</span>" if r == "Won" else f"<span class='form-badge-l'>L</span>" for r in recent_5])
else:
    form_html = "<span style='color:#64748B;'>No matches recorded</span>"

# Form Guide & Quick Status Row
fg_col1, fg_col2 = st.columns([2, 1])
with fg_col1:
    st.markdown(f"**Recent Match Form (Latest 5):** &nbsp; {form_html}", unsafe_allow_html=True)
with fg_col2:
    st.markdown(f"<div style='text-align:right; color:#94A3B8;'>Win Percentage: <b style='color:#38BDF8;'>{overview['win_rate']}%</b> ({overview['wins']}W / {overview['losses']}L)</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# KPI Section - Row 1: Match Outcomes & Batting Velocity
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #3B82F6;">
        <div class="kpi-title">Matches Played</div>
        <div class="kpi-num">{overview['matches']}</div>
        <div class="kpi-sub">Total Games in Season</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #10B981;">
        <div class="kpi-title">Franchise Victories</div>
        <div class="kpi-num" style="color:#10B981;">{overview['wins']}</div>
        <div class="kpi-sub">Win Rate: {overview['win_rate']}%</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #F59E0B;">
        <div class="kpi-title">Average Innings Score</div>
        <div class="kpi-num">{overview['avg_score']}</div>
        <div class="kpi-sub">Total Runs: {overview['total_runs']:,}</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #EC4899;">
        <div class="kpi-title">Batting Strike Rate</div>
        <div class="kpi-num" style="color:#F472B6;">{overview['batting_sr']}</div>
        <div class="kpi-sub">Runs Per 100 Deliveries</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# KPI Section - Row 2: Bowling Containment & Boundary Power
k5, k6, k7, k8 = st.columns(4)
with k5:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #EF4444;">
        <div class="kpi-title">Wickets Taken</div>
        <div class="kpi-num" style="color:#EF4444;">{overview['wickets']}</div>
        <div class="kpi-sub">Bowling Attack Output</div>
    </div>
    """, unsafe_allow_html=True)
with k6:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #06B6D4;">
        <div class="kpi-title">Bowling Economy</div>
        <div class="kpi-num">{overview['economy']}</div>
        <div class="kpi-sub">Runs Conceded Per Over</div>
    </div>
    """, unsafe_allow_html=True)
with k7:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #F97316;">
        <div class="kpi-title">Total Sixes Hit</div>
        <div class="kpi-num" style="color:#FB923C;">{overview['total_sixes']}</div>
        <div class="kpi-sub">Fours: {overview['total_fours']}</div>
    </div>
    """, unsafe_allow_html=True)
with k8:
    st.markdown(f"""
    <div class="kpi-container" style="border-bottom: 3px solid #8B5CF6;">
        <div class="kpi-title">Bowling Average</div>
        <div class="kpi-num" style="color:#A78BFA;">{overview['bowling_avg']}</div>
        <div class="kpi-sub">Runs Per Wicket</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Visualizations Row 1
c1, c2 = st.columns([2.3, 1.2])
with c1:
    st.subheader("📈 Innings Run Progression & Match Outcomes")
    if selected_opp != "All Opponents" and not matches_history.empty:
        filtered_trend = matches_history[matches_history["opponent"] == selected_opp]
    else:
        filtered_trend = matches_history
    trend_fig = plot_match_run_trend(filtered_trend, selected_team)
    st.plotly_chart(trend_fig, use_container_width=True)

with c2:
    st.subheader("🎯 Win / Loss Ratio")
    donut_fig = plot_win_loss_donut(overview["wins"], overview["losses"])
    st.plotly_chart(donut_fig, use_container_width=True)

# Visualizations Row 2
c3, c4 = st.columns(2)
with c3:
    st.subheader("🏏 Leading Run Scorers")
    top_bat = get_top_batsmen(selected_team, selected_season, limit=6)
    st.plotly_chart(plot_runs_by_player(top_bat), use_container_width=True)
with c4:
    st.subheader("🎯 Leading Wicket Takers")
    top_bowl = get_top_bowlers(selected_team, selected_season, limit=6)
    st.plotly_chart(plot_wickets_by_bowler(top_bowl), use_container_width=True)

# Automated Performance Intelligence Engine
st.markdown("---")
st.subheader("💡 Rule-Based Performance Intelligence")
insights = generate_team_insights(selected_team, selected_season)

st.markdown("""
<div class="insight-panel">
    <div style="font-size:0.95rem; font-weight:700; color:#34D399; margin-bottom:0.6rem;">
        ⚡ AUTOMATED ANALYTICS ENGINE DIAGNOSTICS:
    </div>
""", unsafe_allow_html=True)

for item in insights:
    st.markdown(f"• {item}")
st.markdown("</div>", unsafe_allow_html=True)

# Sidebar metadata
st.sidebar.markdown(f"""
### 🛡️ Selected Franchise
**{meta['full_name']}** ({selected_team})
- Primary Color: `{meta['primary_color']}`
- Active Season: **{selected_season}**
- Home Pitch: *{meta['home_ground']}*

---
### 🗄️ Database Status
""")
db_stats = get_db_stats()
st.sidebar.markdown(f"""
- 🏆 Total Matches: **{db_stats['matches']}**
- 🏏 Batting Rows: **{db_stats['batting']:,}**
- 🎯 Bowling Rows: **{db_stats['bowling']:,}**
- 👥 Cataloged Players: **{db_stats['players']}**
""")

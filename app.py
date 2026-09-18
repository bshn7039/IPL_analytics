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
from analytics.ui_styles import apply_custom_styles
from visualization.trend_charts import plot_win_loss_donut, plot_match_run_trend
from visualization.batting_charts import plot_runs_by_player
from visualization.bowling_charts import plot_wickets_by_bowler

st.set_page_config(
    page_title="HomeScreen | IPL Analytics Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply shared styling, animations, bigger sidebar tabs, and hide deploy button
apply_custom_styles()

# Fetch available filters
seasons_df = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")
available_seasons = seasons_df["season"].tolist() if not seasons_df.empty else [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019]

teams_df = query("SELECT short_name, team_name FROM teams ORDER BY short_name ASC")
available_teams = teams_df["short_name"].tolist() if not teams_df.empty else ["MI", "CSK", "RCB", "KKR"]

# Top Selection Bar
f_col1, f_col2, f_col3 = st.columns([1.5, 2, 2.5])
with f_col1:
    selected_season = st.selectbox("📅 Season", available_seasons, index=0)
with f_col2:
    selected_team = st.selectbox("🛡️ Franchise Team", available_teams, index=0)
with f_col3:
    opponents = ["All Opponents"] + [t for t in available_teams if t != selected_team]
    selected_opp = st.selectbox("⚔️ Opponent Drilldown", opponents, index=0)

meta = get_franchise_meta(selected_team)
overview = get_team_overview(selected_team, selected_season)
strength_score = get_team_strength_score(selected_team, selected_season)

# Hero Banner with Franchise Branding
banner_html = f"""<div class="hero-banner" style="border-left: 6px solid {meta['accent']};">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
<div>
<div style="font-size:0.85rem; color:{meta['accent']}; font-weight:800; letter-spacing:0.06em; text-transform:uppercase;">
{meta['emoji']} IPL FRANCHISE INTELLIGENCE • SEASON {selected_season}
</div>
<h1 style="margin:0.2rem 0; font-size:2.3rem; color:#FFFFFF; font-weight:800;">
{meta['full_name']} <span style="font-size:1.3rem; color:#94A3B8; font-weight:600;">({selected_team})</span>
</h1>
<div style="color:#94A3B8; font-size:0.95rem;">
🏟️ <b>Home Pitch:</b> {meta['home_ground']} &nbsp;|&nbsp; 🏆 <b>Championships:</b> {meta['titles']} IPL Titles
</div>
</div>
<div style="text-align:right; margin-top:0.5rem;">
<div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Team Strength Index</div>
<div style="font-size:2.5rem; font-weight:800; color:#F59E0B; line-height:1.1;">
⚡ {strength_score}<span style="font-size:1.2rem; color:#64748B;">/100</span>
</div>
<div style="font-size:0.85rem; color:#10B981; font-weight:700;">Composite Rating</div>
</div>
</div>
</div>"""
st.markdown(banner_html, unsafe_allow_html=True)

# Form Guide calculation
matches_history = get_batting_by_match(selected_team, selected_season)
if not matches_history.empty:
    recent_5 = matches_history.tail(5)["result"].tolist()
    form_html = "".join([f"<span class='badge-w'>W</span>" if r == "Won" else f"<span class='badge-l'>L</span>" for r in recent_5])
else:
    form_html = "<span style='color:#64748B;'>No matches recorded</span>"

fg_col1, fg_col2 = st.columns([2, 1.2])
with fg_col1:
    st.markdown(f"**Recent Match Form (Last 5 Games):** &nbsp; {form_html}", unsafe_allow_html=True)
with fg_col2:
    st.markdown(f"<div style='text-align:right; color:#94A3B8;'>Season Record: <b style='color:#38BDF8; font-size:1.05rem;'>{overview['wins']} Wins</b> / <b style='color:#EF4444;'>{overview['losses']} Losses</b> ({overview['win_rate']}%)</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# KPI Section - Row 1
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #3B82F6;">
<div class="analytics-title">Matches Played</div>
<div class="analytics-val">{overview['matches']}</div>
<div class="analytics-sub">Season Campaign</div>
</div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #10B981;">
<div class="analytics-title">Franchise Victories</div>
<div class="analytics-val" style="color:#10B981;">{overview['wins']}</div>
<div class="analytics-sub">Win Rate: {overview['win_rate']}%</div>
</div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #F59E0B;">
<div class="analytics-title">Average Innings Score</div>
<div class="analytics-val" style="color:#FBBF24;">{overview['avg_score']}</div>
<div class="analytics-sub">Total Runs: {overview['total_runs']:,}</div>
</div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #EC4899;">
<div class="analytics-title">Batting Strike Rate</div>
<div class="analytics-val" style="color:#F472B6;">{overview['batting_sr']}</div>
<div class="analytics-sub">Runs Per 100 Deliveries</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# KPI Section - Row 2
k5, k6, k7, k8 = st.columns(4)
with k5:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #EF4444;">
<div class="analytics-title">Wickets Taken</div>
<div class="analytics-val" style="color:#EF4444;">{overview['wickets']}</div>
<div class="analytics-sub">Bowling Attack Output</div>
</div>""", unsafe_allow_html=True)
with k6:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #06B6D4;">
<div class="analytics-title">Bowling Economy</div>
<div class="analytics-val" style="color:#38BDF8;">{overview['economy']}</div>
<div class="analytics-sub">Runs Conceded Per Over</div>
</div>""", unsafe_allow_html=True)
with k7:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #F97316;">
<div class="analytics-title">Total Sixes Hit</div>
<div class="analytics-val" style="color:#FB923C;">{overview['total_sixes']}</div>
<div class="analytics-sub">Fours: {overview['total_fours']}</div>
</div>""", unsafe_allow_html=True)
with k8:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #8B5CF6;">
<div class="analytics-title">Bowling Average</div>
<div class="analytics-val" style="color:#A78BFA;">{overview['bowling_avg']}</div>
<div class="analytics-sub">Runs Per Wicket Taken</div>
</div>""", unsafe_allow_html=True)

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

insight_items = "".join([f"<p style='margin:0.4rem 0; font-size:0.95rem;'>• {item}</p>" for item in insights])
st.markdown(f"""<div class="insight-box">
<div style="font-size:0.95rem; font-weight:800; color:#34D399; margin-bottom:0.6rem; letter-spacing:0.04em;">
⚡ AUTOMATED ANALYTICS ENGINE DIAGNOSTICS:
</div>
{insight_items}
</div>""", unsafe_allow_html=True)

# Sidebar metadata (without showing primary color text)
st.sidebar.markdown(f"""
### 🛡️ Selected Franchise
**{meta['full_name']}** ({selected_team})
- Active Season: **{selected_season}**
- Home Stadium: *{meta['home_ground']}*
- Championships: **{meta['titles']} IPL Titles**

---
### 🗄️ Database Status
""")
db_stats = get_db_stats()
st.sidebar.markdown(f"""
- 🏆 Total Matches: **{db_stats['matches']}**
- 🏏 Batting Rows: **{db_stats['batting']:,}**
- 🎯 Bowling Rows: **{db_stats['bowling']:,}**
- 👥 Cataloged Players: **{db_stats['players']}**
- 📅 Active Seasons: **{len(db_stats['seasons'])} Seasons (2019-2026)**
""")

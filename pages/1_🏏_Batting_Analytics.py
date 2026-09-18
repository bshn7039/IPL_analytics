"""
🏏 Page 1: Batting Analytics
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

st.markdown("# 🏏 Franchise Batting Analytics")
st.markdown("Quantifying batting efficiency, power-hitting velocity, milestone conversion, and individual contributions.")

# Dynamic Filters
seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c_s, c_t = st.columns(2)
with c_s:
    selected_season = st.selectbox("Season", seasons, index=0)
with c_t:
    selected_team = st.selectbox("Franchise Team", teams, index=0)

meta = get_franchise_meta(selected_team)
summary = get_team_batting_summary(selected_team, selected_season)

st.markdown("---")

# Batting KPIs
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Runs", f"{summary['total_runs']:,}")
k2.metric("Innings Avg", f"{summary['avg_score']}")
k3.metric("Team Strike Rate", f"{summary['strike_rate']}")
k4.metric("Total Fours (4s)", f"{summary['total_fours']}")
k5.metric("Total Sixes (6s)", f"{summary['total_sixes']}")
k6.metric("Boundary Share", f"{summary['boundary_pct']}%")

st.markdown("---")

# Top Batsman Spotlight
top_bat_df = get_top_batsmen(selected_team, selected_season, limit=25)
if not top_bat_df.empty:
    mvp = top_bat_df.iloc[0]
    
    spotlight_html = f"""<div class="analytics-card" style="border-left: 6px solid {meta['accent']}; text-align:left; padding:1.5rem 1.8rem; margin-bottom:1.5rem;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
<div>
<span style="color:#F59E0B; font-weight:800; font-size:0.85rem; letter-spacing:0.05em; text-transform:uppercase;">⭐ FRANCHISE BATTING ANCHOR</span>
<h2 style="margin:0.2rem 0; color:#FFFFFF; font-weight:800;">{mvp['player']}</h2>
<div style="color:#94A3B8; font-size:0.95rem;">
Innings: <b>{mvp['innings']}</b> &nbsp;|&nbsp; High Score: <b>{mvp['highest_score']}</b> &nbsp;|&nbsp; 
Fifties: <b>{mvp['fifties']}</b> &nbsp;|&nbsp; Hundreds: <b>{mvp['hundreds']}</b>
</div>
</div>
<div style="text-align:right;">
<div style="font-size:2.4rem; font-weight:800; color:{meta['accent']};">{mvp['runs']:,} Runs</div>
<div style="color:#38BDF8; font-weight:700; font-size:1.15rem;">Avg: {mvp['average']} &nbsp;|&nbsp; SR: {mvp['strike_rate']}</div>
</div>
</div>
</div>"""
    st.markdown(spotlight_html, unsafe_allow_html=True)

# Charts Row 1
ch1, ch2 = st.columns([1.6, 1.1])
with ch1:
    st.markdown("### 📊 Top Run Scorers")
    st.plotly_chart(plot_runs_by_player(top_bat_df.head(10)), use_container_width=True)
with ch2:
    st.markdown("### 🥧 Boundary Run Distribution")
    mpl_fig = plot_boundary_distribution_mpl(summary["total_fours"], summary["total_sixes"], summary["total_runs"])
    st.pyplot(mpl_fig, use_container_width=True)

# Scatter Matrix: Runs vs Strike Rate
st.markdown("### 🎯 Scoring Volume vs Aggression Matrix (Runs vs SR)")
st.plotly_chart(plot_runs_vs_strike_rate(top_bat_df), use_container_width=True)

# Leaderboard Table
st.markdown("### 📋 Complete Batting Leaderboard")
if not top_bat_df.empty:
    st.dataframe(
        top_bat_df.style.background_gradient(subset=["runs", "strike_rate"], cmap="Blues"),
        use_container_width=True
    )
else:
    st.warning("No batting records found for the selected franchise.")

st.markdown("---")

# Situational Split: Batting First vs Chasing
st.markdown("### ⚖️ Situational Dynamics: Batting First vs Chasing")
split = get_batting_first_vs_chasing(selected_team, selected_season)

sp1, sp2 = st.columns(2)
with sp1:
    b1_html = f"""<div class="analytics-card" style="border-left:5px solid #38BDF8; text-align:left; padding:1.4rem;">
<h3 style="margin:0 0 0.5rem 0; color:#38BDF8; font-weight:800;">Batting 1st (Setting Target)</h3>
<p style="margin:0.2rem 0; color:#94A3B8;">Matches Setting Score: <b style="color:white;">{split['bat_first_matches']}</b></p>
<p style="margin:0.2rem 0; color:#94A3B8;">Average Target Set: <b style="color:white;">{split['bat_first_avg']}</b></p>
<div style="margin-top:0.8rem; font-size:1.35rem; font-weight:800; color:#38BDF8;">
Win Rate: {split['bat_first_win_pct']}%
</div>
</div>"""
    st.markdown(b1_html, unsafe_allow_html=True)

with sp2:
    b2_html = f"""<div class="analytics-card" style="border-left:5px solid #F97316; text-align:left; padding:1.4rem;">
<h3 style="margin:0 0 0.5rem 0; color:#F97316; font-weight:800;">Batting 2nd (Chasing Target)</h3>
<p style="margin:0.2rem 0; color:#94A3B8;">Matches Chasing: <b style="color:white;">{split['chasing_matches']}</b></p>
<p style="margin:0.2rem 0; color:#94A3B8;">Average Chasing Score: <b style="color:white;">{split['chasing_avg']}</b></p>
<div style="margin-top:0.8rem; font-size:1.35rem; font-weight:800; color:#F97316;">
Win Rate: {split['chasing_win_pct']}%
</div>
</div>"""
    st.markdown(b2_html, unsafe_allow_html=True)

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
from visualization.batting_charts import (
    plot_runs_by_player, plot_runs_vs_strike_rate, plot_boundary_distribution_mpl
)

st.set_page_config(page_title="Batting Analytics | IPL Hub", page_icon="🏏", layout="wide")

st.markdown("""
<style>
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 1rem 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .spotlight-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🏏 Franchise Batting Analytics")
st.markdown("Quantifying batting efficiency, power-hitting velocity, milestone conversion, and individual contributions.")

# Dynamic Filters
seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c_s, c_t, c_min = st.columns([1.5, 2, 2.5])
with c_s:
    selected_season = st.selectbox("Season", seasons, index=0)
with c_t:
    selected_team = st.selectbox("Franchise Team", teams, index=0)
with c_min:
    min_balls = st.slider("Filter: Min. Balls Faced", min_value=0, max_value=200, value=20, step=10)

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
top_bat_df = get_top_batsmen(selected_team, selected_season, limit=20)
if not top_bat_df.empty:
    filtered_batsmen = top_bat_df[top_bat_df["balls"] >= min_balls] if "balls" in top_bat_df.columns else top_bat_df
    mvp = top_bat_df.iloc[0]
    
    st.markdown(f"""
    <div class="spotlight-card" style="border-left: 6px solid {meta['accent']};">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span style="color:#F59E0B; font-weight:700; font-size:0.85rem; text-transform:uppercase;">⭐ FRANCHISE BATTING ANCHOR</span>
                <h2 style="margin:0.2rem 0; color:#FFFFFF;">{mvp['player']}</h2>
                <div style="color:#94A3B8; font-size:0.95rem;">
                    Innings: <b>{mvp['innings']}</b> &nbsp;|&nbsp; High Score: <b>{mvp['highest_score']}</b> &nbsp;|&nbsp; 
                    Fifties: <b>{mvp['fifties']}</b> &nbsp;|&nbsp; Hundreds: <b>{mvp['hundreds']}</b>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2.2rem; font-weight:800; color:{meta['accent']};">{mvp['runs']:,} Runs</div>
                <div style="color:#38BDF8; font-weight:600; font-size:1.1rem;">Avg: {mvp['average']} &nbsp;|&nbsp; SR: {mvp['strike_rate']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    filtered_batsmen = top_bat_df

# Charts Row 1
ch1, ch2 = st.columns([1.6, 1.1])
with ch1:
    st.markdown("### 📊 Top Run Scorers")
    st.plotly_chart(plot_runs_by_player(filtered_batsmen.head(10)), use_container_width=True)
with ch2:
    st.markdown("### 🥧 Boundary Run Distribution")
    mpl_fig = plot_boundary_distribution_mpl(summary["total_fours"], summary["total_sixes"], summary["total_runs"])
    st.pyplot(mpl_fig, use_container_width=True)

# Scatter Matrix: Runs vs Strike Rate
st.markdown("### 🎯 Scoring Volume vs Aggression Matrix (Runs vs SR)")
st.plotly_chart(plot_runs_vs_strike_rate(filtered_batsmen), use_container_width=True)

# Leaderboard Table
st.markdown("### 📋 Complete Batting Leaderboard")
if not filtered_batsmen.empty:
    st.dataframe(
        filtered_batsmen.style.background_gradient(subset=["runs", "strike_rate"], cmap="Blues"),
        use_container_width=True
    )
else:
    st.warning("No players matched the minimum balls filter.")

st.markdown("---")

# Situational Split: Batting First vs Chasing
st.markdown("### ⚖️ Situational Dynamics: Batting First vs Chasing")
split = get_batting_first_vs_chasing(selected_team, selected_season)

sp1, sp2 = st.columns(2)
with sp1:
    st.markdown(f"""
    <div style="background:#161F30; border-radius:10px; padding:1.3rem; border-left:5px solid #38BDF8; box-shadow:0 4px 6px rgba(0,0,0,0.2);">
        <h3 style="margin:0 0 0.5rem 0; color:#38BDF8;">Batting 1st (Setting Target)</h3>
        <p style="margin:0.2rem 0; color:#94A3B8;">Matches Setting Score: <b style="color:white;">{split['bat_first_matches']}</b></p>
        <p style="margin:0.2rem 0; color:#94A3B8;">Average Target Set: <b style="color:white;">{split['bat_first_avg']}</b></p>
        <div style="margin-top:0.8rem; font-size:1.3rem; font-weight:700; color:#38BDF8;">
            Win Rate: {split['bat_first_win_pct']}%
        </div>
    </div>
    """, unsafe_allow_html=True)
with sp2:
    st.markdown(f"""
    <div style="background:#161F30; border-radius:10px; padding:1.3rem; border-left:5px solid #F97316; box-shadow:0 4px 6px rgba(0,0,0,0.2);">
        <h3 style="margin:0 0 0.5rem 0; color:#F97316;">Batting 2nd (Chasing Target)</h3>
        <p style="margin:0.2rem 0; color:#94A3B8;">Matches Chasing: <b style="color:white;">{split['chasing_matches']}</b></p>
        <p style="margin:0.2rem 0; color:#94A3B8;">Average Chasing Score: <b style="color:white;">{split['chasing_avg']}</b></p>
        <div style="margin-top:0.8rem; font-size:1.3rem; font-weight:700; color:#F97316;">
            Win Rate: {split['chasing_win_pct']}%
        </div>
    </div>
    """, unsafe_allow_html=True)

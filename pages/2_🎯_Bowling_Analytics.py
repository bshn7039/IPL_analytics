"""
🎯 Page 2: Bowling Analytics
Detailed evaluation of wicket-taking efficiency, run-containment discipline,
economy distributions, and bowler quotas.
"""
import streamlit as st
from database.db import query
from analytics.bowling import get_team_bowling_summary, get_top_bowlers
from analytics.branding import get_franchise_meta
from visualization.bowling_charts import (
    plot_wickets_by_bowler, plot_economy_vs_wickets, plot_bowling_economy_bars_mpl
)

st.set_page_config(page_title="Bowling Analytics | IPL Hub", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .spotlight-card-bowl {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎯 Franchise Bowling Analytics")
st.markdown("Evaluating containment discipline, strike rates, economy thresholds, and wicket distribution.")

seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c_s, c_t, c_ov = st.columns([1.5, 2, 2.5])
with c_s:
    selected_season = st.selectbox("Season", seasons, index=0)
with c_t:
    selected_team = st.selectbox("Franchise Team", teams, index=0)
with c_ov:
    min_overs = st.slider("Filter: Min. Overs Bowled", min_value=0, max_value=50, value=8, step=4)

meta = get_franchise_meta(selected_team)
summary = get_team_bowling_summary(selected_team, selected_season)

st.markdown("---")

# Bowling KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Wickets Taken", f"{summary['total_wickets']}")
k2.metric("Overall Economy", f"{summary['economy']} RPO")
k3.metric("Bowling Average", f"{summary['bowling_avg']}")
k4.metric("Strike Rate", f"{summary['bowling_sr']} balls")
k5.metric("Maidens Bowled", f"{summary['maidens']}")

st.markdown("---")

# Bowler Spotlight
top_bowl_df = get_top_bowlers(selected_team, selected_season, limit=20)
if not top_bowl_df.empty:
    filtered_bowlers = top_bowl_df[top_bowl_df["overs"] >= min_overs] if "overs" in top_bowl_df.columns else top_bowl_df
    mvp_b = top_bowl_df.iloc[0]

    st.markdown(f"""
    <div class="spotlight-card-bowl" style="border-left: 6px solid #EF4444;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span style="color:#F87171; font-weight:700; font-size:0.85rem; text-transform:uppercase;">⚡ STRIKE BOWLER OF THE FRANCHISE</span>
                <h2 style="margin:0.2rem 0; color:#FFFFFF;">{mvp_b['player']}</h2>
                <div style="color:#94A3B8; font-size:0.95rem;">
                    Matches: <b>{mvp_b['matches']}</b> &nbsp;|&nbsp; Overs: <b>{mvp_b['overs']}</b> &nbsp;|&nbsp; 
                    Maidens: <b>{mvp_b['maidens']}</b> &nbsp;|&nbsp; Runs Conceded: <b>{mvp_b['runs_conceded']}</b>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2.2rem; font-weight:800; color:#EF4444;">{mvp_b['wickets']} Wickets</div>
                <div style="color:#38BDF8; font-weight:600; font-size:1.1rem;">Econ: {mvp_b['economy']} &nbsp;|&nbsp; Avg: {mvp_b['bowling_avg']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    filtered_bowlers = top_bowl_df

# Visualizations Row 1
ch1, ch2 = st.columns([1.5, 1.2])
with ch1:
    st.markdown("### 📊 Top Wicket Takers")
    st.plotly_chart(plot_wickets_by_bowler(filtered_bowlers.head(10)), use_container_width=True)
with ch2:
    st.markdown("### 📉 Economy Rate Benchmark")
    mpl_fig = plot_bowling_economy_bars_mpl(filtered_bowlers)
    st.pyplot(mpl_fig, use_container_width=True)

# Scatter: Economy vs Wickets Matrix
st.markdown("### 🎯 Economy vs Wicket-Taking Matrix")
st.plotly_chart(plot_economy_vs_wickets(filtered_bowlers), use_container_width=True)

# Leaderboard Table
st.markdown("### 📋 Complete Bowling Leaderboard")
if not filtered_bowlers.empty:
    st.dataframe(
        filtered_bowlers.style.background_gradient(subset=["wickets"], cmap="Reds")
                             .background_gradient(subset=["economy"], cmap="Blues_r"),
        use_container_width=True
    )
else:
    st.warning("No bowlers matched the minimum overs filter.")

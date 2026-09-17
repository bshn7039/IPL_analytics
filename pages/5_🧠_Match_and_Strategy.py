"""
🧠 Page 5: Match & Strategy Analytics
Strategic telemetry examining toss conversion rates, venue scoring dynamics,
interactive target-chase simulators, and phase-wise T20 phase execution.
"""
import streamlit as st
import plotly.express as px
from database.db import query
from analytics.strategy import get_toss_analysis, get_venue_analysis, get_phase_analysis

st.set_page_config(page_title="Match & Strategy | IPL Hub", page_icon="🧠", layout="wide")

st.markdown("# 🧠 Match & Tactical Strategy Intelligence")
st.markdown("Macro-level analytical telemetry on toss advantage, ground acoustics, target chase feasibility, and phase execution.")

seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

f1, f2 = st.columns(2)
with f1:
    season_opt = st.selectbox("Season Filter", ["All Seasons"] + seasons)
with f2:
    team_opt = st.selectbox("Franchise Scope", ["All Franchises"] + teams)

season_val = None if season_opt == "All Seasons" else int(season_opt)
team_val = None if team_opt == "All Franchises" else team_opt

st.markdown("---")

# Section 1: Toss Analytics
st.subheader("🪙 Toss Advantage & Decision Analysis")
toss_res = get_toss_analysis(season=season_val, team=team_val)

t1, t2, t3, t4 = st.columns(4)
t1.metric("Matches Evaluated", toss_res["total_matches"])
t2.metric("Chose to Field First", f"{toss_res['field_first_pct']}%", delta=f"{toss_res['field_first']} Matches")
t3.metric("Chose to Bat First", f"{toss_res['bat_first_pct']}%", delta=f"{toss_res['bat_first']} Matches")
t4.metric("Toss Winner Won Match", f"{toss_res['toss_win_match_win_pct']}%", delta=f"{round(toss_res['toss_win_match_win_pct'] - 50.0, 1)}% vs 50/50 baseline")

if toss_res["toss_win_match_win_pct"] > 53.0:
    st.info("💡 **Toss Significance**: Captains winning the toss possess a measurable mathematical edge in this selection.")
elif toss_res["toss_win_match_win_pct"] < 47.0:
    st.info("💡 **Toss Neutrality**: Winning the toss shows slight negative correlation with victory, indicating pitch conditions remain steady.")
else:
    st.info("💡 **Balanced Distribution**: Toss outcome exhibits nearly zero statistical correlation with final match victory.")

st.markdown("---")

# Section 2: Stadium & Pitch Analytics
st.subheader("🏟️ Stadium Scoring Profiler & Par Score Benchmark")
venues_df = get_venue_analysis(season=season_val)
if not venues_df.empty:
    fig_venue = px.bar(
        venues_df.head(10),
        x="venue",
        y=["avg_1st_innings", "avg_2nd_innings"],
        barmode="group",
        title="1st Innings vs 2nd Innings Average Score by Stadium",
        labels={"value": "Average Runs", "venue": "Stadium", "variable": "Innings"},
        color_discrete_map={"avg_1st_innings": "#38BDF8", "avg_2nd_innings": "#F59E0B"}
    )
    fig_venue.add_hline(y=175.0, line_dash="dash", line_color="#EF4444", annotation_text="League Par (175)")
    fig_venue.update_layout(template="plotly_dark", plot_bgcolor="#11151F", paper_bgcolor="#11151F")
    st.plotly_chart(fig_venue, use_container_width=True)

    st.dataframe(
        venues_df.style.background_gradient(subset=["avg_1st_innings"], cmap="YlOrRd"),
        use_container_width=True
    )

st.markdown("---")

# Interactive Target Chase Simulator
st.subheader("🎯 Interactive Target Chase Predictor")
st.markdown("Estimate target chase success probability based on pitch scoring history.")

sc1, sc2, sc3 = st.columns([1.5, 1.5, 1])
with sc1:
    sim_venue = st.selectbox("Select Ground", venues_df["venue"].tolist() if not venues_df.empty else ["Wankhede Stadium"])
with sc2:
    sim_target = st.slider("Target Score to Chase", min_value=120, max_value=240, value=180, step=5)
with sc3:
    # Target simulator calculation
    venue_row = venues_df[venues_df["venue"] == sim_venue].iloc[0] if not venues_df.empty and sim_venue in venues_df["venue"].values else None
    par_score = venue_row["avg_1st_innings"] if venue_row is not None else 175.0
    
    # Sigmoid probability curve
    diff = par_score - sim_target
    chase_prob = round(min(95.0, max(5.0, 50.0 + (diff * 1.6))), 1)
    defend_prob = round(100.0 - chase_prob, 1)
    
    st.markdown(f"""
    <div style="background:#161F30; border-radius:10px; padding:0.8rem; text-align:center; border: 1px solid rgba(59, 130, 246, 0.3);">
        <div style="font-size:0.75rem; color:#94A3B8;">CHASE PROBABILITY</div>
        <div style="font-size:1.6rem; font-weight:800; color:{'#10B981' if chase_prob >= 50 else '#EF4444'};">
            {chase_prob}%
        </div>
        <div style="font-size:0.75rem; color:#64748B;">Defend Chance: {defend_prob}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Section 3: Phase Analysis
st.subheader("⏱️ T20 Phase-by-Phase Execution Breakdown")
st.markdown("""
- **Powerplay (Overs 1–6)**: 2 fielders outside 30-yard circle; aggression and early momentum.
- **Middle Overs (Overs 7–15)**: Rotation of strike, spin bowling containment, boundary hunting.
- **Death Overs (Overs 16–20)**: High-risk acceleration, yorkers, boundary preservation.
""")
phase_df = get_phase_analysis(team=team_val, season=season_val)
st.table(phase_df.set_index("Phase"))

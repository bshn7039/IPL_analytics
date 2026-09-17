"""
⚔️ Page 3: Team Comparison
Comprehensive head-to-head analysis between any two IPL franchises,
featuring radar comparison, comparative grouped metrics, simulated win probability, and tactical verdicts.
"""
import streamlit as st
import pandas as pd
from database.db import query
from analytics.comparison import compare_teams
from analytics.branding import get_franchise_meta
from visualization.comparison_charts import plot_team_radar, plot_comparison_grouped_bars

st.set_page_config(page_title="Team Comparison | IPL Hub", page_icon="⚔️", layout="wide")

st.markdown("# ⚔️ Franchise Head-to-Head Comparison")
st.markdown("Direct tactical benchmarking, radar strength distributions, and historical match outcomes.")

seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c1, c2, c3 = st.columns(3)
with c1:
    team_a = st.selectbox("Franchise A (Blue Corner)", teams, index=0)
with c2:
    team_b = st.selectbox("Franchise B (Orange Corner)", teams, index=1 if len(teams) > 1 else 0)
with c3:
    selected_season = st.selectbox("Season Scope", ["All Seasons"] + seasons, index=0)

season_param = None if selected_season == "All Seasons" else int(selected_season)
cmp_data = compare_teams(team_a, team_b, season_param)

meta_a = get_franchise_meta(team_a)
meta_b = get_franchise_meta(team_b)

st.markdown("---")

# H2H Banner & Strength Index
h_col1, h_col2, h_col3 = st.columns([1.5, 1.8, 1.5])
with h_col1:
    st.markdown(f"""
    <div style="background:#161F30; border-radius:12px; padding:1.5rem; text-align:center; border-top:5px solid {meta_a['accent']}; box-shadow:0 4px 10px rgba(0,0,0,0.3);">
        <div style="font-size:1.8rem;">{meta_a['emoji']}</div>
        <h2 style="margin:0.2rem 0; color:#FFFFFF;">{meta_a['full_name']}</h2>
        <div style="color:#94A3B8; font-size:0.85rem; text-transform:uppercase;">Team Strength Score</div>
        <h2 style="margin:0.2rem 0; color:{meta_a['accent']};">⚡ {cmp_data['score_a']}<span style="font-size:1rem; color:#64748B;">/100</span></h2>
        <div style="margin-top:0.6rem; font-size:1.2rem; color:#10B981; font-weight:700;">{cmp_data['h2h_wins_a']} H2H Wins</div>
    </div>
    """, unsafe_allow_html=True)

with h_col2:
    # Calculate simulated win probability
    diff = cmp_data['score_a'] - cmp_data['score_b']
    h2h_total = max(1, cmp_data['h2h_matches'])
    h2h_rate_a = (cmp_data['h2h_wins_a'] / h2h_total) * 100
    prob_a = round(min(85.0, max(15.0, 50.0 + (diff * 1.5) + ((h2h_rate_a - 50.0) * 0.2))), 1)
    prob_b = round(100.0 - prob_a, 1)

    st.markdown(f"""
    <div style="background:#111827; border-radius:12px; padding:1.2rem; text-align:center; border: 1px solid rgba(255,255,255,0.06); height:100%;">
        <span style="font-size:0.85rem; color:#94A3B8; letter-spacing:0.08em; text-transform:uppercase; font-weight:600;">HEAD-TO-HEAD MATCHUP</span>
        <h1 style="margin:0.2rem 0; font-size:2.4rem; color:#F59E0B;">VS</h1>
        <div style="font-size:1.05rem; color:#E2E8F0; margin-bottom:0.8rem;">Total Encounters: <b>{cmp_data['h2h_matches']}</b></div>
        
        <div style="font-size:0.8rem; color:#94A3B8; margin-bottom:0.3rem;">Simulated Match Win Probability:</div>
        <div style="background:#1F2937; border-radius:8px; height:18px; width:100%; display:flex; overflow:hidden;">
            <div style="background:{meta_a['accent']}; width:{prob_a}%; height:100%;"></div>
            <div style="background:{meta_b['accent']}; width:{prob_b}%; height:100%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-top:0.3rem;">
            <span style="color:{meta_a['accent']}; font-weight:700;">{team_a}: {prob_a}%</span>
            <span style="color:{meta_b['accent']}; font-weight:700;">{team_b}: {prob_b}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_col3:
    st.markdown(f"""
    <div style="background:#161F30; border-radius:12px; padding:1.5rem; text-align:center; border-top:5px solid {meta_b['accent']}; box-shadow:0 4px 10px rgba(0,0,0,0.3);">
        <div style="font-size:1.8rem;">{meta_b['emoji']}</div>
        <h2 style="margin:0.2rem 0; color:#FFFFFF;">{meta_b['full_name']}</h2>
        <div style="color:#94A3B8; font-size:0.85rem; text-transform:uppercase;">Team Strength Score</div>
        <h2 style="margin:0.2rem 0; color:{meta_b['accent']};">⚡ {cmp_data['score_b']}<span style="font-size:1rem; color:#64748B;">/100</span></h2>
        <div style="margin-top:0.6rem; font-size:1.2rem; color:#10B981; font-weight:700;">{cmp_data['h2h_wins_b']} H2H Wins</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Visual Comparisons
rc1, rc2 = st.columns([1.5, 1.3])
with rc1:
    st.subheader("🕸️ Tactical Radar Profile (5 Normalized Axes)")
    st.plotly_chart(plot_team_radar(cmp_data['stats_a'], cmp_data['stats_b'], team_a, team_b), use_container_width=True)
with rc2:
    st.subheader("📊 Direct Metric Differential")
    st.plotly_chart(plot_comparison_grouped_bars(cmp_data['stats_a'], cmp_data['stats_b'], team_a, team_b), use_container_width=True)

# Side-by-side Metric Comparison Table
st.subheader("📋 Statistical Matrix Breakdown")
metrics_table = pd.DataFrame([
    {"Metric": "Win Percentage", team_a: f"{cmp_data['stats_a']['win_rate']}%", team_b: f"{cmp_data['stats_b']['win_rate']}%"},
    {"Metric": "Average Innings Score", team_a: cmp_data['stats_a']['avg_score'], team_b: cmp_data['stats_b']['avg_score']},
    {"Metric": "Batting Strike Rate", team_a: cmp_data['stats_a']['batting_sr'], team_b: cmp_data['stats_b']['batting_sr']},
    {"Metric": "Bowling Economy (RPO)", team_a: cmp_data['stats_a']['economy'], team_b: cmp_data['stats_b']['economy']},
    {"Metric": "Bowling Average", team_a: cmp_data['stats_a']['bowling_avg'], team_b: cmp_data['stats_b']['bowling_avg']},
    {"Metric": "Total Wickets Taken", team_a: cmp_data['stats_a']['wickets'], team_b: cmp_data['stats_b']['wickets']},
    {"Metric": "Total Sixes Hit", team_a: cmp_data['stats_a']['total_sixes'], team_b: cmp_data['stats_b']['total_sixes']}
])
st.table(metrics_table.set_index("Metric"))

# Automated Analytical Verdict
st.markdown("### 💡 Qualitative Tactical Verdict")
st.info(f"**{cmp_data['verdict']}**")

# Head to head match history
if not cmp_data["h2h_df"].empty:
    st.subheader(f"📜 Match History Log: {team_a} vs {team_b}")
    st.dataframe(cmp_data["h2h_df"][["season", "date", "venue", "winner", "result"]], use_container_width=True)

"""
👤 Page 4: Player Comparison
Individual head-to-head benchmarking for batters, bowlers, and all-rounders
with 5-dimensional skill spider charts and metric tables.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import query
from analytics.comparison import compare_players
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles
from visualization.comparison_charts import plot_player_comparison_bars

st.set_page_config(page_title="Player Comparison | IPL Hub", page_icon="👤", layout="wide")
apply_custom_styles()

st.markdown("# 👤 Individual Player Head-to-Head Benchmarking")
st.markdown("Compare scoring dynamics, boundary frequencies, consistency averages, and bowling figures.")

# Fetch players with role metadata
players_df = query("SELECT player_name, team_short, role FROM players ORDER BY player_name ASC")

# Role Filter
role_filter = st.radio("Filter Players by Role:", ["All Roles", "Batter", "Bowler", "All-rounder", "Wicketkeeper"], horizontal=True)
if role_filter != "All Roles":
    filtered_roster = players_df[players_df["role"] == role_filter]
else:
    filtered_roster = players_df

player_names = filtered_roster["player_name"].tolist() if not filtered_roster.empty else players_df["player_name"].tolist()

p_col1, p_col2 = st.columns(2)
with p_col1:
    default_a = "Virat Kohli" if "Virat Kohli" in player_names else player_names[0]
    player_a = st.selectbox("Select Player A", player_names, index=player_names.index(default_a) if default_a in player_names else 0)
with p_col2:
    default_b = "Rohit Sharma" if "Rohit Sharma" in player_names else (player_names[1] if len(player_names) > 1 else player_names[0])
    player_b = st.selectbox("Select Player B", player_names, index=player_names.index(default_b) if default_b in player_names else 0)

# Get player metadata
p_meta_a = players_df[players_df["player_name"] == player_a].iloc[0] if not players_df[players_df["player_name"] == player_a].empty else None
p_meta_b = players_df[players_df["player_name"] == player_b].iloc[0] if not players_df[players_df["player_name"] == player_b].empty else None

team_meta_a = get_franchise_meta(p_meta_a["team_short"]) if p_meta_a is not None else get_franchise_meta("MI")
team_meta_b = get_franchise_meta(p_meta_b["team_short"]) if p_meta_b is not None else get_franchise_meta("CSK")

cmp_res = compare_players(player_a, player_b)
bat_a = cmp_res["bat_a"]
bat_b = cmp_res["bat_b"]
bowl_a = cmp_res["bowl_a"]
bowl_b = cmp_res["bowl_b"]

st.markdown("---")

# Profile Cards Header
c_a, c_b = st.columns(2)
with c_a:
    p1_html = f"""<div class="analytics-card" style="border-left:5px solid {team_meta_a['accent']}; text-align:left; padding:1.3rem 1.6rem;">
<div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Franchise: {team_meta_a['full_name']} ({p_meta_a['team_short'] if p_meta_a is not None else ''})</div>
<h2 style="margin:0.2rem 0; color:#FFFFFF; font-weight:800;">{player_a}</h2>
<span style="background:#1E293B; color:#38BDF8; padding:0.3rem 0.7rem; border-radius:6px; font-size:0.85rem; font-weight:700;">
{p_meta_a['role'] if p_meta_a is not None else 'Cricketer'}
</span>
</div>"""
    st.markdown(p1_html, unsafe_allow_html=True)

with c_b:
    p2_html = f"""<div class="analytics-card" style="border-left:5px solid {team_meta_b['accent']}; text-align:left; padding:1.3rem 1.6rem;">
<div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Franchise: {team_meta_b['full_name']} ({p_meta_b['team_short'] if p_meta_b is not None else ''})</div>
<h2 style="margin:0.2rem 0; color:#FFFFFF; font-weight:800;">{player_b}</h2>
<span style="background:#1E293B; color:#F97316; padding:0.3rem 0.7rem; border-radius:6px; font-size:0.85rem; font-weight:700;">
{p_meta_b['role'] if p_meta_b is not None else 'Cricketer'}
</span>
</div>"""
    st.markdown(p2_html, unsafe_allow_html=True)

st.markdown("---")

# Batting Comparison Section
st.subheader("🏏 Batting Head-to-Head Breakdown")
if bat_a or bat_b:
    bc1, bc2 = st.columns([1.4, 1.2])
    with bc1:
        st.plotly_chart(plot_player_comparison_bars(bat_a, bat_b, player_a, player_b), use_container_width=True)
    with bc2:
        categories = ["Volume", "Consistency", "Strike Rate", "Sixes Rate", "Milestones"]
        def norm_p(b):
            if not b: return [0, 0, 0, 0, 0]
            v = min(100.0, max(10.0, b.get("runs", 0) / 700 * 100))
            c = min(100.0, max(10.0, b.get("average", 0) / 55 * 100))
            s = min(100.0, max(10.0, (b.get("strike_rate", 100) - 100) / (180 - 100) * 100))
            six = min(100.0, max(10.0, b.get("sixes", 0) / 35 * 100))
            m = min(100.0, max(10.0, (b.get("fifties", 0) * 20) + (b.get("hundreds", 0) * 40)))
            return [v, c, s, six, m]
        
        va = norm_p(bat_a) + [norm_p(bat_a)[0]]
        vb = norm_p(bat_b) + [norm_p(bat_b)[0]]
        cat_l = categories + [categories[0]]
        
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=va, theta=cat_l, fill="toself", name=player_a, line_color="#10B981"))
        fig_r.add_trace(go.Scatterpolar(r=vb, theta=cat_l, fill="toself", name=player_b, line_color="#6366F1"))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template="plotly_dark",
            paper_bgcolor="#11151F",
            title="Skill Attribute Radar",
            margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(fig_r, use_container_width=True)

    bat_comparison = pd.DataFrame([
        {"Metric": "Innings Played", player_a: bat_a.get("innings", 0) if bat_a else 0, player_b: bat_b.get("innings", 0) if bat_b else 0},
        {"Metric": "Career Runs", player_a: f"{bat_a.get('runs', 0):,}" if bat_a else 0, player_b: f"{bat_b.get('runs', 0):,}" if bat_b else 0},
        {"Metric": "Batting Average", player_a: bat_a.get("average", 0) if bat_a else 0, player_b: bat_b.get("average", 0) if bat_b else 0},
        {"Metric": "Strike Rate (%)", player_a: bat_a.get("strike_rate", 0) if bat_a else 0, player_b: bat_b.get("strike_rate", 0) if bat_b else 0},
        {"Metric": "Fours (4s)", player_a: bat_a.get("fours", 0) if bat_a else 0, player_b: bat_b.get("fours", 0) if bat_b else 0},
        {"Metric": "Sixes (6s)", player_a: bat_a.get("sixes", 0) if bat_a else 0, player_b: bat_b.get("sixes", 0) if bat_b else 0},
        {"Metric": "Fifties (50s)", player_a: bat_a.get("fifties", 0) if bat_a else 0, player_b: bat_b.get("fifties", 0) if bat_b else 0},
        {"Metric": "Hundreds (100s)", player_a: bat_a.get("hundreds", 0) if bat_a else 0, player_b: bat_b.get("hundreds", 0) if bat_b else 0},
        {"Metric": "Highest Score", player_a: bat_a.get("highest_score", 0) if bat_a else 0, player_b: bat_b.get("highest_score", 0) if bat_b else 0}
    ])
    st.table(bat_comparison.set_index("Metric"))

# Bowling Section
if bowl_a or bowl_b:
    st.markdown("---")
    st.subheader("🎯 Bowling Head-to-Head Breakdown")
    bowl_comparison = pd.DataFrame([
        {"Metric": "Overs Bowled", player_a: bowl_a.get("overs", 0) if bowl_a else 0, player_b: bowl_b.get("overs", 0) if bowl_b else 0},
        {"Metric": "Wickets Taken", player_a: bowl_a.get("wickets", 0) if bowl_a else 0, player_b: bowl_b.get("wickets", 0) if bowl_b else 0},
        {"Metric": "Economy Rate (RPO)", player_a: bowl_a.get("economy", 0) if bowl_a else 0, player_b: bowl_b.get("economy", 0) if bowl_b else 0},
        {"Metric": "Bowling Average", player_a: bowl_a.get("bowling_avg", "N/A") if bowl_a else "N/A", player_b: bowl_b.get("bowling_avg", "N/A") if bowl_b else "N/A"},
        {"Metric": "Strike Rate (Balls/Wkt)", player_a: bowl_a.get("bowling_sr", "N/A") if bowl_a else "N/A", player_b: bowl_b.get("bowling_sr", "N/A") if bowl_b else "N/A"},
        {"Metric": "Maidens Bowled", player_a: bowl_a.get("maidens", 0) if bowl_a else 0, player_b: bowl_b.get("maidens", 0) if bowl_b else 0}
    ])
    st.table(bowl_comparison.set_index("Metric"))

"""
Page 3: Team Comparison
Comprehensive head-to-head analysis between any two IPL franchises,
featuring radar comparison, comparative grouped metrics, simulated win probability, and tactical verdicts.
"""
import streamlit as st
import pandas as pd
from database.db import query
from analytics.comparison import compare_teams
from analytics.branding import get_franchise_meta
from analytics.ui_styles import apply_custom_styles
from visualization.comparison_charts import plot_team_radar, plot_comparison_grouped_bars

st.set_page_config(page_title="Team Comparison | IPL Hub", page_icon="⚔️", layout="wide")
apply_custom_styles()

st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #0D1A1A 0%, #121F20 60%, #091515 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(245, 158, 11, 0.18);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 280px; height: 100%;
    background: radial-gradient(circle at right, rgba(245, 158, 11, 0.1) 0%, transparent 65%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #F59E0B;
    margin-bottom: 0.5rem;
}
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.6rem 0;
}
.franchise-card {
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
    text-align: center;
    transition: all 0.25s ease;
}
.vs-box {
    background: linear-gradient(145deg, #111827, #1A2236);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.chart-wrapper {
    background: linear-gradient(160deg, #0E1626 0%, #0A1020 100%);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 1rem 1.2rem 0.5rem;
    margin-bottom: 1rem;
}
.chart-title {
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    margin-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 0.5rem;
}
.verdict-card {
    background: linear-gradient(145deg, #0F172A, #141E33);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    border: 1px solid rgba(245, 158, 11, 0.25);
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}
.metrics-table-wrapper {
    background: linear-gradient(160deg, #0E1626 0%, #0A1020 100%);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">Analytics Module 03</div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">Franchise Head-to-Head Comparison</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">Tactical benchmarking, radar strength distributions, simulated match outcome probability, and historical H2H record.</p>
</div>
""", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────────────────
seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

c1, c2, c3 = st.columns(3)
with c1:
    team_a = st.selectbox("Franchise A", teams, index=0)
with c2:
    team_b = st.selectbox("Franchise B", teams, index=1 if len(teams) > 1 else 0)
with c3:
    selected_season = st.selectbox("Season Scope", ["All Seasons"] + seasons, index=0)

season_param = None if selected_season == "All Seasons" else int(selected_season)
cmp_data = compare_teams(team_a, team_b, season_param)

meta_a = get_franchise_meta(team_a)
meta_b = get_franchise_meta(team_b)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Win Probability Calculation ───────────────────────────────────────────────
diff = cmp_data['score_a'] - cmp_data['score_b']
h2h_total = max(1, cmp_data['h2h_matches'])
h2h_rate_a = (cmp_data['h2h_wins_a'] / h2h_total) * 100
prob_a = round(min(88.0, max(12.0, 50.0 + (diff * 1.5) + ((h2h_rate_a - 50.0) * 0.2))), 1)
prob_b = round(100.0 - prob_a, 1)

# ── H2H Matchup Cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Head-to-Head Matchup Overview</div>', unsafe_allow_html=True)
h_col1, h_col2, h_col3 = st.columns([1.5, 1.8, 1.5])

with h_col1:
    st.markdown(f"""
<div class="franchise-card" style="border-top:4px solid {meta_a['accent']};">
<div style="font-size:2.8rem; margin-bottom:0.4rem;">{meta_a['emoji']}</div>
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">{team_a}</div>
<h3 style="margin:0 0 0.8rem; color:#FFFFFF; font-weight:800; font-size:1.1rem;">{meta_a['full_name']}</h3>
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">Strength Index</div>
<div style="font-size:2.2rem; font-weight:800; color:{meta_a['accent']}; font-variant-numeric:tabular-nums;">{cmp_data['score_a']}<span style="font-size:1rem; color:#334155;">/100</span></div>
<div style="margin-top:0.6rem; font-size:1.1rem; color:#10B981; font-weight:700;">{cmp_data['h2h_wins_a']} H2H Wins</div>
</div>
""", unsafe_allow_html=True)

with h_col2:
    st.markdown(f"""
<div class="vs-box">
<div style="font-size:0.72rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">Head-to-Head</div>
<div style="font-size:2.8rem; font-weight:900; color:#F59E0B; letter-spacing:-0.03em; line-height:1;">VS</div>
<div style="font-size:0.9rem; color:#94A3B8; margin:0.6rem 0;">{cmp_data['h2h_matches']} Encounters</div>
<div style="font-size:0.72rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">Simulated Win Probability</div>
<div style="background:#0F172A; border-radius:8px; height:16px; width:100%; display:flex; overflow:hidden; border:1px solid rgba(255,255,255,0.08);">
<div style="background:{meta_a['accent']}; width:{prob_a}%; height:100%; border-radius:4px 0 0 4px;"></div>
<div style="background:{meta_b['accent']}; width:{prob_b}%; height:100%; border-radius:0 4px 4px 0;"></div>
</div>
<div style="display:flex; justify-content:space-between; margin-top:0.5rem; font-size:0.82rem; font-weight:700; font-family:'Space Mono',monospace;">
<span style="color:{meta_a['accent']};">{team_a} {prob_a}%</span>
<span style="color:{meta_b['accent']};">{team_b} {prob_b}%</span>
</div>
</div>
""", unsafe_allow_html=True)

with h_col3:
    st.markdown(f"""
<div class="franchise-card" style="border-top:4px solid {meta_b['accent']};">
<div style="font-size:2.8rem; margin-bottom:0.4rem;">{meta_b['emoji']}</div>
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">{team_b}</div>
<h3 style="margin:0 0 0.8rem; color:#FFFFFF; font-weight:800; font-size:1.1rem;">{meta_b['full_name']}</h3>
<div style="font-size:0.7rem; font-family:'Space Mono',monospace; color:#64748B; text-transform:uppercase; letter-spacing:0.08em;">Strength Index</div>
<div style="font-size:2.2rem; font-weight:800; color:{meta_b['accent']}; font-variant-numeric:tabular-nums;">{cmp_data['score_b']}<span style="font-size:1rem; color:#334155;">/100</span></div>
<div style="margin-top:0.6rem; font-size:1.1rem; color:#10B981; font-weight:700;">{cmp_data['h2h_wins_b']} H2H Wins</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Radar + Grouped Bars ──────────────────────────────────────────────────────
rc1, rc2 = st.columns([1.5, 1.3])
with rc1:
    st.markdown('<div class="chart-wrapper"><div class="chart-title">Tactical Radar Profile — 5-Axis Normalized Comparison</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_team_radar(cmp_data['stats_a'], cmp_data['stats_b'], team_a, team_b), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with rc2:
    st.markdown('<div class="chart-wrapper"><div class="chart-title">Direct Metric Differential — Grouped Bars</div>', unsafe_allow_html=True)
    st.plotly_chart(plot_comparison_grouped_bars(cmp_data['stats_a'], cmp_data['stats_b'], team_a, team_b), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Statistical Matrix Table ──────────────────────────────────────────────────
st.markdown('<div class="section-label">Statistical Matrix Breakdown</div>', unsafe_allow_html=True)
metrics_table = pd.DataFrame([
    {"Metric": "Win Percentage",      team_a: f"{cmp_data['stats_a']['win_rate']}%",    team_b: f"{cmp_data['stats_b']['win_rate']}%"},
    {"Metric": "Average Innings Score",team_a: cmp_data['stats_a']['avg_score'],         team_b: cmp_data['stats_b']['avg_score']},
    {"Metric": "Batting Strike Rate", team_a: cmp_data['stats_a']['batting_sr'],         team_b: cmp_data['stats_b']['batting_sr']},
    {"Metric": "Bowling Economy",     team_a: cmp_data['stats_a']['economy'],            team_b: cmp_data['stats_b']['economy']},
    {"Metric": "Bowling Average",     team_a: cmp_data['stats_a']['bowling_avg'],        team_b: cmp_data['stats_b']['bowling_avg']},
    {"Metric": "Wickets Taken",       team_a: cmp_data['stats_a']['wickets'],            team_b: cmp_data['stats_b']['wickets']},
    {"Metric": "Total Sixes",         team_a: cmp_data['stats_a']['total_sixes'],        team_b: cmp_data['stats_b']['total_sixes']},
])
st.table(metrics_table.set_index("Metric"))

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Tactical Verdict ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="verdict-card">
<div class="section-label">Qualitative Tactical Verdict</div>
<p style="margin:0.5rem 0 0; color:#CBD5E1; font-size:1rem; line-height:1.6;">{cmp_data['verdict']}</p>
</div>
""", unsafe_allow_html=True)

# ── H2H Match History ─────────────────────────────────────────────────────────
if not cmp_data["h2h_df"].empty:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">Match History Log — {team_a} vs {team_b}</div>', unsafe_allow_html=True)
    st.dataframe(cmp_data["h2h_df"][["season", "date", "venue", "winner", "result"]], use_container_width=True)

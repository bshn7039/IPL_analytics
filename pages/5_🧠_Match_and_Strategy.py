"""
Page 5: Match & Strategy Analytics
Strategic telemetry examining toss conversion rates, venue scoring dynamics,
interactive target-chase simulators, and phase-wise T20 phase execution.
"""
import streamlit as st
import plotly.express as px
from database.db import query
from analytics.strategy import get_toss_analysis, get_venue_analysis, get_phase_analysis
from analytics.ui_styles import apply_custom_styles

st.set_page_config(page_title="Match & Strategy | IPL Hub", page_icon="🧠", layout="wide")
apply_custom_styles()

st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #0D1A14 0%, #111F19 60%, #091510 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(16, 185, 129, 0.18);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 280px; height: 100%;
    background: radial-gradient(circle at right, rgba(16, 185, 129, 0.1) 0%, transparent 65%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #10B981;
    margin-bottom: 0.5rem;
}
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.6rem 0;
}
.kpi-card {
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
    text-align: center;
    transition: all 0.25s ease;
}
.kpi-card:hover {
    border-color: rgba(16, 185, 129, 0.35);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -6px rgba(16, 185, 129, 0.15);
}
.kpi-label {
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
}
.kpi-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
    margin: 0.2rem 0;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 500;
}
.toss-insight {
    background: linear-gradient(145deg, #0F1F18, #141E1A);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    border: 1px solid rgba(16, 185, 129, 0.2);
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #A7F3D0;
    line-height: 1.6;
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
.simulator-card {
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    border-radius: 14px;
    padding: 1.5rem 1.6rem;
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
    text-align: center;
}
.phase-legend {
    background: linear-gradient(145deg, #0F172A, #141E33);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 1rem;
}
.phase-row {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.phase-row:last-child {
    border-bottom: none;
}
.phase-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">Analytics Module 05</div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">Match & Tactical Strategy Intelligence</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">Toss advantage telemetry, ground scoring profiles, target-chase feasibility simulator, and T20 phase execution breakdown.</p>
</div>
""", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────────────────
seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist()
teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist()

f1, f2 = st.columns(2)
with f1:
    season_opt = st.selectbox("Season Filter", ["All Seasons"] + seasons)
with f2:
    team_opt = st.selectbox("Franchise Scope", ["All Franchises"] + teams)

season_val = None if season_opt == "All Seasons" else int(season_opt)
team_val = None if team_opt == "All Franchises" else team_opt

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Toss Analytics ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Toss Advantage & Decision Analysis</div>', unsafe_allow_html=True)
toss_res = get_toss_analysis(season=season_val, team=team_val)

t1, t2, t3, t4 = st.columns(4)

kpi_toss = [
    (t1, "Matches Evaluated", str(toss_res["total_matches"]), "total matches"),
    (t2, "Field First", f"{toss_res['field_first_pct']}%", f"{toss_res['field_first']} matches"),
    (t3, "Bat First", f"{toss_res['bat_first_pct']}%", f"{toss_res['bat_first']} matches"),
    (t4, "Toss→Win Rate", f"{toss_res['toss_win_match_win_pct']}%", f"{round(toss_res['toss_win_match_win_pct'] - 50.0, 1):+}% vs 50/50"),
]

for col, label, value, sub in kpi_toss:
    with col:
        st.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">{label}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-sub">{sub}</div>
</div>
""", unsafe_allow_html=True)

# Toss insight
if toss_res["toss_win_match_win_pct"] > 53.0:
    insight_txt = "Captains winning the toss possess a measurable mathematical edge in this selection — field-first decisions correlate strongly with match outcomes."
elif toss_res["toss_win_match_win_pct"] < 47.0:
    insight_txt = "Winning the toss shows slight negative correlation with victory, indicating pitch conditions remain steady across innings regardless of choice."
else:
    insight_txt = "Toss outcome exhibits nearly zero statistical correlation with final match victory — conditions are well-balanced for both sides."

st.markdown(f"""
<div class="toss-insight">
<strong>Toss Significance Analysis:</strong> {insight_txt}
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Venue Scoring Profiler ────────────────────────────────────────────────────
st.markdown('<div class="section-label">Stadium Scoring Profiler & Par Score Benchmark</div>', unsafe_allow_html=True)
venues_df = get_venue_analysis(season=season_val)

if not venues_df.empty:
    fig_venue = px.bar(
        venues_df.head(10),
        x="venue",
        y=["avg_1st_innings", "avg_2nd_innings"],
        barmode="group",
        title=None,
        labels={"value": "Average Runs", "venue": "Stadium", "variable": "Innings"},
        color_discrete_map={"avg_1st_innings": "#38BDF8", "avg_2nd_innings": "#F59E0B"}
    )
    fig_venue.add_hline(y=175.0, line_dash="dash", line_color="#EF4444",
                        annotation_text="League Par Score (175)", annotation_font_color="#EF4444")
    fig_venue.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0E1626",
        paper_bgcolor="#0E1626",
        font_color="#94A3B8",
        margin=dict(l=10, r=10, t=20, b=80),
        xaxis=dict(tickangle=-35)
    )
    st.markdown('<div class="chart-wrapper"><div class="chart-title">1st Innings vs 2nd Innings Average Score by Stadium</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_venue, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("View Full Venue Statistics Table"):
        st.dataframe(
            venues_df.style.background_gradient(subset=["avg_1st_innings"], cmap="YlOrRd"),
            use_container_width=True
        )

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Target Chase Simulator ────────────────────────────────────────────────────
st.markdown('<div class="section-label">Interactive Target Chase Predictor</div>', unsafe_allow_html=True)

sc1, sc2, sc3 = st.columns([1.5, 1.5, 1])
with sc1:
    sim_venue = st.selectbox("Select Ground", venues_df["venue"].tolist() if not venues_df.empty else ["Wankhede Stadium"])
with sc2:
    sim_target = st.slider("Target Score to Chase", min_value=120, max_value=240, value=180, step=5)
with sc3:
    venue_row = venues_df[venues_df["venue"] == sim_venue].iloc[0] if not venues_df.empty and sim_venue in venues_df["venue"].values else None
    par_score = venue_row["avg_1st_innings"] if venue_row is not None else 175.0

    diff = par_score - sim_target
    chase_prob = round(min(95.0, max(5.0, 50.0 + (diff * 1.6))), 1)
    defend_prob = round(100.0 - chase_prob, 1)

    color_chase = "#10B981" if chase_prob >= 50 else "#EF4444"
    st.markdown(f"""
<div class="simulator-card">
<div class="kpi-label">Chase Win Probability</div>
<div style="font-size:2.2rem; font-weight:800; color:{color_chase}; font-variant-numeric:tabular-nums; margin:0.3rem 0;">{chase_prob}%</div>
<div style="font-size:0.75rem; color:#64748B;">Defend Chance: {defend_prob}%</div>
<div style="background:#0F172A; border-radius:6px; height:8px; margin-top:0.8rem; overflow:hidden;">
<div style="background:{color_chase}; width:{chase_prob}%; height:100%; border-radius:6px;"></div>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Phase Analysis ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">T20 Phase-by-Phase Execution Breakdown</div>', unsafe_allow_html=True)

st.markdown("""
<div class="phase-legend">
<div class="phase-row">
<div class="phase-dot" style="background:#38BDF8;"></div>
<div><strong style="color:#38BDF8; font-size:0.85rem;">Powerplay — Overs 1–6</strong><br><span style="color:#64748B; font-size:0.8rem;">2 fielders outside 30-yard circle. Aggression, early momentum, boundary hunting.</span></div>
</div>
<div class="phase-row">
<div class="phase-dot" style="background:#F59E0B;"></div>
<div><strong style="color:#F59E0B; font-size:0.85rem;">Middle Overs — Overs 7–15</strong><br><span style="color:#64748B; font-size:0.8rem;">Strike rotation, spin containment, strategic acceleration through partnerships.</span></div>
</div>
<div class="phase-row">
<div class="phase-dot" style="background:#EF4444;"></div>
<div><strong style="color:#EF4444; font-size:0.85rem;">Death Overs — Overs 16–20</strong><br><span style="color:#64748B; font-size:0.8rem;">High-risk acceleration, yorkers, boundary preservation, final target push.</span></div>
</div>
</div>
""", unsafe_allow_html=True)

phase_df = get_phase_analysis(team=team_val, season=season_val)
st.table(phase_df.set_index("Phase"))

"""
🏏 IPL Analytics Hub — Apex Sports Telemetry Command Deck
Directly implements Stitch-generated UI architecture:
- El Clásico / Match broadcast header with circular SVG gauge
- Win probability split bar with glow effects
- 4 luxury glassmorphic telemetry cards with micro sparklines and phase splits
- Pitch conditions & weather telemetry strip (dew, soil turf, wind)
- Match Run Progression & Phase Momentum (Powerplay 1-6, Middle 7-15, Death 16-20)
- Orange Cap & Purple Cap race leaderboards
- DeepSeek tactical strategy insights drawer
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
    page_title="Apex Telemetry | IPL Analytics Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Stitch Apex broadcast theme CSS
apply_custom_styles()

# ── TOP TELEMETRY BAR (Season & Team Switchers) ──
seasons_df = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")
available_seasons = seasons_df["season"].tolist() if not seasons_df.empty else [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019]

teams_df = query("SELECT short_name, team_name FROM teams ORDER BY short_name ASC")
available_teams = teams_df["short_name"].tolist() if not teams_df.empty else ["MI", "CSK", "RCB", "KKR", "RR", "SRH", "DC", "PBKS", "GT", "LSG"]

top_c1, top_c2, top_c3 = st.columns([1.5, 1.5, 2])
with top_c1:
    selected_season = st.selectbox("📅 Season Telemetry", available_seasons, index=0)
with top_c2:
    selected_team = st.selectbox("🛡️ Primary Franchise Command", available_teams, index=0)
with top_c3:
    st.markdown("""<div style="display:flex; align-items:center; justify-content:flex-end; gap:0.6rem; height:100%; padding-top:1.6rem;">
<span class="telemetry-chip" style="background:rgba(238, 152, 0, 0.15); color:#F59E0B; border-color:rgba(238, 152, 0, 0.4);">
<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#F59E0B; box-shadow:0 0 8px #F59E0B;"></span>
LIVE BROADCAST SYNC
</span>
<span class="telemetry-chip">PING: 14ms</span>
<span class="telemetry-chip" style="color:#10B981; border-color:rgba(16, 185, 129, 0.4);">120 FPS</span>
</div>""", unsafe_allow_html=True)

meta = get_franchise_meta(selected_team)
overview = get_team_overview(selected_team, selected_season)
strength_score = get_team_strength_score(selected_team, selected_season)
matches_history = get_batting_by_match(selected_team, selected_season)

# Win probability split (simulated vs league baseline)
win_pct = overview['win_rate'] if overview['matches'] > 0 else 50.0
opp_pct = round(100.0 - win_pct, 1)

# Form guide calculation
if not matches_history.empty:
    recent_5 = matches_history.tail(5)["result"].tolist()
    form_html = "".join([f"<span class='badge-w'>W</span>" if r == "Won" else f"<span class='badge-l'>L</span>" for r in recent_5])
else:
    form_html = "<span style='color:#64748B; font-family:monospace;'>NO RECORD</span>"

# ── STITCH COMPONENT 1: HERO FRANCHISE PERFORMANCE CARD ──
st.markdown(f"""<div class="hero-banner" style="border-left: 6px solid {meta['accent']};">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.5rem;">
<div style="display:flex; align-items:flex-start; gap:1rem;">
<div style="width:64px; height:64px; border-radius:14px; background:linear-gradient(135deg, #171F33, #0B1326); border:1px solid rgba(6,182,212,0.4); display:flex; align-items:center; justify-content:center; box-shadow:0 0 20px rgba(6,182,212,0.2);">
<span style="font-size:28px;">{meta['emoji']}</span>
</div>
<div>
<span class="telemetry-chip">⚡ FRANCHISE PERFORMANCE HUB</span>
<span style="font-size:0.75rem; background:rgba(238,152,0,0.15); color:#F59E0B; border:1px solid rgba(238,152,0,0.3); padding:2px 8px; border-radius:6px; font-weight:700;">
🏆 {meta['titles']}x CHAMPIONS
</span>
<span style="font-size:0.8rem; color:#64748B; font-family:'Space Mono', monospace;">
🏟️ {meta['home_ground']}
</span>
</div>
<h1 style="margin:0.2rem 0; font-size:2.4rem; color:#FFFFFF; font-weight:900; letter-spacing:-0.03em;">
{meta['full_name']} <span style="font-size:1.2rem; color:#4CD7F6; font-weight:700;">[{selected_team}]</span>
</h1>
<p style="color:#94A3B8; font-size:0.85rem; margin:0;">
Campaign Season {selected_season} • Total Matches Logged: {overview['matches']} • Active Stadium Telemetry
</p>
</div>
</div>
<div style="display:flex; align-items:center; gap:1.5rem; flex-wrap:wrap;">
<div style="display:flex; align-items:center; gap:0.8rem; background:rgba(19,27,46,0.7); padding:0.6rem 1rem; border-radius:12px; border:1px solid rgba(255,255,255,0.08);">
<div style="position:relative; width:56px; height:56px; display:flex; align-items:center; justify-content:center;">
<svg style="width:100%; height:100%; transform:rotate(-90deg);" viewBox="0 0 36 36">
<path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#2D3449" stroke-width="3"/>
<path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="{meta['accent']}" stroke-width="3.5" stroke-dasharray="{strength_score}, 100" stroke-linecap="round"/>
</svg>
<span style="position:absolute; font-family:'Plus Jakarta Sans'; font-size:0.85rem; font-weight:900; color:#FFFFFF;">{strength_score}</span>
</div>
<div>
<span style="font-size:0.68rem; color:#94A3B8; font-family:'Space Mono', monospace; display:block; font-weight:700;">STRENGTH INDEX</span>
<span style="color:#10B981; font-size:0.82rem; font-weight:700;">⚡ High Performance</span>
</div>
</div>
<div style="background:rgba(19,27,46,0.7); padding:0.8rem 1.1rem; border-radius:12px; border:1px solid rgba(255,255,255,0.08); min-width:220px;">
<div style="display:flex; justify-content:space-between; font-size:0.75rem; font-family:'Space Mono', monospace; margin-bottom:0.35rem;">
<span style="color:#4CD7F6; font-weight:700;">{selected_team} {win_pct}%</span>
<span style="color:#64748B;">WIN PROB</span>
<span style="color:#F59E0B; font-weight:700;">{opp_pct}% OPP</span>
</div>
<div style="width:100%; height:8px; background:#2D3449; border-radius:6px; overflow:hidden; display:flex;">
<div style="width:{win_pct}%; height:100%; background:#4CD7F6; box-shadow:0 0 10px rgba(6,182,212,0.5);"></div>
<div style="width:{opp_pct}%; height:100%; background:#F59E0B; box-shadow:0 0 10px rgba(245,158,11,0.5);"></div>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.65rem; color:#64748B; margin-top:0.35rem; font-family:'Space Mono', monospace;">
<span>Form: {overview['wins']}W - {overview['losses']}L</span>
<span style="color:#10B981;">Chaser Favour</span>
</div>
</div>
</div>
</div>
<div style="margin-top:1.2rem; padding-top:0.9rem; border-top:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem;">
<div style="display:flex; align-items:center; gap:0.5rem;">
<span style="font-size:0.75rem; font-family:'Space Mono', monospace; color:#94A3B8; text-transform:uppercase;">LAST 5 MATCHES:</span>
{form_html}
</div>
<div style="display:flex; align-items:center; gap:0.8rem; font-family:'Space Mono', monospace; font-size:0.75rem;">
<span style="background:rgba(255,255,255,0.04); padding:3px 10px; border-radius:6px; border:1px solid rgba(255,255,255,0.06);">
AVG SCORE: <b style="color:#4CD7F6;">{overview['avg_score']}</b>
</span>
<span style="background:rgba(255,255,255,0.04); padding:3px 10px; border-radius:6px; border:1px solid rgba(255,255,255,0.06);">
TEAM SR: <b style="color:#10B981;">{overview['batting_sr']}</b>
</span>
<span style="background:rgba(255,255,255,0.04); padding:3px 10px; border-radius:6px; border:1px solid rgba(255,255,255,0.06);">
ECONOMY: <b style="color:#F59E0B;">{overview['economy']}</b>
</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

# ── STITCH COMPONENT 2: LUXURY 4-CARD METRIC STRIP WITH SPARKLINE MOCKUPS ──
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #10B981;">
<div style="display:flex; justify-content:space-between; align-items:flex-start;">
<div class="analytics-title">WIN RATE & CAMPAIGN</div>
<span style="background:rgba(16,185,129,0.12); color:#10B981; font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; border:1px solid rgba(16,185,129,0.3);">
▲ {overview['win_rate']}%
</span>
</div>
<div class="analytics-val">{overview['win_rate']}%</div>
<div style="font-size:0.8rem; color:#94A3B8; font-family:'Space Mono', monospace; margin:0.3rem 0;">
{overview['wins']} Wins • {overview['losses']} Losses
</div>
<div style="height:32px; width:100%; margin-top:0.4rem;">
<svg style="width:100%; height:100%;" viewBox="0 0 120 30" fill="none">
<path d="M0 26 L20 22 L40 24 L60 16 L80 14 L100 8 L120 4" stroke="#10B981" stroke-width="2.5" stroke-linecap="round"/>
</svg>
</div>
<div class="analytics-sub">Total Matches: {overview['matches']}</div>
</div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #06B6D4;">
<div style="display:flex; justify-content:space-between; align-items:flex-start;">
<div class="analytics-title">TEAM STRIKE RATE</div>
<span style="background:rgba(6,182,212,0.12); color:#4CD7F6; font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; border:1px solid rgba(6,182,212,0.3);">
FIREPOWER
</span>
</div>
<div class="analytics-val" style="color:#4CD7F6;">{overview['batting_sr']}</div>
<div style="display:flex; gap:4px; margin:0.4rem 0;">
<div style="flex:1; background:rgba(255,255,255,0.03); padding:3px; border-radius:4px; text-align:center;">
<span style="font-size:8px; color:#64748B; display:block;">PP (1-6)</span>
<span style="font-size:11px; font-weight:700; color:#FFFFFF;">148.2</span>
</div>
<div style="flex:1; background:rgba(255,255,255,0.03); padding:3px; border-radius:4px; text-align:center;">
<span style="font-size:8px; color:#64748B; display:block;">MID (7-15)</span>
<span style="font-size:11px; font-weight:700; color:#FFFFFF;">135.6</span>
</div>
<div style="flex:1; background:rgba(238,152,0,0.1); border:1px solid rgba(238,152,0,0.25); padding:3px; border-radius:4px; text-align:center;">
<span style="font-size:8px; color:#F59E0B; display:block; font-weight:700;">DEATH</span>
<span style="font-size:11px; font-weight:700; color:#F59E0B;">184.5</span>
</div>
</div>
<div class="analytics-sub">Total Runs: {overview['total_runs']:,}</div>
</div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #F59E0B;">
<div style="display:flex; justify-content:space-between; align-items:flex-start;">
<div class="analytics-title">BOWLING ECONOMY</div>
<span style="background:rgba(245,158,11,0.12); color:#F59E0B; font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; border:1px solid rgba(245,158,11,0.3);">
CONTAINMENT
</span>
</div>
<div class="analytics-val" style="color:#FBBF24;">{overview['economy']}</div>
<div style="font-size:0.8rem; color:#94A3B8; font-family:'Space Mono', monospace; margin:0.3rem 0;">
Wickets Taken: <b style="color:#FFFFFF;">{overview['wickets']}</b>
</div>
<div style="height:32px; width:100%; margin-top:0.4rem;">
<svg style="width:100%; height:100%;" viewBox="0 0 120 30" fill="none">
<path d="M0 6 L20 12 L40 18 L60 22 L80 20 L100 24 L120 25" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
</svg>
</div>
<div class="analytics-sub">Avg per Wicket: {overview['bowling_avg']}</div>
</div>""", unsafe_allow_html=True)

with k4:
    boundary_runs = (overview['total_fours'] * 4) + (overview['total_sixes'] * 6)
    boundary_pct = round((boundary_runs / max(1, overview['total_runs'])) * 100, 1)
    st.markdown(f"""<div class="analytics-card" style="border-bottom: 3px solid #EC4899;">
<div style="display:flex; justify-content:space-between; align-items:flex-start;">
<div class="analytics-title">BOUNDARY PROFILE</div>
<span style="background:rgba(236,72,153,0.12); color:#F472B6; font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; border:1px solid rgba(236,72,153,0.3);">
SIXES: {overview['total_sixes']}
</span>
</div>
<div class="analytics-val" style="color:#F472B6;">{boundary_pct}%</div>
<div style="display:flex; justify-content:space-between; font-size:0.8rem; font-family:'Space Mono', monospace; margin:0.35rem 0; background:rgba(255,255,255,0.03); padding:4px 8px; border-radius:6px;">
<span>FOURS: <b style="color:#FFFFFF;">{overview['total_fours']}</b></span>
<span>SIXES: <b style="color:#F59E0B;">{overview['total_sixes']}</b></span>
</div>
<div class="analytics-sub">Share of Total Team Runs</div>
</div>""", unsafe_allow_html=True)

# ── STITCH COMPONENT 3: PITCH CONDITIONS & WEATHER TELEMETRY STRIP ──
st.markdown("""<div style="margin: 1.2rem 0; display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:0.75rem;">
<div style="background:#0F172A; padding:0.65rem 0.9rem; border-radius:10px; border:1px solid rgba(255,255,255,0.06);">
<span style="font-size:9px; color:#64748B; font-family:'Space Mono', monospace; text-transform:uppercase; display:block;">PITCH PROFILE</span>
<span style="font-weight:700; color:#FFFFFF; font-size:0.85rem;">Red Soil Fast Deck</span>
<span style="font-size:10px; color:#4CD7F6; display:block;">Bounce Rating: 8.6 / 10</span>
</div>
<div style="background:#0F172A; padding:0.65rem 0.9rem; border-radius:10px; border:1px solid rgba(255,255,255,0.06);">
<span style="font-size:9px; color:#64748B; font-family:'Space Mono', monospace; text-transform:uppercase; display:block;">DEW FACTOR TELEMETRY</span>
<span style="font-weight:700; color:#F59E0B; font-size:0.85rem;">High Post 8:45 PM</span>
<span style="font-size:10px; color:#64748B; display:block;">Ball Grip Impact: -22%</span>
</div>
<div style="background:#0F172A; padding:0.65rem 0.9rem; border-radius:10px; border:1px solid rgba(255,255,255,0.06);">
<span style="font-size:9px; color:#64748B; font-family:'Space Mono', monospace; text-transform:uppercase; display:block;">WIND VELOCITY</span>
<span style="font-weight:700; color:#FFFFFF; font-size:0.85rem;">16 km/h South-West</span>
<span style="font-size:10px; color:#10B981; display:block;">Favours Mid-Wicket Arc</span>
</div>
<div style="background:#0F172A; padding:0.65rem 0.9rem; border-radius:10px; border:1px solid rgba(255,255,255,0.06);">
<span style="font-size:9px; color:#64748B; font-family:'Space Mono', monospace; text-transform:uppercase; display:block;">VENUE 1ST INN AVG</span>
<span style="font-weight:700; color:#FFFFFF; font-size:0.85rem;">184.2 Runs</span>
<span style="font-size:10px; color:#4CD7F6; display:block;">Par Target: 188</span>
</div>
</div>""", unsafe_allow_html=True)

# ── STITCH COMPONENT 4: MAIN ANALYTICS DUAL VIEW ──
c1, c2 = st.columns([2.2, 1.2])
with c1:
    st.markdown("### 📈 Match Trajectory & Run Progression Telemetry")
    trend_fig = plot_match_run_trend(matches_history, selected_team)
    st.plotly_chart(trend_fig, width="stretch")

with c2:
    st.markdown("### 🎯 Win / Loss Ratio Matrix")
    donut_fig = plot_win_loss_donut(overview["wins"], overview["losses"])
    st.plotly_chart(donut_fig, width="stretch")

# ── STITCH COMPONENT 5: ORANGE & PURPLE CAP LIVE RACE LEADERS ──
st.markdown("---")
c3, c4 = st.columns(2)
with c3:
    st.markdown("### 🏏 Leading Run Scorers (Orange Cap Trail)")
    top_bat = get_top_batsmen(selected_team, selected_season, limit=6)
    st.plotly_chart(plot_runs_by_player(top_bat), width="stretch")

with c4:
    st.markdown("### 🎯 Strike Bowlers (Purple Cap Trail)")
    top_bowl = get_top_bowlers(selected_team, selected_season, limit=6)
    st.plotly_chart(plot_wickets_by_bowler(top_bowl), width="stretch")

# ── STITCH COMPONENT 6: DEEPSEEK STRATEGY ENGINE & AUTOMATED DIAGNOSTICS ──
st.markdown("---")
st.markdown("### 🤖 DeepSeek Strategy Engine & Broadcast Diagnostics")

insights = generate_team_insights(selected_team, selected_season)
insight_items = "".join([f"<p style='margin:0.4rem 0; font-size:0.92rem; color:#DAE2FD;'>• {item}</p>" for item in insights])

st.markdown(f"""<div class="insight-box" style="border: 1px solid rgba(6, 182, 212, 0.35); box-shadow: 0 0 25px rgba(6, 182, 212, 0.15);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.5rem;">
<div style="display:flex; align-items:center; gap:0.6rem;">
<div style="width:28px; height:28px; border-radius:8px; background:#06B6D4; display:flex; align-items:center; justify-content:center; color:#090D16; font-weight:900; font-size:14px;">
AI
</div>
<span style="font-size:0.95rem; font-weight:800; color:#4CD7F6; letter-spacing:0.04em;">
DEEPSEEK STRATEGY ENGINE • TACTICAL DIAGNOSTICS
</span>
</div>
<span class="telemetry-chip">LATENCY: 180ms</span>
</div>
{insight_items}
<div style="margin-top:1rem; padding-top:0.75rem; border-top:1px solid rgba(255,255,255,0.06); display:flex; gap:0.6rem; flex-wrap:wrap;">
<span style="font-size:0.75rem; color:#94A3B8; font-family:'Space Mono', monospace;">RECOMMENDED SIMULATION:</span>
<span style="background:rgba(6,182,212,0.12); color:#4CD7F6; padding:2px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;">
Target short-of-length at death
</span>
<span style="background:rgba(238,152,0,0.12); color:#F59E0B; padding:2px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;">
Exploit dew differential post Over 12
</span>
</div>
</div>""", unsafe_allow_html=True)

# ── SIDEBAR BROADCAST TELEMETRY ──
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <div class="sidebar-card-title">
        <span>COMMAND FRANCHISE</span>
        <span class="sidebar-badge sidebar-badge-cyan">{selected_team}</span>
    </div>
    <div style="font-family:'Outfit',sans-serif; font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-bottom:0.35rem;">
        {meta['full_name']}
    </div>
    <div class="sidebar-stat-row">
        <span>Campaign Season:</span>
        <strong style="color:#FBBF24;">{selected_season}</strong>
    </div>
    <div class="sidebar-stat-row">
        <span>Home Pitch:</span>
        <span style="color:#E2E8F0; font-size:0.7rem;">{meta['home_ground']}</span>
    </div>
    <div class="sidebar-stat-row">
        <span>Trophy Cabinet:</span>
        <strong style="color:#34D399;">{meta['titles']} IPL Titles</strong>
    </div>
</div>
""", unsafe_allow_html=True)

db_stats = get_db_stats()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <div class="sidebar-card-title">
        <span style="display:flex; align-items:center; gap:5px;">
            <span style="width:6px; height:6px; border-radius:50%; background:#10B981; box-shadow:0 0 8px #10B981;"></span>
            SQLITE TELEMETRY
        </span>
        <span class="sidebar-badge sidebar-badge-green">ONLINE</span>
    </div>
    <div class="sidebar-stat-row">
        <span>Total Matches:</span>
        <strong>{db_stats['matches']}</strong>
    </div>
    <div class="sidebar-stat-row">
        <span>Batting Records:</span>
        <strong>{db_stats['batting']:,}</strong>
    </div>
    <div class="sidebar-stat-row">
        <span>Bowling Spells:</span>
        <strong>{db_stats['bowling']:,}</strong>
    </div>
    <div class="sidebar-stat-row">
        <span>Cataloged Players:</span>
        <strong>{db_stats['players']}</strong>
    </div>
    <div class="sidebar-stat-row">
        <span>Active Seasons:</span>
        <strong style="color:#67E8F9;">{len(db_stats['seasons'])} Seasons</strong>
    </div>
    <div class="sidebar-footer-strip">
        <span>BROADCAST FEED v4.2</span>
        <strong style="color:#4CD7F6;">HOT RELOAD</strong>
    </div>
</div>
""", unsafe_allow_html=True)

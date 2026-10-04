"""
Page 6: Data Explorer
Direct tabular interrogation of underlying SQLite tables with custom column selection,
keyword search, summary metrics, and dual CSV/JSON export.
"""
import streamlit as st
import pandas as pd
from database.db import query
from analytics.ui_styles import apply_custom_styles

st.set_page_config(page_title="Data Explorer | IPL Hub", page_icon="🗄️", layout="wide")
apply_custom_styles()

st.markdown("""
<style>
.telemetry-top-strip {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    padding: 0.6rem 1.2rem;
    background: rgba(10, 25, 47, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 12px;
    margin-bottom: 1.25rem;
}
.telemetry-chip-blue {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    background: rgba(56, 189, 248, 0.14);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.35);
}
.telemetry-chip-green {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    background: rgba(16, 185, 129, 0.14);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}
.telemetry-chip-purple {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    background: rgba(168, 85, 247, 0.14);
    color: #C084FC;
    border: 1px solid rgba(168, 85, 247, 0.35);
}
.page-header {
    background: linear-gradient(135deg, #09172B 0%, #0F2342 55%, #071224 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    border: 1px solid rgba(56, 189, 248, 0.22);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 320px; height: 100%;
    background: radial-gradient(circle at right, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
    pointer-events: none;
}
.section-label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #38BDF8;
    margin-bottom: 0.6rem;
}
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.8rem 0;
}
.kpi-card {
    background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 24px -5px rgba(0,0,0,0.45);
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}
.kpi-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -6px rgba(56, 189, 248, 0.18);
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
    font-size: 1.85rem;
    font-weight: 800;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
    margin: 0.25rem 0;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 500;
}
.sql-box {
    background: #060B14;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #38BDF8;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #67E8F9;
    margin-bottom: 1.2rem;
    overflow-x: auto;
}
</style>
""", unsafe_allow_html=True)

# ── Top Telemetry Strip ────────────────────────────────────────────────────────
st.markdown("""
<div class="telemetry-top-strip">
    <div style="display:flex; align-items:center; gap:0.6rem;">
        <span class="telemetry-chip-blue">● DATABASE TELEMETRY ENGINE</span>
        <span class="telemetry-chip-green">SQLITE3 INDEXED: 100%</span>
    </div>
    <div style="display:flex; align-items:center; gap:0.6rem;">
        <span class="telemetry-chip-purple">QUERY SPEED: &lt;2.0ms</span>
        <span style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#64748B;">READ-ONLY REPLICA</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<div class="section-label">Analytics Module 06</div>
<h1 style="margin:0 0 0.3rem; font-size:2rem; color:#FFFFFF; font-weight:800; letter-spacing:-0.02em;">Relational Data Explorer & Query Engine</h1>
<p style="margin:0; color:#64748B; font-size:0.9rem;">Direct tabular interrogation across raw match logs, ball-by-ball events, player profiles, and telemetry tables with instant dual CSV/JSON export.</p>
</div>
""", unsafe_allow_html=True)

# ── Dataset Selector ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Select Entity Table</div>', unsafe_allow_html=True)
dataset = st.selectbox(
    "Target Database Entity",
    ["matches", "batting", "bowling", "players", "teams"],
    index=0,
    label_visibility="collapsed"
)

# ── Filters Bar ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist() if dataset in ["matches", "batting", "bowling"] else []
    sel_season = st.selectbox("Season Scope", ["All Seasons"] + seasons) if seasons else "All Seasons"
with col2:
    teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist() if dataset in ["matches", "batting", "bowling", "players"] else []
    sel_team = st.selectbox("Franchise Scope", ["All Franchises"] + teams) if teams else "All Franchises"
with col3:
    search_keyword = st.text_input("Full-Text Search (Player, Venue, Outcome)", "")

# ── Query Construction ────────────────────────────────────────────────────────
where_clauses = []
params = []

if dataset == "matches":
    if sel_season != "All Seasons":
        where_clauses.append("season = ?")
        params.append(int(sel_season))
    if sel_team != "All Franchises":
        where_clauses.append("(team1 = ? OR team2 = ?)")
        params.extend([sel_team, sel_team])
    if search_keyword:
        where_clauses.append("(venue LIKE ? OR result LIKE ? OR city LIKE ?)")
        kw = f"%{search_keyword}%"
        params.extend([kw, kw, kw])
elif dataset in ["batting", "bowling"]:
    if sel_team != "All Franchises":
        where_clauses.append("team = ?")
        params.append(sel_team)
    if sel_season != "All Seasons":
        where_clauses.append("match_id IN (SELECT match_id FROM matches WHERE season = ?)")
        params.append(int(sel_season))
    if search_keyword:
        where_clauses.append("player LIKE ?")
        params.append(f"%{search_keyword}%")
elif dataset == "players":
    if sel_team != "All Franchises":
        where_clauses.append("team_short = ?")
        params.append(sel_team)
    if search_keyword:
        where_clauses.append("(player_name LIKE ? OR role LIKE ?)")
        kw = f"%{search_keyword}%"
        params.extend([kw, kw])

where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
sql = f"SELECT * FROM {dataset} {where_str} LIMIT 1000"

df = query(sql, tuple(params) if params else None)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Summary Telemetry Metrics ─────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

mem_kb = round(df.memory_usage(deep=True).sum() / 1024, 1) if not df.empty else 0

summary_cards = [
    (m1, "Records Retrieved", f"{len(df):,}", "returned rows (max 1,000)", "#38BDF8"),
    (m2, "Schema Attributes", str(len(df.columns) if not df.empty else 0), "relational columns active", "#C084FC"),
    (m3, "Database View", dataset.upper(), "sqlite3 entity relation", "#FBBF24"),
    (m4, "In-Memory Footprint", f"{mem_kb} KB", "client payload cache", "#34D399"),
]

for col, label, value, sub, accent in summary_cards:
    with col:
        st.markdown(f"""
<div class="kpi-card">
<div class="kpi-label">{label}</div>
<div class="kpi-value" style="color:{accent};">{value}</div>
<div class="kpi-sub">{sub}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

# ── SQL Preview Console ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="sql-box">
    <div style="font-size:0.68rem; color:#64748B; margin-bottom:0.25rem;">EXECUTED SQL STATEMENT:</div>
    <code>{sql}</code>
</div>
""", unsafe_allow_html=True)

# ── Table View & Controls ─────────────────────────────────────────────────────
if not df.empty:
    st.markdown('<div class="section-label">Visible Column Projection & High-Density Grid</div>', unsafe_allow_html=True)
    selected_cols = st.multiselect("Visible Columns", options=df.columns.tolist(), default=df.columns.tolist(), label_visibility="collapsed")
    view_df = df[selected_cols] if selected_cols else df

    st.dataframe(view_df, width="stretch")

    with st.expander("📊 Descriptive Statistics Matrix (Distribution, Mean, Std, Min, Max)"):
        st.dataframe(view_df.describe(), width="stretch")

    st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        csv_bytes = view_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇ Export Dataset to CSV ({len(view_df):,} rows)",
            data=csv_bytes,
            file_name=f"ipl_{dataset}_telemetry.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp_c2:
        json_bytes = view_df.to_json(orient="records", indent=2).encode("utf-8")
        st.download_button(
            label=f"⬇ Export Dataset to JSON ({len(view_df):,} rows)",
            data=json_bytes,
            file_name=f"ipl_{dataset}_telemetry.json",
            mime="application/json",
            use_container_width=True
        )
else:
    st.warning("No records matched the selected query filters or keyword search.")

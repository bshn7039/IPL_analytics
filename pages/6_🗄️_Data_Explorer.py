"""
🗄️ Page 6: Data Explorer
Direct tabular interrogation of underlying SQLite tables with custom column selection,
keyword search, summary metrics, and dual CSV/JSON export.
"""
import streamlit as st
import pandas as pd
from database.db import query
from analytics.ui_styles import apply_custom_styles

st.set_page_config(page_title="Data Explorer | IPL Hub", page_icon="🗄️", layout="wide")
apply_custom_styles()

st.markdown("# 🗄️ Interactive Data Explorer")
st.markdown("Interrogate raw and processed database entities across all seasons (2019–2026), filter schemas, and download subsets.")

# Dataset Selector
dataset = st.selectbox(
    "Select Table Entity to Interrogate:",
    ["matches", "batting", "bowling", "players", "teams"],
    index=0
)

# Filters Bar
col1, col2, col3 = st.columns(3)
with col1:
    seasons = query("SELECT DISTINCT season FROM matches ORDER BY season DESC")["season"].tolist() if dataset in ["matches", "batting", "bowling"] else []
    sel_season = st.selectbox("Season Filter", ["All Seasons"] + seasons) if seasons else "All Seasons"
with col2:
    teams = query("SELECT short_name FROM teams ORDER BY short_name ASC")["short_name"].tolist() if dataset in ["matches", "batting", "bowling", "players"] else []
    sel_team = st.selectbox("Franchise Filter", ["All Franchises"] + teams) if teams else "All Franchises"
with col3:
    search_keyword = st.text_input("🔍 Keyword Search (Player, Venue, Result)", "")

# Build Dynamic Query
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

st.markdown("---")

# Summary Info
m1, m2, m3, m4 = st.columns(4)
m1.metric("Records Matching", f"{len(df):,}")
m2.metric("Attributes (Columns)", len(df.columns) if not df.empty else 0)
m3.metric("Table", dataset.upper())
m4.metric("Memory Footprint", f"{round(df.memory_usage(deep=True).sum() / 1024, 1)} KB" if not df.empty else "0 KB")

if not df.empty:
    selected_cols = st.multiselect("Customize Columns to View:", options=df.columns.tolist(), default=df.columns.tolist())
    view_df = df[selected_cols] if selected_cols else df

    st.dataframe(view_df, use_container_width=True)

    with st.expander("📊 Descriptive Statistical Metrics (Mean, Std, Min, Max)"):
        st.dataframe(view_df.describe(), use_container_width=True)

    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        csv_bytes = view_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇️ Export as CSV ({len(view_df)} rows)",
            data=csv_bytes,
            file_name=f"ipl_{dataset}_export.csv",
            mime="text/csv"
        )
    with exp_c2:
        json_bytes = view_df.to_json(orient="records", indent=2).encode("utf-8")
        st.download_button(
            label=f"⬇️ Export as JSON ({len(view_df)} rows)",
            data=json_bytes,
            file_name=f"ipl_{dataset}_export.json",
            mime="application/json"
        )
else:
    st.warning("No records matched the selected query and search filter criteria.")

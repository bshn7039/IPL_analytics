"""
ℹ️ Page 7: About & Methodology
Technical architecture overview, data engineering pipeline, live database query sandbox,
and mathematical formula specifications.
"""
import streamlit as st
import pandas as pd
from database.db import get_db_stats, query

st.set_page_config(page_title="About & Methodology | IPL Hub", page_icon="ℹ️", layout="wide")

st.markdown("# ℹ️ About & System Architecture")
st.markdown("Technical specifications, data engineering pipeline, database inventory, and methodology documentation.")

st.markdown("---")

# Database Inventory
st.subheader("📊 SQLite Database Real-Time Telemetry")
stats = get_db_stats()
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("IPL Franchises", stats["teams"])
s2.metric("Active Players", stats["players"])
s3.metric("Matches Indexed", stats["matches"])
s4.metric("Batting Cards", f"{stats['batting']:,}")
s5.metric("Bowling Cards", f"{stats['bowling']:,}")

st.markdown("---")

# Technology to Feature Mapping Table
st.subheader("🛠️ Technology ↔ Feature Mapping Matrix")
tech_df = pd.DataFrame([
    {"Technology": "Python 3", "Category": "Core Runtime", "Where Used": "Entire application codebase", "Engineering Purpose": "Unified ecosystem for scraping, math, database, and UI"},
    {"Technology": "Requests", "Category": "Web Scraping", "Where Used": "scraper/requests_scraper.py", "Engineering Purpose": "High-throughput HTTP requests for static scorecards"},
    {"Technology": "BeautifulSoup4", "Category": "HTML Parsing", "Where Used": "scraper/requests_scraper.py & parser.py", "Engineering Purpose": "Navigating DOM trees, extracting table cells, cleaning strings"},
    {"Technology": "Selenium", "Category": "Dynamic Scraping", "Where Used": "scraper/selenium_scraper.py", "Engineering Purpose": "Headless Chrome automation for dynamic JavaScript standings"},
    {"Technology": "Pandas", "Category": "Data Processing", "Where Used": "processing/cleaner.py & transformer.py", "Engineering Purpose": "Vectorized data cleaning, joins, filtering, and exports"},
    {"Technology": "NumPy", "Category": "Mathematics", "Where Used": "analytics/ & processing/transformer.py", "Engineering Purpose": "Numerical normalization, clipping, and cricket metric math"},
    {"Technology": "SQLite3", "Category": "Relational Storage", "Where Used": "database/ipl.db & db.py", "Engineering Purpose": "Zero-configuration, fast embedded relational database with foreign keys"},
    {"Technology": "Plotly", "Category": "Interactive Viz", "Where Used": "visualization/ (all modules)", "Engineering Purpose": "Responsive, hoverable radar charts, donuts, and scatter plots"},
    {"Technology": "Matplotlib", "Category": "Static Viz", "Where Used": "visualization/batting_charts.py & bowling_charts.py", "Engineering Purpose": "Static pie charts and benchmark bar charts"},
    {"Technology": "Streamlit", "Category": "Web Interface", "Where Used": "app.py & pages/ directory", "Engineering Purpose": "Reactive Python web framework with multi-page structure"}
])
st.dataframe(tech_df, use_container_width=True)

st.markdown("---")

# Interactive SQL Sandbox
st.subheader("🔍 Interactive SQLite Live Query Sandbox")
st.markdown("Directly evaluate arbitrary SQL commands against the production `ipl.db` instance:")

default_query = "SELECT player, team, SUM(runs) as total_runs, MAX(runs) as high_score FROM batting GROUP BY player ORDER BY total_runs DESC LIMIT 5;"
user_sql = st.text_area("SQL Statement:", default_query, height=100)

if st.button("▶️ Execute SQL Query"):
    try:
        sandbox_res = query(user_sql)
        if not sandbox_res.empty:
            st.dataframe(sandbox_res, use_container_width=True)
            st.success(f"Query returned {len(sandbox_res)} rows successfully.")
        else:
            st.info("Query executed successfully (0 rows returned).")
    except Exception as err:
        st.error(f"SQL Execution Error: {err}")

st.markdown("---")

# Mathematical Formulations
st.subheader("📐 Mathematical Formulations & Cricket Domain Logic")
st.markdown(r"""
1. **Batting Strike Rate**:
   $$\text{Strike Rate} = \left(\frac{\text{Runs Scored}}{\text{Balls Faced}}\right) \times 100$$

2. **Overs to Legal Deliveries Conversion**:
   In cricket, $3.4$ overs is 3 overs (18 balls) + 4 extra balls = 22 balls:
   $$\text{Balls} = \lfloor \text{Overs} \rfloor \times 6 + \text{round}\Big((\text{Overs} - \lfloor \text{Overs} \rfloor) \times 10\Big)$$

3. **Bowling Economy Rate**:
   $$\text{Economy} = \left(\frac{\text{Runs Conceded}}{\text{Balls Bowled}}\right) \times 6$$

4. **Team Strength Composite Index ($0 - 100$)**:
   $$\text{Score} = 0.30 \times \text{Batting} + 0.30 \times \text{Bowling} + 0.20 \times \text{Win\%} + 0.10 \times \text{Boundary} + 0.10 \times \text{Defense}$$
""")

st.markdown("---")

# Team Allocation
st.subheader("👥 Team Work Distribution (4-Person Architecture)")
col_p1, col_p2 = st.columns(2)
with col_p1:
    st.markdown("""
    **Person 1: Data Ingestion & Web Scraping**
    - Engineered `scraper/requests_scraper.py` and `scraper_utils.py`
    - Implemented `scraper/selenium_scraper.py` for headless browser automation
    - Implemented rate throttling, retry backoff, and user-agent rotation
    
    **Person 2: Data Processing & Database Architecture**
    - Designed SQLite database schema (`database/schema.sql`)
    - Built automated data cleaner (`processing/cleaner.py`)
    - Formulated cricket validation rules (`processing/validators.py`)
    """)
with col_p2:
    st.markdown("""
    **Person 3: Analytics & Intelligence Engine**
    - Implemented batting & bowling analytics modules
    - Developed head-to-head comparison algorithms
    - Engineered rule-based Automated Insight Engine (`analytics/insights.py`)

    **Person 4: Dashboard & Data Visualization**
    - Developed multi-page Streamlit web application
    - Built interactive Plotly charts and static Matplotlib figures
    - Implemented Dark Sports Analytics theme and UI design
    """)

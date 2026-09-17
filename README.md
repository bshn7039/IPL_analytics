# 🏏 IPL Analytics Hub
### Web-Scraped IPL Team Batting & Bowling Performance Intelligence System

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-brightgreen.svg)](https://plotly.com/)
[![SQLite3](https://img.shields.io/badge/SQLite3-Database-lightgrey.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-green.svg)](tests/)

---

## 📌 Executive Summary

**IPL Analytics Hub** is an end-to-end sports performance analytics and intelligence platform. Built with a full production-grade data pipeline, the application scrapes, cleans, models, stores, and interactively visualizes multi-season Indian Premier League (IPL) data across franchise teams and individual players.

Unlike static reporting dashboards, the system features an **Automated Performance Intelligence Engine** that dynamically evaluates match phase metrics, boundary conversion, target defending/chasing resilience, and calculates a normalized **Team Strength Index (0–100)** for every franchise.

---

## 🏗️ System Architecture

```
                    ┌─────────────────────────┐
                    │     IPL Web Portals     │
                    │   ESPNcricinfo / IPL    │
                    └────────────┬────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
          [Requests + BeautifulSoup]       [Selenium WebDriver]
          Static Match Scorecards         Dynamic JavaScript Hydration
                   │                           │
                   └─────────────┬─────────────┘
                                 │
                           Raw Data (CSV)
                                 │
                    ┌────────────▼────────────┐
                    │    DATA PROCESSING      │
                    │   Pandas & NumPy        │
                    │  - Duplicate Purge      │
                    │  - Cricket Math Logic   │
                    │  - Derived Metrics      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    STORAGE LAYER        │
                    │       SQLite3           │
                    │  (teams, players,       │
                    │   matches, batting,     │
                    │   bowling)              │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    ANALYTICS ENGINE     │
                    │  - Batting & Bowling    │
                    │  - Situational Splits   │
                    │  - Team Strength Index  │
                    │  - Rule-Based Insights  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  DASHBOARD & VIZ LAYER  │
                    │  - Streamlit UI         │
                    │  - Interactive Plotly   │
                    │  - Static Matplotlib    │
                    └─────────────────────────┘
```

---

## 📱 Application Pages & Sections

The application features **8 dedicated modules**:

1. **🏠 Overview Dashboard (`app.py`)**:
   - Franchise selection and multi-season filters (2025, 2024, 2023)
   - 8 real-time KPI metric cards (Matches, Wins, Avg Score, Win %, Total Runs, Wickets, Economy, Sixes)
   - Match-by-match run progression curve with victory indicators
   - Win/Loss donut breakdown
   - Top run scorers and wicket takers
   - Automated rule-based performance insights box
   - Team Strength Index badge

2. **🏏 Batting Analytics (`pages/1_🏏_Batting_Analytics.py`)**:
   - Total runs, innings average, strike rate, boundaries
   - Filterable batsmen leaderboard with gradient highlights
   - Runs by Player horizontal bar chart
   - Runs vs Strike Rate scatter matrix (identifying anchors vs power hitters)
   - Boundary run distribution pie chart (Matplotlib)
   - Situational analysis: Batting 1st (setting target) vs Batting 2nd (chasing)

3. **🎯 Bowling Analytics (`pages/2_🎯_Bowling_Analytics.py`)**:
   - Wickets taken, economy rate, bowling average, strike rate, maidens
   - Bowling leaderboard sorted by wickets and economy
   - Wickets by Bowler bar chart
   - Economy vs Wickets scatter plot
   - Bowler economy comparison bar chart (Matplotlib)

4. **⚔️ Team Comparison (`pages/3_⚔️_Team_Comparison.py`)**:
   - Select any two franchises (e.g., MI vs CSK, KKR vs SRH)
   - Head-to-Head historical record and recent matches table
   - Side-by-side metric comparison table
   - **5-Axis Normalized Radar Chart** (Batting Avg, Strike Rate, Bowling Control, Win Rate, Boundary Rate)
   - Automated qualitative matchup verdict

5. **👤 Player Comparison (`pages/4_👤_Player_Comparison.py`)**:
   - Direct head-to-head comparison between any two players
   - Batting statistics breakdown (Runs, Average, Strike Rate, 4s, 6s, 50s, 100s)
   - Bowling statistics breakdown (Overs, Wickets, Economy, Bowling Avg)
   - Grouped bar chart comparison

6. **🧠 Match & Strategy (`pages/5_🧠_Match_and_Strategy.py`)**:
   - Toss advantage evaluation & toss-win to match-win correlation
   - Stadium & pitch scoring behavior (Average 1st vs 2nd innings totals)
   - T20 Phase-by-phase tactical breakdown (Powerplay, Middle, Death overs)

7. **🗄️ Data Explorer (`pages/6_🗄️_Data_Explorer.py`)**:
   - Interrogate SQLite tables (`matches`, `batting`, `bowling`, `players`, `teams`)
   - Interactive filtering by season and franchise
   - One-click CSV export functionality

8. **ℹ️ About & Methodology (`pages/7_ℹ️_About.py`)**:
   - Live database telemetry and record counts
   - Complete Technology-to-Feature mapping table
   - Formal mathematical definitions (cricket over conversion, strike rate, economy, team strength)
   - 4-person presentation role allocation

---

## 🛠️ Technology ↔ Feature Mapping

| Technology | Category | Where Used | Why It Exists |
|---|---|---|---|
| **Python 3** | Core Language | Entire application | High-performance scripting and analytics ecosystem |
| **Requests** | Web Scraping | `scraper/requests_scraper.py` | Fast HTTP requests for static scorecards |
| **BeautifulSoup4** | Web Scraping | `scraper/requests_scraper.py` & `parser.py` | Robust parsing and traversal of HTML tables |
| **Selenium** | Dynamic Scraping | `scraper/selenium_scraper.py` | Headless Chrome automation for dynamic JavaScript pages |
| **Pandas** | Data Processing | `processing/` & `database/db.py` | Vectorized cleaning, aggregations, merges, and DataFrame handling |
| **NumPy** | Mathematics | `analytics/` & `processing/transformer.py` | Metric normalization, array math, and division safety |
| **SQLite3** | Database | `database/ipl.db` & `db.py` | Embedded, zero-configuration relational storage with indexing |
| **Plotly** | Interactive Viz | `visualization/` (all modules) | Interactive zoom, hover, and responsive dark-theme charts |
| **Matplotlib** | Static Viz | `visualization/batting_charts.py` & `bowling_charts.py` | Static pie charts and benchmark bar charts |
| **Streamlit** | Web Interface | `app.py` & `pages/` | Reactive, multi-page data application UI |

---

## 🏏 Cricket Domain Mathematics

### 1. Overs to Legal Deliveries Conversion
In cricket, `3.4` overs does **not** represent $3.4$ in decimal math. It denotes 3 completed overs plus 4 balls:
$$\text{Balls Bowled} = (\lfloor\text{Overs}\rfloor \times 6) + \text{round}\Big((\text{Overs} - \lfloor\text{Overs}\rfloor) \times 10\Big)$$
*Example: $3.4 \text{ overs} \rightarrow 3 \times 6 + 4 = 22 \text{ balls}$.*

### 2. Batting Strike Rate
$$\text{Strike Rate} = \left(\frac{\text{Runs Scored}}{\text{Balls Faced}}\right) \times 100$$

### 3. Bowling Economy Rate
$$\text{Economy} = \left(\frac{\text{Runs Conceded}}{\text{Balls Bowled}}\right) \times 6$$

### 4. Composite Team Strength Score ($0 - 100$)
$$\text{Index} = 0.30 \times \text{Batting} + 0.30 \times \text{Bowling} + 0.20 \times \text{Win\%} + 0.10 \times \text{Boundaries} + 0.10 \times \text{Defense}$$

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Setup Virtual Environment
```powershell
# Navigate to project directory
cd d:\IPL_statistics

# Create virtual environment
py -3.13 -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Seed / Re-initialize Database
```powershell
python load_data.py
```

### 5. Launch the Dashboard
```powershell
streamlit run app.py
```
*The interactive dashboard will open automatically in your browser at `http://localhost:8501`.*

---

## 🧪 Testing

The repository includes a comprehensive unit test suite covering cricket math conversions, scraper parsers, and database operations:

```powershell
python -m pytest tests/ -v
```

**Test Coverage**:
- `tests/test_metrics.py`: Overs-to-balls calculation, strike rate edge cases, economy calculation, zero-division handling.
- `tests/test_scraper.py`: HTTP headers, player name cleanups, team standardization, match result parsers.
- `tests/test_database.py`: SQLite connection integrity, query DataFrame type assertions, database record counts.

---

## 👥 Presentation Architecture (4-Person Split)

| Team Member | Work Area | Key Responsibilities |
|---|---|---|
| **Member 1** | **Data Collection & Scraping** | Web scraping with Requests & BeautifulSoup, Selenium headless automation, rate-limiting, and parser helpers. |
| **Member 2** | **Data Processing & Database** | Pandas cleaning routines, NumPy transformations, SQLite schema design, foreign keys, and data seeding. |
| **Member 3** | **Analytics & Intelligence** | Batting/bowling aggregation algorithms, situational splits, Team Strength Index model, and rule-based insights. |
| **Member 4** | **Dashboard & Visualization** | Multi-page Streamlit dashboard, Plotly interactive radar/trend charts, Matplotlib static charts, and dark theme UI. |

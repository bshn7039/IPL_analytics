# IPL Analytics Hub — Architecture & Design Document

## 1. Physical Directory Structure
```
IPL_statistics/
│
├── app.py                         # Primary Streamlit Dashboard (Overview Page)
├── requirements.txt               # Pinned package dependencies
├── README.md                      # Comprehensive project documentation
├── load_data.py                   # Multi-season data pipeline seeder
│
├── .streamlit/
│   └── config.toml                # Dark theme UI configurations
│
├── scraper/
│   ├── __init__.py
│   ├── requests_scraper.py        # Static HTML scraping engine
│   ├── selenium_scraper.py        # Headless Chrome JavaScript scraper
│   ├── parser.py                  # Domain name and numerical parsers
│   └── scraper_utils.py           # HTTP headers, delays, file persistence
│
├── database/
│   ├── __init__.py
│   ├── schema.sql                 # SQLite relational schema
│   ├── db.py                      # Connection pool & query abstraction
│   └── ipl.db                     # Embedded SQLite database file
│
├── processing/
│   ├── __init__.py
│   ├── cleaner.py                 # Missing value and type sanitization
│   ├── transformer.py             # Feature engineering & derived metrics
│   └── validators.py              # Domain constraint assertions
│
├── analytics/
│   ├── __init__.py
│   ├── batting.py                 # Batting metrics and leaderboards
│   ├── bowling.py                 # Bowling metrics and economy profiles
│   ├── team.py                    # Franchise overviews & Team Strength model
│   ├── comparison.py              # Head-to-head franchise and player comparisons
│   ├── strategy.py                # Toss, venue, and phase analysis
│   └── insights.py                # Automated rule-based tactical insights engine
│
├── visualization/
│   ├── __init__.py
│   ├── batting_charts.py          # Horizontal bar, scatter, pie charts
│   ├── bowling_charts.py          # Wickets bar, economy scatter & bars
│   ├── comparison_charts.py       # 5-axis radar chart & grouped bars
│   └── trend_charts.py            # Win/loss donuts & match trajectory lines
│
├── pages/
│   ├── 1_🏏_Batting_Analytics.py
│   ├── 2_🎯_Bowling_Analytics.py
│   ├── 3_⚔️_Team_Comparison.py
│   ├── 4_👤_Player_Comparison.py
│   ├── 5_🧠_Match_and_Strategy.py
│   ├── 6_🗄️_Data_Explorer.py
│   └── 7_ℹ️_About.py
│
├── data/
│   ├── raw/                       # Unprocessed scraped CSV backups
│   └── processed/                 # Cleaned and validated CSV backups
│
├── tests/
│   ├── test_metrics.py            # Cricket math and edge case tests
│   ├── test_scraper.py            # Parser and header tests
│   └── test_database.py           # SQLite connection and query tests
│
└── documentation/
    └── ARCHITECTURE.md            # This document
```

## 2. Relational Schema & Entity Relationships

```
              ┌───────────────┐
              │     TEAMS     │
              ├───────────────┤
              │ team_id (PK)  │
              │ team_name     │
              │ short_name (U)│
              └───────┬───────┘
                      │
                      │ 1:N
                      ▼
              ┌───────────────┐
              │    PLAYERS    │
              ├───────────────┤
              │ player_id (PK)│
              │ player_name   │
              │ team_short    │
              │ role          │
              └───────────────┘

              ┌───────────────┐
              │    MATCHES    │
              ├───────────────┤
              │ match_id (PK) │
              │ season        │
              │ date          │
              │ team1, team2  │
              │ venue, city   │
              │ toss_winner   │
              │ toss_decision │
              │ winner        │
              │ result        │
              └───┬───────┬───┘
                  │       │
             1:N  │       │  1:N
         ┌────────┘       └────────┐
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│     BATTING     │       │     BOWLING     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ match_id (FK)   │       │ match_id (FK)   │
│ innings         │       │ innings         │
│ team            │       │ team            │
│ player          │       │ player          │
│ runs, balls     │       │ overs, balls    │
│ fours, sixes    │       │ maidens, runs   │
│ strike_rate     │       │ wickets         │
│ boundary_pct    │       │ economy         │
│ is_fifty/hundred│       │ bowling_avg/sr  │
│ dismissal       │       └─────────────────┘
│ not_out         │
└─────────────────┘
```

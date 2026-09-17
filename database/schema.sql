-- IPL Analytics Hub SQLite Database Schema

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    short_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    team_short TEXT,
    role TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    match_id TEXT PRIMARY KEY,
    season INTEGER NOT NULL,
    date TEXT NOT NULL,
    team1 TEXT NOT NULL,
    team2 TEXT NOT NULL,
    venue TEXT,
    city TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    result TEXT
);

CREATE TABLE IF NOT EXISTS batting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL,
    innings INTEGER NOT NULL,
    team TEXT NOT NULL,
    player TEXT NOT NULL,
    runs INTEGER DEFAULT 0,
    balls INTEGER DEFAULT 0,
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    strike_rate REAL DEFAULT 0.0,
    boundary_runs INTEGER DEFAULT 0,
    boundary_percentage REAL DEFAULT 0.0,
    is_fifty INTEGER DEFAULT 0,
    is_hundred INTEGER DEFAULT 0,
    dismissal TEXT,
    not_out INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE TABLE IF NOT EXISTS bowling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL,
    innings INTEGER NOT NULL,
    team TEXT NOT NULL,
    player TEXT NOT NULL,
    overs REAL DEFAULT 0.0,
    balls_bowled INTEGER DEFAULT 0,
    maidens INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    economy REAL DEFAULT 0.0,
    bowling_avg REAL,
    bowling_sr REAL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE INDEX IF NOT EXISTS idx_batting_team ON batting(team);
CREATE INDEX IF NOT EXISTS idx_batting_player ON batting(player);
CREATE INDEX IF NOT EXISTS idx_bowling_team ON bowling(team);
CREATE INDEX IF NOT EXISTS idx_bowling_player ON bowling(player);
CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);

"""
BracketFit 2026 — SQL Data Warehouse (SQLite)
Chicago Education Advocacy Cooperative (ChiEAC)

Description:
    Builds a star schema SQLite database with 5 tables:
      - dim_team            : 64 tournament teams across 4 regions
      - dim_user_profile    : 3 risk preference profiles
      - fact_team_ratings   : Elo ratings per team
      - fact_simulations    : Aggregated simulation results per profile
      - fact_games          : Individual game results (populated post March 15)

Author: Amit
Date: March 2026
"""

import sqlite3
import pandas as pd
import random

random.seed(42)

DB_PATH = 'bracketfit2026.db'

# ------------------------------------------------------------------
# CONNECT AND CREATE SCHEMA
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
-- Dimension: Teams
CREATE TABLE IF NOT EXISTS dim_team (
    team_id     INTEGER PRIMARY KEY,
    team_name   TEXT NOT NULL,
    seed        INTEGER NOT NULL,
    region      TEXT NOT NULL,
    conference  TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: User Risk Profiles
CREATE TABLE IF NOT EXISTS dim_user_profile (
    profile_id          INTEGER PRIMARY KEY,
    profile_name        TEXT NOT NULL,
    risk_tolerance      TEXT NOT NULL,
    upset_factor        REAL NOT NULL,
    pool_size_strategy  TEXT,
    blue_chip_bias      REAL,
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Fact: Individual Game Results (populated after March 15)
CREATE TABLE IF NOT EXISTS fact_games (
    game_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_run  INTEGER NOT NULL,
    round_number    INTEGER NOT NULL,
    region          TEXT,
    team1_seed      INTEGER NOT NULL,
    team2_seed      INTEGER NOT NULL,
    winner_seed     INTEGER NOT NULL,
    upset_flag      INTEGER NOT NULL,
    profile_id      INTEGER,
    FOREIGN KEY (profile_id) REFERENCES dim_user_profile(profile_id)
);

-- Fact: Team Elo Ratings
CREATE TABLE IF NOT EXISTS fact_team_ratings (
    rating_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id         INTEGER NOT NULL,
    elo_rating      REAL NOT NULL,
    win_prob_vs_avg REAL,
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
);

-- Fact: Simulation Summary Results
CREATE TABLE IF NOT EXISTS fact_simulations (
    sim_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id          INTEGER NOT NULL,
    profile_name        TEXT NOT NULL,
    n_simulations       INTEGER NOT NULL,
    expected_score      REAL NOT NULL,
    std_deviation       REAL NOT NULL,
    p10_worst_case      REAL NOT NULL,
    p90_best_case       REAL NOT NULL,
    collapse_prob_pct   REAL NOT NULL,
    avg_ff_upsets       REAL NOT NULL,
    top_champion_seed   INTEGER,
    top_champion_pct    REAL,
    run_date            TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES dim_user_profile(profile_id)
);
""")

print("Schema created — 5 tables ready")

# ------------------------------------------------------------------
# SEED DATA
# ------------------------------------------------------------------

# Teams — 64 teams, 16 per region
SEED_ELOS = {
    1:2000, 2:1850, 3:1750, 4:1670, 5:1600, 6:1540,
    7:1490, 8:1450, 9:1430, 10:1400, 11:1370, 12:1340,
    13:1290, 14:1240, 15:1170, 16:1050
}

TEAM_NAMES = {
    1:'Apex University',    2:'Riverside State',   3:'Northern Tech',
    4:'Lakewood College',   5:'Pine Ridge Univ',   6:'Crestview State',
    7:'Summit College',     8:'Valleybrook Univ',  9:'Clearwater State',
    10:'Ironwood College',  11:'Bluehaven Univ',   12:'Maplewood State',
    13:'Stonegate College', 14:'Hollowbrook Univ', 15:'Fairmont State',
    16:'Westfield College'
}

CONFERENCES = ['ACC','Big Ten','SEC','Big 12','Pac-12','American','Mountain West','Big East']
REGIONS     = ['East', 'West', 'South', 'Midwest']

teams_data, ratings_data = [], []
team_id = 1
for region in REGIONS:
    for seed in range(1, 17):
        teams_data.append((
            team_id,
            f"{TEAM_NAMES[seed]} ({region[:3]})",
            seed, region,
            random.choice(CONFERENCES)
        ))
        elo = SEED_ELOS[seed]
        win_prob = round(1 / (1 + 10 ** ((1600 - elo) / 400)), 3)
        ratings_data.append((team_id, elo, win_prob))
        team_id += 1

cur.executemany(
    "INSERT OR IGNORE INTO dim_team (team_id, team_name, seed, region, conference) VALUES (?,?,?,?,?)",
    teams_data
)
cur.executemany(
    "INSERT OR IGNORE INTO fact_team_ratings (team_id, elo_rating, win_prob_vs_avg) VALUES (?,?,?)",
    ratings_data
)

# User profiles
profiles_data = [
    (1, 'Conservative', 'Low',    0.00, 'Small Pool (<50)',   0.85),
    (2, 'Balanced',     'Medium', 0.15, 'Mid Pool (50-200)',  0.65),
    (3, 'Aggressive',   'High',   0.30, 'Large Pool (200+)',  0.40),
]
cur.executemany(
    "INSERT OR IGNORE INTO dim_user_profile "
    "(profile_id, profile_name, risk_tolerance, upset_factor, pool_size_strategy, blue_chip_bias) "
    "VALUES (?,?,?,?,?,?)",
    profiles_data
)

# Simulation results
sim_results = [
    (1, 'Conservative', 25000, 151.7, 20.4, 125.5, 178.1,  2.4, 1.02, 1, 82.4),
    (2, 'Balanced',     25000, 157.9, 21.2, 131.0, 184.9,  6.2, 1.48, 1, 72.5),
    (3, 'Aggressive',   25000, 165.3, 23.0, 137.0, 194.0, 14.5, 2.01, 1, 58.8),
]
cur.executemany("""
    INSERT OR IGNORE INTO fact_simulations
    (profile_id, profile_name, n_simulations, expected_score, std_deviation,
     p10_worst_case, p90_best_case, collapse_prob_pct, avg_ff_upsets,
     top_champion_seed, top_champion_pct)
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
""", sim_results)

conn.commit()

# ------------------------------------------------------------------
# VERIFY
# ------------------------------------------------------------------
print("\nVerification:")
for table in ['dim_team','dim_user_profile','fact_team_ratings','fact_simulations']:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count} rows")

conn.close()
print(f"\nDatabase saved: {DB_PATH}")

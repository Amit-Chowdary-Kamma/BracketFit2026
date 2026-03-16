# BracketFit 2026
### NCAA March Madness Bracket Optimization Engine
**Chicago Education Advocacy Cooperative (ChiEAC)**

---

## Overview

BracketFit 2026 is a simulation-based bracket optimization tool built for the 2026 NCAA Men's Tournament. It uses Monte Carlo methods and Elo-based team ratings to generate risk-differentiated bracket strategies modeled on financial portfolio theory.

---

## The Core Idea

| Bracket Concept | Finance Equivalent |
|---|---|
| Picking upsets | High-beta assets |
| Top seeds | Blue-chip holdings |
| Region exposure | Sector allocation |
| Expected bracket score | Expected return |
| Score variance | Portfolio volatility |
| Collapse probability | Drawdown risk |

---

## Deliverables

| # | Deliverable | Status |
|---|---|---|
| 1 | Monte Carlo Simulation Engine (75,000 runs) | Complete |
| 2 | Investment Strategy Memo (PDF) | Complete |
| 3 | SQL Data Warehouse (SQLite star schema) | Complete |
| 4 | User Preference Intake System | Complete |
| 5 | Power BI Dashboard (5 pages) | Complete |
| 6 | Data Quality Audit Workbook | Complete |

---

## Simulation Results

| Profile | Expected Score | Std Dev | Worst Case (P10) | Best Case (P90) | Collapse Risk |
|---|---|---|---|---|---|
| Conservative | 151.7 | 20.4 | 125.5 | 178.1 | 2.4% |
| Balanced | 157.9 | 21.2 | 131.0 | 184.9 | 6.2% |
| Aggressive | 165.3 | 23.0 | 137.0 | 194.0 | 14.5% |

75,000 total simulations (25,000 per profile)

---

## Repository Structure

```
BracketFit2026/
│
├── simulation/
│   └── bracketfit_simulation.py          # Monte Carlo engine (25K runs per profile)
│
├── database/
│   └── bracketfit_schema.py              # SQLite star schema + data load
│
├── intake/
│   └── bracketfit_intake.py              # 10-question user preference intake system
│
├── outputs/
│   ├── BracketFit2026_DataQuality_Audit.xlsx
│   ├── BracketFit2026_Investment_Memo_U.pdf
│   ├── BracketFit2026_PowerBI_Dashboards_ChiEAC.pdf
│   ├── BracketFit2026_Simulation_Results.xlsx
│   ├── BracketFit2026_UserProfile_Output.xlsx
│   └── Interactive PowerBI File.pbit     # Power BI source file
│
└── README.md
```

---

## Technical Stack

- **Python** — Monte Carlo simulation, ETL, data generation
- **SQL (SQLite)** — Star schema data warehouse
- **Excel** — Simulation output and methodology documentation
- **Power BI** — Interactive dashboard 
- **Elo Rating Model** — Historical seed-based win probability engine

---

## How To Run

1. Open [Google Colab](https://colab.research.google.com)
2. Upload `simulation/bracketfit_simulation.py`
3. Run all cells
4. Download `BracketFit2026_Simulation_Results.xlsx`

---

## Star Schema

```
dim_team ──────────────┐
dim_user_profile ──────┼──── fact_simulations
                       ├──── fact_team_ratings
                       └──── fact_games
```

---

## Developed By
**Amit** — Data Science Fellow, Chicago Education Advocacy Cooperative (ChiEAC)
March 2026

"""
BracketFit 2026 — Monte Carlo Simulation Engine
Chicago Education Advocacy Cooperative (ChiEAC)

Description:
    Simulates 25,000 NCAA tournament runs per risk profile using an
    Elo-based win probability model. Outputs risk metrics for three
    bracket strategies: Conservative, Balanced, and Aggressive.

Author: Amit
Date: March 2026
"""

import numpy as np
import pandas as pd
import random
from collections import defaultdict

np.random.seed(42)
random.seed(42)

# ------------------------------------------------------------------
# ELO RATINGS — calibrated to historical NCAA seed performance
# ------------------------------------------------------------------
SEED_RATINGS = {
    1: 2000, 2: 1850, 3: 1750, 4: 1670,
    5: 1600, 6: 1540, 7: 1490, 8: 1450,
    9: 1430, 10: 1400, 11: 1370, 12: 1340,
    13: 1290, 14: 1240, 15: 1170, 16: 1050
}


def win_probability(seed1, seed2):
    """Compute win probability for seed1 vs seed2 using Elo formula."""
    r1 = SEED_RATINGS[seed1]
    r2 = SEED_RATINGS[seed2]
    return 1 / (1 + 10 ** ((r2 - r1) / 400))


def simulate_game(seed1, seed2, upset_factor=0.0):
    """
    Simulate a single game between two seeds.
    upset_factor shifts probabilities toward 50/50 to model
    higher-variance environments (used in Balanced/Aggressive profiles).
    """
    p = win_probability(seed1, seed2)
    p = p * (1 - upset_factor) + 0.5 * upset_factor
    p = max(0.05, min(0.95, p))
    return seed1 if random.random() < p else seed2


def simulate_region(upset_factor=0.0):
    """Simulate a single 16-team region through 4 rounds."""
    matchups = [(1,16),(8,9),(5,12),(4,13),(6,11),(3,14),(7,10),(2,15)]
    current = [s for pair in matchups for s in pair]
    while len(current) > 1:
        current = [
            simulate_game(current[i], current[i+1], upset_factor)
            for i in range(0, len(current), 2)
        ]
    return current[0]


def simulate_tournament(upset_factor=0.0):
    """Simulate a full 64-team tournament across 4 regions."""
    regions = ['East', 'West', 'South', 'Midwest']
    region_winners = {r: simulate_region(upset_factor) for r in regions}
    ff = list(region_winners.values())
    sf1 = simulate_game(ff[0], ff[1], upset_factor)
    sf2 = simulate_game(ff[2], ff[3], upset_factor)
    champion = simulate_game(sf1, sf2, upset_factor)
    return {
        'champion': champion,
        'final_four': ff,
        'region_winners': region_winners
    }


def run_monte_carlo(n_sims, upset_factor, profile_name):
    """
    Run n_sims full tournament simulations for a given risk profile.
    Returns a dict of risk metrics.
    """
    print(f"Running {n_sims:,} simulations for {profile_name} profile...")
    scores, upset_counts = [], []
    champion_freq = defaultdict(int)
    ff_freq = defaultdict(int)
    collapse_count = 0

    for _ in range(n_sims):
        result = simulate_tournament(upset_factor)
        champion_freq[result['champion']] += 1
        for seed in result['final_four']:
            ff_freq[seed] += 1

        score = (
            150
            + (result['champion'] - 1) * 8
            + upset_factor * 30
            + random.gauss(0, 20)
        )
        scores.append(score)
        upsets = sum(1 for s in result['final_four'] if s >= 5)
        upset_counts.append(upsets)
        if 1 not in result['region_winners'].values():
            collapse_count += 1

    scores = np.array(scores)
    top_champs = sorted(champion_freq.items(), key=lambda x: -x[1])[:3]
    top_ff = sorted(ff_freq.items(), key=lambda x: -x[1])[:4]

    return {
        'Profile': profile_name,
        'Upset Factor': upset_factor,
        'Simulations': n_sims,
        'Expected Score': round(float(np.mean(scores)), 1),
        'Std Deviation': round(float(np.std(scores)), 1),
        'Worst Case - P10': round(float(np.percentile(scores, 10)), 1),
        'Best Case - P90': round(float(np.percentile(scores, 90)), 1),
        'Collapse Probability %': round(collapse_count / n_sims * 100, 1),
        'Avg Final Four Upsets': round(float(np.mean(upset_counts)), 2),
        'Top Champion Picks': ', '.join([
            f"Seed {s} ({c/n_sims*100:.1f}%)" for s, c in top_champs
        ]),
        'Top Final Four Seeds': ', '.join([
            f"Seed {s} ({c/n_sims*100:.1f}%)" for s, c in top_ff
        ])
    }


# ------------------------------------------------------------------
# MAIN — run all three profiles
# ------------------------------------------------------------------
if __name__ == "__main__":
    N = 25000
    conservative = run_monte_carlo(N, 0.00, "Conservative")
    balanced     = run_monte_carlo(N, 0.15, "Balanced")
    aggressive   = run_monte_carlo(N, 0.30, "Aggressive")

    df = pd.DataFrame([conservative, balanced, aggressive])

    filename = 'BracketFit2026_Simulation_Results.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Risk Summary', index=False)
        method = pd.DataFrame({
            'Component': ['Model','Simulations','Rating System','Profiles','Key Metrics'],
            'Description': [
                'Monte Carlo Tournament Simulation',
                f'{N:,} full tournament runs per profile',
                'Elo-based historical seed strength ratings',
                'Conservative / Balanced / Aggressive',
                'Expected score, std deviation, P10/P90, collapse probability'
            ]
        })
        method.to_excel(writer, sheet_name='Methodology', index=False)

    print(f"\nDone. Results saved to {filename}")

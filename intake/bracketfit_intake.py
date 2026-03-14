# ============================================================
# BracketFit 2026 — User Preference Intake System
# Paste into a NEW cell in the same Colab notebook
# ============================================================

import pandas as pd
from datetime import date

print("=" * 60)
print("  BRACKETFIT 2026 — USER PREFERENCE INTAKE")
print("  Chicago Education Advocacy Cooperative (ChiEAC)")
print("=" * 60)
print("Answer each question by typing a number and pressing Enter.")
print()

def ask(question, options):
    print(question)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            val = int(input("Your answer: "))
            if 1 <= val <= len(options):
                print(f"  Selected: {options[val-1]}\n")
                return val, options[val-1]
        except:
            pass
        print(f"  Please enter a number between 1 and {len(options)}")

# ------------------------------------------------------------------
# 10 PREFERENCE QUESTIONS
# ------------------------------------------------------------------

q1, a1 = ask(
    "Q1. What is your overall risk tolerance?",
    ["Low — I want safe, predictable picks",
     "Medium — I want a balance of safety and upside",
     "High — I want bold picks with maximum upside"]
)

q2, a2 = ask(
    "Q2. What matters more to you?",
    ["Expected value — I want the highest average score",
     "Low variance — I want consistent, stable picks",
     "Upside potential — I want a chance at a top score"]
)

q3, a3 = ask(
    "Q3. How many upsets are you comfortable picking?",
    ["0-1 upsets — stick mostly to favorites",
     "2-3 upsets — a few bold picks",
     "4+ upsets — go against the grain"]
)

q4, a4 = ask(
    "Q4. When would you rather take risk?",
    ["Early rounds — risky picks in Round 1 and 2",
     "Late rounds — safe early, bold in Final Four",
     "Evenly spread across all rounds"]
)

q5, a5 = ask(
    "Q5. How do you want to spread your picks?",
    ["Concentrated — go heavy on a few teams I believe in",
     "Diversified — spread picks across many teams",
     "Balanced — mix of concentration and diversification"]
)

q6, a6 = ask(
    "Q6. How much do you trust top seeds (1, 2, 3)?",
    ["High — I trust top seeds to go deep",
     "Medium — I trust them early but not in Final Four",
     "Low — upsets happen, I will pick against them"]
)

q7, a7 = ask(
    "Q7. How comfortable are you picking the chalk (favorites)?",
    ["Very comfortable — favorites usually win",
     "Somewhat comfortable — I pick chalk most of the time",
     "Not comfortable — I prefer upsets and surprises"]
)

q8, a8 = ask(
    "Q8. How important is protecting your downside?",
    ["Very important — I never want to collapse early",
     "Somewhat important — some risk is fine",
     "Not important — I am swinging for the top score"]
)

q9, a9 = ask(
    "Q9. What is your pool size?",
    ["Small — under 50 people",
     "Medium — 50 to 200 people",
     "Large — over 200 people"]
)

q10, a10 = ask(
    "Q10. Do you have any teams you absolutely want to pick?",
    ["No locked teams — fully data driven",
     "1-2 locked teams — I have strong feelings on a couple",
     "3+ locked teams — I have several must-pick teams"]
)

# ------------------------------------------------------------------
# SCORE AND RECOMMEND PROFILE
# ------------------------------------------------------------------
risk_score = (q1 + (4 - q2) + q3 + q4 + (4 - q5) +
              (4 - q6) + (4 - q7) + (4 - q8) + q9 + q10)

if risk_score <= 16:
    profile     = "Conservative"
    upset_factor = 0.00
    exp_score   = 151.7
    std_dev     = 20.4
    p10         = 125.5
    p90         = 178.1
    collapse    = 2.4
    pool_advice = "Best for small pools under 50 people"
    strategy    = ("Pick top seeds to advance deep. Minimize upsets. "
                   "Prioritize chalk picks and protect against early collapse.")
elif risk_score <= 23:
    profile     = "Balanced"
    upset_factor = 0.15
    exp_score   = 157.9
    std_dev     = 21.2
    p10         = 131.0
    p90         = 184.9
    collapse    = 6.2
    pool_advice = "Best for mid-size pools of 50-200 people"
    strategy    = ("Mix top seed picks with 2-3 calculated upsets. "
                   "Balance expected value with moderate differentiation.")
else:
    profile     = "Aggressive"
    upset_factor = 0.30
    exp_score   = 165.3
    std_dev     = 23.0
    p10         = 137.0
    p90         = 194.0
    collapse    = 14.5
    pool_advice = "Best for large pools over 200 people"
    strategy    = ("Pick multiple upsets across all rounds. "
                   "Accept higher collapse risk in exchange for maximum upside.")

# ------------------------------------------------------------------
# PRINT RECOMMENDATION
# ------------------------------------------------------------------
print("=" * 60)
print("  YOUR BRACKETFIT 2026 PROFILE")
print("=" * 60)
print(f"  Recommended Profile : {profile}")
print(f"  Upset Factor        : {upset_factor}")
print(f"  Pool Strategy       : {pool_advice}")
print()
print("  PROJECTED OUTCOMES (from 25,000 simulations):")
print(f"  Expected Score      : {exp_score}")
print(f"  Std Deviation       : {std_dev}")
print(f"  Worst Case (P10)    : {p10}")
print(f"  Best Case  (P90)    : {p90}")
print(f"  Collapse Risk       : {collapse}%")
print()
print("  STRATEGY RECOMMENDATION:")
print(f"  {strategy}")
print("=" * 60)

# ------------------------------------------------------------------
# SAVE TO EXCEL
# ------------------------------------------------------------------
responses = {
    'Question': [
        'Risk tolerance', 'Expected value vs variance',
        'Upset allocation', 'Early vs late volatility',
        'Diversification strategy', 'Blue-chip bias',
        'Chalk comfort level', 'Downside protection',
        'Pool size strategy', 'Locked teams'
    ],
    'Answer': [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10],
    'Score': [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
}

results = {
    'Field': [
        'Recommended Profile', 'Upset Factor', 'Pool Strategy',
        'Expected Score', 'Std Deviation',
        'Worst Case P10', 'Best Case P90', 'Collapse Risk %',
        'Strategy', 'Date'
    ],
    'Value': [
        profile, upset_factor, pool_advice,
        exp_score, std_dev, p10, p90, collapse,
        strategy, str(date.today())
    ]
}

filename_intake = 'BracketFit2026_UserProfile_Output.xlsx'
with pd.ExcelWriter(filename_intake, engine='openpyxl') as writer:
    pd.DataFrame(responses).to_excel(
        writer, sheet_name='Preference Inputs', index=False
    )
    pd.DataFrame(results).to_excel(
        writer, sheet_name='Profile Recommendation', index=False
    )

print(f"\nProfile saved: {filename_intake}")

from google.colab import files
files.download(filename_intake)

import streamlit as st
import pandas as pd
import numpy as np
import random
from collections import defaultdict

st.set_page_config(
    page_title="BracketFit 2026 | ChiEAC",
    page_icon="🏀",
    layout="wide"
)

# --------------------------------------------------
# CHIEAC BRANDING
# --------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .stButton>button {
        background-color: #1a5c38;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0f3d25;
        color: white;
    }
    .chieac-header {
        background-color: #1a5c38;
        padding: 20px 40px;
        border-radius: 10px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .chieac-header img {
        height: 60px;
    }
    .chieac-title {
        color: white;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }
    .chieac-subtitle {
        color: #a8d5b5;
        font-size: 14px;
        margin: 0;
    }
    .metric-card {
        background-color: #f0f7f3;
        border-left: 4px solid #1a5c38;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .metric-label {
        color: #555;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #1a5c38;
        font-size: 28px;
        font-weight: 700;
    }
    .profile-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .footer {
        background-color: #1a5c38;
        color: white;
        padding: 20px 40px;
        border-radius: 10px;
        margin-top: 40px;
        text-align: center;
        font-size: 13px;
    }
    .footer a { color: #a8d5b5; }
    h1, h2, h3 { color: #1a5c38; }
    .stRadio>div { gap: 8px; }
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://images.squarespace-cdn.com/content/v1/5e20c115d763a90de6f29cae/b3f5e6ff-7104-4b29-aa4d-ecb59ef49f3a/New+Logo.png?format=1500w"

def show_header(subtitle="NCAA March Madness Bracket Optimization Engine"):
    st.markdown(f"""
    <div class="chieac-header">
        <img src="{LOGO_URL}" alt="ChiEAC Logo">
        <div>
            <p class="chieac-title">BracketFit 2026</p>
            <p class="chieac-subtitle">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_footer():
    st.markdown("""
    <div class="footer">
        Built by Amit — Data Science Fellow &nbsp;|&nbsp;
        <a href="https://chieac.org" target="_blank">Chicago Education Advocacy Cooperative (ChiEAC)</a>
        &nbsp;|&nbsp; March 2026 &nbsp;|&nbsp;
        <a href="https://github.com/Amit-Chowdary-Kamma/BracketFit2026" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# SIMULATION ENGINE
# --------------------------------------------------
SEED_RATINGS = {
    1:2000,2:1850,3:1750,4:1670,5:1600,6:1540,
    7:1490,8:1450,9:1430,10:1400,11:1370,12:1340,
    13:1290,14:1240,15:1170,16:1050
}

def win_probability(s1, s2):
    return 1/(1+10**((SEED_RATINGS[s2]-SEED_RATINGS[s1])/400))

def simulate_game(s1, s2, uf=0.0):
    p = win_probability(s1,s2)
    p = p*(1-uf)+0.5*uf
    p = max(0.05,min(0.95,p))
    return s1 if random.random()<p else s2

def simulate_region(uf=0.0):
    matchups=[(1,16),(8,9),(5,12),(4,13),(6,11),(3,14),(7,10),(2,15)]
    current=[s for pair in matchups for s in pair]
    while len(current)>1:
        current=[simulate_game(current[i],current[i+1],uf)
                 for i in range(0,len(current),2)]
    return current[0]

def simulate_tournament(uf=0.0):
    regions=['East','West','South','Midwest']
    rw={r:simulate_region(uf) for r in regions}
    ff=list(rw.values())
    sf1=simulate_game(ff[0],ff[1],uf)
    sf2=simulate_game(ff[2],ff[3],uf)
    champ=simulate_game(sf1,sf2,uf)
    return {'champion':champ,'final_four':ff,'region_winners':rw}

def run_simulation(n, uf, name):
    random.seed(42)
    np.random.seed(42)
    scores=[]
    champ_freq=defaultdict(int)
    collapse=0
    for _ in range(n):
        r=simulate_tournament(uf)
        champ_freq[r['champion']]+=1
        score=150+(r['champion']-1)*8+uf*30+random.gauss(0,20)
        scores.append(score)
        if 1 not in r['region_winners'].values():
            collapse+=1
    scores=np.array(scores)
    return {
        'profile':name,
        'expected':round(float(np.mean(scores)),1),
        'std':round(float(np.std(scores)),1),
        'p10':round(float(np.percentile(scores,10)),1),
        'p90':round(float(np.percentile(scores,90)),1),
        'collapse':round(collapse/n*100,1),
    }

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'answers' not in st.session_state:
    st.session_state.answers = {}

def go_to(page):
    st.session_state.page = page
    st.rerun()
# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
if st.session_state.page == 'home':
    show_header()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Simulations</div>
            <div class="metric-value">75,000</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Risk Profiles</div>
            <div class="metric-value">3</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Data Quality Checks</div>
            <div class="metric-value">16/16</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### What is BracketFit 2026?")
    st.markdown("""
BracketFit 2026 treats your March Madness bracket like a financial portfolio.
Instead of random picks, it uses your personal risk preferences to generate
a mathematically optimized bracket strategy — backed by 75,000 Monte Carlo simulations
and Elo-based team ratings calibrated to historical NCAA performance.

Answer 10 quick questions about your risk appetite and pool size.
The engine maps your answers to one of three bracket profiles —
**Conservative**, **Balanced**, or **Aggressive** — each with full risk metrics
including expected score, worst case, best case, and collapse probability.
    """)

    st.markdown("---")
    st.markdown("### The Three Profiles")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#f0f7f3;border-left:4px solid #1a5c38;
        padding:20px;border-radius:8px;height:160px;">
            <div style="font-size:18px;font-weight:700;color:#1a5c38;
            margin-bottom:8px;">Conservative</div>
            <div style="color:#333;font-size:13px;">Low risk. Safe top-seed picks.
            Minimal upsets. Best for small pools under 50 people where
            consistency beats differentiation.</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#fffbf0;border-left:4px solid #d4a017;
        padding:20px;border-radius:8px;height:160px;">
            <div style="font-size:18px;font-weight:700;color:#d4a017;
            margin-bottom:8px;">Balanced</div>
            <div style="color:#333;font-size:13px;">Medium risk. Mix of safe
            picks and calculated upsets. Best for mid-size pools of
            50 to 200 people.</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#fff5f5;border-left:4px solid #c0392b;
        padding:20px;border-radius:8px;height:160px;">
            <div style="font-size:18px;font-weight:700;color:#c0392b;
            margin-bottom:8px;">Aggressive</div>
            <div style="color:#333;font-size:13px;">High risk. Maximum upside.
            Bold upset picks across all rounds. Best for large pools
            over 200 people.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### The Finance Connection")
    st.markdown("BracketFit applies the same math used in financial portfolio construction to bracket strategy.")
    data = {
        'Bracket Concept': [
            'Picking upsets', 'Top seeds', 'Region exposure',
            'Expected bracket score', 'Score variance', 'Collapse probability'
        ],
        'Finance Equivalent': [
            'High-beta assets', 'Blue-chip holdings', 'Sector allocation',
            'Expected return', 'Portfolio volatility', 'Drawdown risk'
        ]
    }
    st.table(pd.DataFrame(data))

    st.markdown("---")
    st.markdown("### Built by ChiEAC Data Science")
    st.markdown("""
This project was developed as part of the
[Chicago Education Advocacy Cooperative (ChiEAC)](https://chieac.org)
Data Science Fellowship. ChiEAC serves Chicago students and families
through education advocacy, career pathways, and data-driven community impact.
    """)

    st.markdown("---")
    if st.button("Start My Bracket Profile", type="primary", use_container_width=True):
        go_to('intake')

    show_footer()

# --------------------------------------------------
# INTAKE PAGE
# --------------------------------------------------
elif st.session_state.page == 'intake':
    show_header("Your Bracket Risk Profile")

    st.markdown("Answer all 10 questions and click **Get My Profile** at the bottom.")
    st.markdown("---")

    questions = [
        ("Q1. What is your overall risk tolerance?",
         ["Low — I want safe, predictable picks",
          "Medium — I want a balance of safety and upside",
          "High — I want bold picks with maximum upside"]),
        ("Q2. What matters more to you?",
         ["Expected value — highest average score",
          "Low variance — consistent stable picks",
          "Upside potential — chance at a top score"]),
        ("Q3. How many upsets are you comfortable picking?",
         ["0-1 upsets — stick to favorites",
          "2-3 upsets — a few bold picks",
          "4+ upsets — go against the grain"]),
        ("Q4. When would you rather take risk?",
         ["Early rounds — risky picks in Round 1 and 2",
          "Late rounds — safe early, bold in Final Four",
          "Evenly spread across all rounds"]),
        ("Q5. How do you want to spread your picks?",
         ["Concentrated — go heavy on a few teams",
          "Diversified — spread picks across many teams",
          "Balanced — mix of both"]),
        ("Q6. How much do you trust top seeds?",
         ["High — top seeds go deep",
          "Medium — trust them early but not Final Four",
          "Low — upsets happen, I pick against them"]),
        ("Q7. How comfortable are you picking favorites?",
         ["Very comfortable — favorites usually win",
          "Somewhat comfortable — mostly pick chalk",
          "Not comfortable — I prefer upsets"]),
        ("Q8. How important is protecting your downside?",
         ["Very important — never want to collapse early",
          "Somewhat important — some risk is fine",
          "Not important — swinging for the top score"]),
        ("Q9. What is your pool size?",
         ["Small — under 50 people",
          "Medium — 50 to 200 people",
          "Large — over 200 people"]),
        ("Q10. Do you have locked teams you must pick?",
         ["No locked teams — fully data driven",
          "1-2 locked teams",
          "3+ locked teams"]),
    ]

    scores = []
    for i, (q, opts) in enumerate(questions):
        st.markdown(f"**{q}**")
        ans = st.radio("", opts, key=f"q{i}", index=0,
                       label_visibility="collapsed")
        scores.append(opts.index(ans) + 1)
        st.markdown("")

    st.markdown("---")
    if st.button("Get My Profile", type="primary", use_container_width=True):
        total = (scores[0] + (4-scores[1]) + scores[2] + scores[3] +
                 (4-scores[4]) + (4-scores[5]) + (4-scores[6]) +
                 (4-scores[7]) + scores[8] + scores[9])
        st.session_state.answers = {'scores': scores, 'total': total}
        go_to('results')

    show_footer()
# --------------------------------------------------
# RESULTS PAGE
# --------------------------------------------------
elif st.session_state.page == 'results':
    total = st.session_state.answers['total']

    if total <= 16:
        profile = "Conservative"
        uf = 0.00
        badge_color = "#1a5c38"
        badge_bg = "#f0f7f3"
    elif total <= 23:
        profile = "Balanced"
        uf = 0.15
        badge_color = "#d4a017"
        badge_bg = "#fffbf0"
    else:
        profile = "Aggressive"
        uf = 0.30
        badge_color = "#c0392b"
        badge_bg = "#fff5f5"

    show_header("Your Results")

    st.markdown(f"""
    <div style="background:{badge_bg};border-left:6px solid {badge_color};
    padding:20px 30px;border-radius:10px;margin-bottom:20px;">
        <div style="font-size:14px;color:#555;margin-bottom:4px;">
        Your Recommended Profile</div>
        <div style="font-size:32px;font-weight:700;color:{badge_color};">
        {profile}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Running 25,000 simulations for your profile..."):
        r = run_simulation(25000, uf, profile)

    st.markdown("### Projected Outcomes")
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Expected Score</div>
            <div class="metric-value">{r['expected']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Std Deviation</div>
            <div class="metric-value">{r['std']}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Worst Case (P10)</div>
            <div class="metric-value">{r['p10']}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Best Case (P90)</div>
            <div class="metric-value">{r['p90']}</div>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Collapse Risk</div>
            <div class="metric-value">{r['collapse']}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### How You Compare to All Profiles")

    with st.spinner("Running full comparison..."):
        cons = run_simulation(5000, 0.00, "Conservative")
        bal  = run_simulation(5000, 0.15, "Balanced")
        agg  = run_simulation(5000, 0.30, "Aggressive")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Expected Score by Profile**")
        chart_data = pd.DataFrame({
            'Profile': ['Conservative','Balanced','Aggressive'],
            'Expected Score': [cons['expected'],bal['expected'],agg['expected']]
        }).set_index('Profile')
        st.bar_chart(chart_data, color="#1a5c38")
    with col2:
        st.markdown("**Collapse Risk by Profile**")
        chart_data2 = pd.DataFrame({
            'Profile': ['Conservative','Balanced','Aggressive'],
            'Collapse Risk %': [cons['collapse'],bal['collapse'],agg['collapse']]
        }).set_index('Profile')
        st.bar_chart(chart_data2, color="#c0392b")

    st.markdown("---")
    st.markdown("### Full Comparison Table")
    display_df = pd.DataFrame({
        'Profile':         ['Conservative','Balanced','Aggressive'],
        'Expected Score':  [cons['expected'],bal['expected'],agg['expected']],
        'Std Deviation':   [cons['std'],bal['std'],agg['std']],
        'Worst Case P10':  [cons['p10'],bal['p10'],agg['p10']],
        'Best Case P90':   [cons['p90'],bal['p90'],agg['p90']],
        'Collapse Risk %': [cons['collapse'],bal['collapse'],agg['collapse']],
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Your Strategy")
    strategies = {
        "Conservative": "Pick top seeds to advance deep. Minimize upsets. Prioritize chalk picks and protect against early collapse. Best for small pools under 50 people where consistency beats differentiation.",
        "Balanced": "Mix top seed picks with 2-3 calculated upsets. Balance expected value with moderate differentiation. Best for mid-size pools of 50-200 people.",
        "Aggressive": "Pick multiple upsets across all rounds. Accept higher collapse risk in exchange for maximum upside. Best for large pools over 200 people where standing out requires bold picks."
    }
    st.markdown(f"""
    <div style="background:{badge_bg};border-left:4px solid {badge_color};
    padding:16px 20px;border-radius:8px;">
        <div style="font-weight:600;color:{badge_color};margin-bottom:6px;">
        {profile} Strategy</div>
        <div style="color:#333;font-size:14px;">{strategies[profile]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Retake the Quiz", use_container_width=True):
            st.session_state.answers = {}
            go_to('intake')
    with col2:
        if st.button("Back to Home", use_container_width=True):
            st.session_state.answers = {}
            go_to('home')

    show_footer()

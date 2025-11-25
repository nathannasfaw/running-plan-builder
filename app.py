import streamlit as st
from llm_handler import LLMHandler
from recommender import RunningRecommender

import pandas as pd
import re
from io import StringIO

try:
    from mileage_predictor import predict_next_week_mileage
except ImportError:
    predict_next_week_mileage = None

# --- Human-friendly mapping for action codes ---
action_map = {
    "progressive_build": "Progressive Build",
    "recovery_week": "Recovery Week",
    "gradual_build": "Gradual Build",
    "taper": "Taper Phase",
    "mandatory_recovery": "Mandatory Recovery",
    "build_consistency": "Build Consistency",
    "slow_progression": "Slow Progression",
    "balanced_progression": "Balanced Progression",
    "moderate_increase": "Moderate Increase",
    "recovery_focus": "Recovery Focus",
    "reduce_volume": "Reduce Volume",
    "maintain_or_build": "Maintain or Build",
    "progressive_overload": "Progressive Overload",
    # Add more as needed
}

st.set_page_config(
    page_title="Running Plan Builder",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a modern, earth-tone look ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, .stApp {
        background-color: #3e2c23 !important;
        color: #f4ede4 !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1v0mbdj:before {
        background-color: #3e2c23 !important;
    }
    .st-emotion-cache-1c7y2kd {
        background-color: #6e5846 !important;
        color: #f4ede4 !important;
        border-radius: 0 18px 18px 0;
        padding: 1.5em 1em 1.5em 1.5em;
    }
    .stButton>button {
        background-color: #a78c6d !important;
        color: #fff !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        padding: 0.5em 1.5em;
        margin-top: 1em;
        font-family: 'Montserrat', sans-serif !important;
    }
    .stButton>button:hover {
        background-color: #8c7156 !important;
        color: #fff !important;
    }
    .card {
        background: #4b3a2f;
        border-radius: 16px;
        padding: 2em 2em 1.5em 2em;
        margin-bottom: 2em;
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        color: #f4ede4;
    }
    .highlight {
        color: #d6bfa7;
        font-weight: bold;
        font-size: 1.2em;
    }
    .focus-area {
        background: #6e5846;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        color: #f4ede4;
    }
    .weekly-table th, .weekly-table td {
        background: #3e2c23 !important;
        color: #f4ede4 !important;
        border: 1px solid #a78c6d !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-family:Montserrat, sans-serif; color:#f4ede4;'>🏃‍♂️ Running Plan Builder</h1>", unsafe_allow_html=True)
st.caption("Personalized, AI-powered running plans with Gemini")

# --- Sidebar ---
st.sidebar.header("Plan Type")
plan_mode = st.sidebar.radio(
    "Choose your plan mode:",
    ["Quick Plan (for new runners)", "Advanced Plan (personalized)"]
)

st.sidebar.header("Tell us about your running")

exp_level = st.sidebar.selectbox(
    "How would you describe your running experience?",
    ["Beginner (just getting started)", "Intermediate (run regularly)", "Advanced (competitive/serious)"]
)
cluster_map = {
    "Beginner (just getting started)": 0,
    "Intermediate (run regularly)": 1,
    "Advanced (competitive/serious)": 2
}
cluster_id = cluster_map[exp_level]

training_days = st.sidebar.slider(
    "How many days do you run per week?", min_value=1, max_value=7, value=3
)

fatigue_feeling = st.sidebar.selectbox(
    "How do you usually feel after your runs?",
    ["Fresh", "Normal", "Tired", "Exhausted"]
)
fatigue_map = {
    "Fresh": 10.0,
    "Normal": 20.0,
    "Tired": 30.0,
    "Exhausted": 40.0
}
current_fatigue = fatigue_map[fatigue_feeling]

st.sidebar.markdown("---")
goal_race = st.sidebar.selectbox(
    "Are you training for a race?",
    ["No", "5K", "10K", "Half Marathon", "Marathon"]
)
race_distance_map = {
    "5K": 3.1,
    "10K": 6.2,
    "Half Marathon": 13.1,
    "Marathon": 26.2
}
goal_race_distance = None
weeks_until_race = None
if goal_race != "No":
    goal_race_distance = race_distance_map[goal_race]
    weeks_until_race = st.sidebar.slider("Weeks until race", min_value=1, max_value=52, value=8)

if plan_mode == "Quick Plan (for new runners)":
    current_mileage = st.sidebar.number_input(
        "How many miles do you usually run per week?", min_value=0.0, max_value=200.0, value=10.0
    )
    predicted_mileage = current_mileage * 1.08
else:
    st.sidebar.markdown("#### Enter your weekly mileage for the last 6 weeks:")
    recent_mileage = []
    for i in range(6, 0, -1):
        val = st.sidebar.number_input(f"Week {i} ago", min_value=0.0, max_value=200.0, value=10.0)
        recent_mileage.append(val)
    if predict_next_week_mileage:
        predicted_mileage = predict_next_week_mileage(recent_mileage)
    else:
        predicted_mileage = sum(recent_mileage[-3:]) / 3 * 1.05

def extract_markdown_table(text):
    """
    Extracts the first markdown table from a string and returns it as a pandas DataFrame.
    """
    lines = text.splitlines()
    table_lines = []
    in_table = False
    for line in lines:
        if re.match(r"^\|.*\|$", line):
            table_lines.append(line)
            in_table = True
        elif in_table and (line.strip() == "" or not "|" in line):
            break
        elif in_table:
            table_lines.append(line)
    if table_lines:
        # Remove alignment lines (those with only dashes and pipes)
        table_str = "\n".join([l for l in table_lines if not re.match(r"^\|\s*:?-+:?\s*\|", l)])
        try:
            df = pd.read_csv(StringIO(table_str), sep="|").dropna(axis=1, how='all')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            return df
        except Exception:
            return None
    return None

# --- Main Layout ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### Your Personalized Plan")
if st.button("Generate My Plan"):
    with st.spinner("Generating your plan..."):
        recommender = RunningRecommender()
        rec = recommender.get_recommendation(
            cluster_id=cluster_id,
            current_weekly_mileage=current_mileage if plan_mode == "Quick Plan (for new runners)" else recent_mileage[-1],
            predicted_next_week_mileage=predicted_mileage,
            current_fatigue_index=current_fatigue,
            training_days_per_week=training_days,
            goal_race_distance=goal_race_distance,
            weeks_until_race=weeks_until_race
        )
        # Map action code to human-friendly phrase
        rec['action'] = action_map.get(rec['action'], rec['action'].replace('_', ' ').title())
        handler = LLMHandler()
        plan = handler.get_friendly_plan(rec)

        # --- Plan Summary Section ---
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"<div class='highlight'>Level: {rec['cluster_name']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Current Mileage:** {rec['current_mileage']} miles/week")
            st.markdown(f"**Training Days:** {rec['training_days']} days/week")
            if goal_race_distance:
                st.markdown(f"**Goal Race:** {goal_race} in {weeks_until_race} weeks")
        with col2:
            st.markdown(f"<div class='focus-area'>Fatigue: <b>{rec['current_fatigue']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='focus-area'>Next Week Mileage: <b>{rec['predicted_mileage']:.1f}</b></div>", unsafe_allow_html=True)

        # --- Extract summary, table, and coach's advice from LLM output ---
        summary, table, rest = None, None, None
        lines = plan.splitlines()
        summary_lines = []
        table_lines = []
        in_table = False
        for line in lines:
            if line.strip().startswith("| Day") or line.strip().startswith("|Day"):
                in_table = True
                table_lines.append(line)
            elif in_table and line.strip().startswith("|"):
                table_lines.append(line)
            elif in_table and (line.strip() == "" or not "|" in line):
                in_table = False
            elif not in_table and not table_lines:
                summary_lines.append(line)
        rest = "\n".join(lines[len(summary_lines) + len(table_lines):])
        summary = "\n".join(summary_lines)
        table = "\n".join(table_lines)

        if summary.strip():
            st.markdown(summary)
        week_table = extract_markdown_table(table)
        if week_table is not None and not week_table.empty:
            st.markdown("#### 🗓️ Weekly Schedule")
            st.table(week_table)
        else:
            st.info("No structured table found. Please check the plan below.")
        if rec['caution_flags']:
            st.markdown("<div class='focus-area'><b>⚠️ Cautions:</b><ul>" + "".join(f"<li>{c}</li>" for c in rec['caution_flags']) + "</ul></div>", unsafe_allow_html=True)
        if rest.strip():
            st.markdown("#### 📋 Coach's Advice")
            st.markdown(rest)
else:
    st.info("Fill in your details on the left and click **Generate My Plan**!")
st.markdown("</div>", unsafe_allow_html=True)
import pandas as pd
import streamlit as st

from src.ui.filter_section import (
    render_sidebar_filters,
    stop_if_filtered_data_empty,
)

from src.ui.candidate_history_section import render_candidate_history_section
from src.ui.pattern_section import render_pattern_section
from src.ui.growth_section import render_growth_section
from src.ui.main_dashboard_section import render_main_dashboard_section
from src.ui.sidebar_section import render_sidebar_forms


from src.analyzer import (
    load_data,
    calculate_metrics,
)

DATA_PATH = "data/covers.csv"
SNAPSHOTS_PATH = "data/metrics_snapshots.csv"
CANDIDATE_TESTS_PATH = "data/candidate_tests.csv"


st.set_page_config(page_title="Cover Performance Analytics", layout="wide")

st.title("Cover Performance Analytics")
st.write("Analyze your cover performances across platforms.")


# -----------------------------
# LOAD RAW DATA
# -----------------------------

raw_df = load_data(DATA_PATH)

covers_df = pd.read_csv(DATA_PATH)
snapshots_df = pd.read_csv(SNAPSHOTS_PATH)

# -----------------------------
# SIDEBAR FORMS
# -----------------------------

render_sidebar_forms(DATA_PATH, SNAPSHOTS_PATH)


# -----------------------------
# CALCULATE METRICS
# -----------------------------

df = calculate_metrics(raw_df)


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

filtered_df = render_sidebar_filters(df)
stop_if_filtered_data_empty(filtered_df)


# -----------------------------
# MAIN DASHBOARD
# -----------------------------

render_main_dashboard_section(filtered_df)


# -----------------------------
# GROWTH ANALYTICS
# -----------------------------

render_growth_section(covers_df, snapshots_df)


# -----------------------------
# PATTERN ANALYTICS
# -----------------------------

render_pattern_section(
    DATA_PATH,
    SNAPSHOTS_PATH,
    CANDIDATE_TESTS_PATH,
)


# -----------------------------
# CANDIDATE HISTORY ANALYTICS
# -----------------------------

render_candidate_history_section(CANDIDATE_TESTS_PATH)
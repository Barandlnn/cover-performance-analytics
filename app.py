import streamlit as st

from src.data_manager import (
    
    CANDIDATE_TESTS_PATH,
    load_current_cover_data,
    load_covers_raw,
    load_snapshots_raw,
)

from src.analyzer import calculate_metrics

from src.ui.filter_section import (
    render_sidebar_filters,
    stop_if_filtered_data_empty,
)

from src.ui.candidate_history_section import render_candidate_history_section
from src.ui.pattern_section import render_pattern_section
from src.ui.growth_section import render_growth_section
from src.ui.main_dashboard_section import render_main_dashboard_section
from src.ui.sidebar_section import render_sidebar_forms


st.set_page_config(page_title="Cover Performance Analytics", layout="wide")

st.title("Cover Performance Analytics")
st.write("Analyze your cover performances across platforms.")


# -----------------------------
# LOAD RAW DATA
# -----------------------------

raw_df = load_current_cover_data()

covers_df = load_covers_raw()
snapshots_df = load_snapshots_raw()


# -----------------------------
# SIDEBAR FORMS
# -----------------------------

render_sidebar_forms()


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

render_pattern_section()


# -----------------------------
# CANDIDATE HISTORY ANALYTICS
# -----------------------------

render_candidate_history_section(CANDIDATE_TESTS_PATH)
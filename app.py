import streamlit as st

from src.ui.report_export_section import render_report_export_section

from src.data_manager import (
    load_current_cover_data,
    load_covers_raw,
    load_snapshots_raw,
)

from src.i18n import (
    DEFAULT_LANGUAGE,
    LANGUAGE_OPTIONS,
    get_language_label,
    get_language_code,
    t,
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
from src.ui.ai_creator_coach_section import render_ai_creator_coach_section
from src.ui.sidebar_section import render_sidebar_forms

st.set_page_config(
    page_title=t("app.title", DEFAULT_LANGUAGE),
    layout="wide",
)


# -----------------------------
# LANGUAGE SETTINGS
# -----------------------------

if "language" not in st.session_state:
    st.session_state["language"] = DEFAULT_LANGUAGE

if "language_selector" not in st.session_state:
    st.session_state["language_selector"] = get_language_label(
        st.session_state["language"]
    )


def sync_language_selection() -> None:
    """Synchronize the selected language label with the language code."""
    st.session_state["language"] = get_language_code(
        st.session_state["language_selector"]
    )


current_language = st.session_state["language"]
language_labels = list(LANGUAGE_OPTIONS.keys())

st.sidebar.selectbox(
    t("language.selector_label", current_language),
    language_labels,
    key="language_selector",
    on_change=sync_language_selection,
)

language = st.session_state["language"]


st.title(t("app.title", language))
st.caption(t("app.caption", language))


# -----------------------------
# LOAD RAW DATA
# -----------------------------

raw_df = load_current_cover_data()
covers_df = load_covers_raw()
snapshots_df = load_snapshots_raw()


# -----------------------------
# SIDEBAR FORMS
# -----------------------------

render_sidebar_forms(
    language=language,
)


# -----------------------------
# CALCULATE METRICS
# -----------------------------

df = calculate_metrics(raw_df)


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

filtered_df = render_sidebar_filters(
    df,
    language=language,
)

stop_if_filtered_data_empty(
    filtered_df,
    language=language,
)


# -----------------------------
# MAIN DASHBOARD
# -----------------------------

render_main_dashboard_section(
    filtered_df,
    language=language,
)

# -----------------------------
# AI CREATOR COACH
# -----------------------------

render_ai_creator_coach_section(
    filtered_df,
    language=language,
)

# -----------------------------
# REPORT EXPORT
# -----------------------------

render_report_export_section(
    filtered_df,
    language=language,
)


# -----------------------------
# GROWTH ANALYTICS
# -----------------------------

render_growth_section(
    covers_df,
    snapshots_df,
    language=language,
)


# -----------------------------
# PATTERN ANALYTICS
# -----------------------------

render_pattern_section(
    language=language,
)


# -----------------------------
# CANDIDATE HISTORY ANALYTICS
# -----------------------------

render_candidate_history_section(
    language=language,
)

import streamlit as st

from src.data_manager import (
    load_covers_raw,
    load_snapshots_raw,
)

from src.candidate_test_repository import save_candidate_test_result
from src.pattern_analyzer import (
    get_all_pattern_summaries,
    generate_pattern_insights,
    generate_pattern_recommendations,
    score_cover_candidate,
    generate_candidate_explanations,
)


def render_pattern_section() -> None:
    """
    V2 Pattern Analytics ve V2 Next Cover Candidate Test ekranını render eder.

    Bu dosya sadece Streamlit UI tarafını yönetir.
    Pattern hesaplama işleri src/pattern_analyzer.py içinde kalır.
    CSV okuma/yazma işleri src/data_manager.py üzerinden yönetilir.
    """

    st.markdown("---")
    st.header("📊 V2 Pattern Analytics")
    st.caption(
        "Analyze which genres, artists, and content types perform better based on "
        "latest metrics and growth data."
    )

    try:
        covers_df_v2 = load_covers_raw()
        snapshots_df_v2 = load_snapshots_raw()

        pattern_summaries = get_all_pattern_summaries(
            covers_df_v2,
            snapshots_df_v2,
        )

        if not pattern_summaries:
            st.info(
                "Pattern analytics is not available yet. "
                "Required columns may be missing."
            )
            return

        pattern_insights = generate_pattern_insights(pattern_summaries)
        pattern_recommendations = generate_pattern_recommendations(pattern_summaries)

        st.subheader("🧠 V2 Pattern Insights")

        for insight in pattern_insights:
            st.info(insight)

        st.subheader("🎯 V2 Cover Planning Recommendations")

        if pattern_recommendations.empty:
            st.info("No planning recommendations are available yet.")
        else:
            st.dataframe(
                pattern_recommendations,
                width="stretch",
            )

            top_recommendation = pattern_recommendations.iloc[0]

            st.success(
                f"Top recommendation: {top_recommendation['pattern']} "
                f"({top_recommendation['dimension']}) — "
                f"{top_recommendation['priority']}. "
                f"{top_recommendation['action']}"
            )

        render_candidate_test_section(
            pattern_summaries=pattern_summaries,
        )

    except Exception as error:
        st.error(f"Pattern analytics could not be loaded: {error}")


def render_candidate_test_section(
    pattern_summaries: dict,
) -> None:
    """
    V2 Next Cover Candidate Test ekranını render eder.

    Bu bölüm pattern_summaries üzerinden yeni cover adayı skorlar.
    """

    st.subheader("🧪 V2 Next Cover Candidate Test")
    st.caption(
        "Select a possible future cover profile and estimate how strong it looks "
        "based on current pattern data."
    )

    def _get_candidate_options(dimension: str) -> list[str]:
        summary_df = pattern_summaries.get(dimension)

        if (
            summary_df is None
            or summary_df.empty
            or dimension not in summary_df.columns
        ):
            return ["Not available"]

        return summary_df[dimension].astype(str).tolist()

    candidate_col1, candidate_col2, candidate_col3 = st.columns(3)

    with candidate_col1:
        selected_candidate_genre = st.selectbox(
            "Candidate Genre",
            _get_candidate_options("genre"),
            key="candidate_genre_selector",
        )

    with candidate_col2:
        selected_candidate_artist = st.selectbox(
            "Candidate Artist",
            _get_candidate_options("artist"),
            key="candidate_artist_selector",
        )

    with candidate_col3:
        selected_candidate_content_type = st.selectbox(
            "Candidate Content Type",
            _get_candidate_options("content_type"),
            key="candidate_content_type_selector",
        )

    if st.button("Analyze Candidate Cover", key="analyze_candidate_button"):
        candidate_details_df, candidate_summary = score_cover_candidate(
            pattern_summaries,
            {
                "genre": selected_candidate_genre,
                "artist": selected_candidate_artist,
                "content_type": selected_candidate_content_type,
            },
        )

        st.session_state["last_candidate_test"] = {
            "genre": selected_candidate_genre,
            "artist": selected_candidate_artist,
            "content_type": selected_candidate_content_type,
            "details_df": candidate_details_df,
            "summary": candidate_summary,
        }

    last_candidate_test = st.session_state.get("last_candidate_test")

    if last_candidate_test is None:
        return

    candidate_details_df = last_candidate_test["details_df"]
    candidate_summary = last_candidate_test["summary"]

    st.metric(
        "Candidate Score",
        candidate_summary["candidate_score"],
        candidate_summary["candidate_label"],
    )

    if candidate_summary["candidate_label"] in [
        "Strong Candidate",
        "Promising Candidate",
    ]:
        st.success(candidate_summary["action"])
    elif candidate_summary["candidate_label"] == "Interesting but Needs More Data":
        st.warning(candidate_summary["action"])
    else:
        st.info(candidate_summary["action"])

    candidate_explanations = generate_candidate_explanations(
        candidate_details_df,
        candidate_summary,
    )

    st.subheader("🧠 Candidate Explanation")

    for explanation in candidate_explanations:
        st.info(explanation)

    st.dataframe(
        candidate_details_df,
        width="stretch",
    )

    if st.button("Save Candidate Test Result", key="save_candidate_button"):
        save_candidate_test_result(
            last_candidate_test["genre"],
            last_candidate_test["artist"],
            last_candidate_test["content_type"],
            last_candidate_test["summary"],
        )

        st.success("Candidate test result saved successfully.")
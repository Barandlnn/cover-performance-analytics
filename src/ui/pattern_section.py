import streamlit as st

from src.candidate_test_repository import (
    save_candidate_test_result,
)
from src.data_manager import (
    load_covers_raw,
    load_snapshots_raw,
)
from src.i18n import t
from src.pattern_analyzer import (
    generate_candidate_explanations,
    generate_pattern_insights,
    generate_pattern_recommendations,
    get_all_pattern_summaries,
    score_cover_candidate,
)

CANDIDATE_LABEL_TRANSLATION_KEYS = {
    "Strong Candidate": "pattern.candidate.label.strong",
    "Promising Candidate": "pattern.candidate.label.promising",
    "Interesting but Needs More Data": ("pattern.candidate.label.needs_more_data"),
    "Experimental Candidate": ("pattern.candidate.label.experimental"),
    "Weak Candidate": "pattern.candidate.label.weak",
}


CANDIDATE_ACTION_TRANSLATION_KEYS = {
    "Strong Candidate": "pattern.candidate.action.strong",
    "Promising Candidate": "pattern.candidate.action.promising",
    "Interesting but Needs More Data": ("pattern.candidate.action.needs_more_data"),
    "Experimental Candidate": ("pattern.candidate.action.experimental"),
    "Weak Candidate": "pattern.candidate.action.weak",
}


def _get_localized_candidate_label(
    candidate_label: str,
    language: str,
) -> str:
    """
    Analyzer tarafından üretilen sabit aday etiketini
    seçilen arayüz diline çevirir.
    """
    translation_key = CANDIDATE_LABEL_TRANSLATION_KEYS.get(candidate_label)

    if translation_key is None:
        return candidate_label

    return t(
        translation_key,
        language,
    )


def _get_localized_candidate_action(
    candidate_label: str,
    language: str,
) -> str:
    """
    Aday etiketine karşılık gelen aksiyon mesajını
    seçilen arayüz dilinde döndürür.
    """
    translation_key = CANDIDATE_ACTION_TRANSLATION_KEYS.get(candidate_label)

    if translation_key is None:
        return candidate_label

    return t(
        translation_key,
        language,
    )


def render_pattern_section(
    language: str,
) -> None:
    """
    V2 Pattern Analytics ve V2 Next Cover Candidate Test
    ekranını render eder.

    Bu dosya sadece Streamlit UI tarafını yönetir.
    Pattern hesaplama işleri src/pattern_analyzer.py içinde kalır.
    CSV okuma/yazma işleri src.data_manager.py üzerinden yönetilir.
    """
    st.markdown("---")

    st.header(
        t(
            "pattern.title",
            language,
        )
    )

    st.caption(
        t(
            "pattern.caption",
            language,
        )
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
                t(
                    "pattern.unavailable",
                    language,
                )
            )
            return

        pattern_insights = generate_pattern_insights(
            pattern_summaries,
            language=language,
        )

        pattern_recommendations = generate_pattern_recommendations(
            pattern_summaries,
            language=language,
        )

        st.subheader(
            t(
                "pattern.insights.title",
                language,
            )
        )

        for insight in pattern_insights:
            st.info(insight)

        st.subheader(
            t(
                "pattern.recommendations.title",
                language,
            )
        )

        if pattern_recommendations.empty:
            st.info(
                t(
                    "pattern.recommendations.empty",
                    language,
                )
            )

        else:
            st.dataframe(
                pattern_recommendations,
                width="stretch",
            )

            top_recommendation = pattern_recommendations.iloc[0]

            top_recommendation_message = t(
                "pattern.recommendations.top",
                language,
            ).format(
                pattern=top_recommendation["pattern"],
                dimension=top_recommendation["dimension"],
                priority=top_recommendation["priority"],
                action=top_recommendation["action"],
            )

            st.success(top_recommendation_message)

        render_candidate_test_section(
            pattern_summaries=pattern_summaries,
            language=language,
        )

    except Exception as error:
        st.error(f"{t('pattern.load_error', language)}: {error}")


def render_candidate_test_section(
    pattern_summaries: dict,
    language: str,
) -> None:
    """
    V2 Next Cover Candidate Test ekranını render eder.

    Bu bölüm pattern_summaries üzerinden yeni cover
    adayını skorlar.
    """
    st.subheader(
        t(
            "pattern.candidate.title",
            language,
        )
    )

    st.caption(
        t(
            "pattern.candidate.caption",
            language,
        )
    )

    def _get_candidate_options(
        dimension: str,
    ) -> list[str]:
        summary_df = pattern_summaries.get(dimension)

        if (
            summary_df is None
            or summary_df.empty
            or dimension not in summary_df.columns
        ):
            return [
                t(
                    "pattern.candidate.not_available",
                    language,
                )
            ]

        return summary_df[dimension].astype(str).tolist()

    candidate_col1, candidate_col2, candidate_col3 = st.columns(3)

    with candidate_col1:
        selected_candidate_genre = st.selectbox(
            t(
                "pattern.candidate.genre",
                language,
            ),
            _get_candidate_options("genre"),
            key="candidate_genre_selector",
        )

    with candidate_col2:
        selected_candidate_artist = st.selectbox(
            t(
                "pattern.candidate.artist",
                language,
            ),
            _get_candidate_options("artist"),
            key="candidate_artist_selector",
        )

    with candidate_col3:
        selected_candidate_content_type = st.selectbox(
            t(
                "pattern.candidate.content_type",
                language,
            ),
            _get_candidate_options("content_type"),
            key="candidate_content_type_selector",
        )

    if st.button(
        t(
            "pattern.candidate.analyze",
            language,
        ),
        key="analyze_candidate_button",
    ):
        candidate_details_df, candidate_summary = score_cover_candidate(
            pattern_summaries,
            {
                "genre": selected_candidate_genre,
                "artist": selected_candidate_artist,
                "content_type": (selected_candidate_content_type),
            },
        )

        st.session_state["last_candidate_test"] = {
            "genre": selected_candidate_genre,
            "artist": selected_candidate_artist,
            "content_type": (selected_candidate_content_type),
            "details_df": candidate_details_df,
            "summary": candidate_summary,
        }

    last_candidate_test = st.session_state.get("last_candidate_test")

    if last_candidate_test is None:
        return

    candidate_details_df = last_candidate_test["details_df"]
    candidate_summary = last_candidate_test["summary"]

    candidate_label = candidate_summary["candidate_label"]

    localized_candidate_label = _get_localized_candidate_label(
        candidate_label,
        language,
    )

    localized_candidate_action = _get_localized_candidate_action(
        candidate_label,
        language,
    )

    st.metric(
        t(
            "pattern.candidate.score",
            language,
        ),
        candidate_summary["candidate_score"],
        localized_candidate_label,
    )

    if candidate_label in [
        "Strong Candidate",
        "Promising Candidate",
    ]:
        st.success(localized_candidate_action)

    elif candidate_label == "Interesting but Needs More Data":
        st.warning(localized_candidate_action)

    else:
        st.info(localized_candidate_action)

    candidate_explanations = generate_candidate_explanations(
        candidate_details_df,
        candidate_summary,
        language=language,
    )

    st.subheader(
        t(
            "pattern.candidate.explanation_title",
            language,
        )
    )

    for explanation in candidate_explanations:
        st.info(explanation)

    st.dataframe(
        candidate_details_df,
        width="stretch",
    )

    if st.button(
        t(
            "pattern.candidate.save",
            language,
        ),
        key="save_candidate_button",
    ):
        save_candidate_test_result(
            last_candidate_test["genre"],
            last_candidate_test["artist"],
            last_candidate_test["content_type"],
            last_candidate_test["summary"],
        )

        st.success(
            t(
                "pattern.candidate.save_success",
                language,
            )
        )

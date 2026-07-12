import pandas as pd
import streamlit as st

from src.candidate_history_analyzer import (
    generate_candidate_history_insights,
    get_candidate_history_summary,
    get_genre_candidate_performance,
    get_top_candidates,
    load_candidate_history,
)
from src.i18n import t

DISPLAY_COLUMN_KEYS = {
    "test_date": "candidate_history.columns.test_date",
    "genre": "candidate_history.columns.genre",
    "artist": "candidate_history.columns.artist",
    "content_type": "candidate_history.columns.content_type",
    "candidate_score": "candidate_history.columns.candidate_score",
    "candidate_label": "candidate_history.columns.candidate_label",
    "needs_more_data_count": ("candidate_history.columns.needs_more_data_count"),
    "action": "candidate_history.columns.action",
    "total_tests": "candidate_history.columns.total_tests",
    "average_candidate_score": ("candidate_history.columns.average_candidate_score"),
    "best_candidate_score": ("candidate_history.columns.best_candidate_score"),
    "strong_candidate_count": ("candidate_history.columns.strong_candidate_count"),
    "promising_candidate_count": (
        "candidate_history.columns.promising_candidate_count"
    ),
    "test_count": "candidate_history.columns.test_count",
    "average_score": "candidate_history.columns.average_score",
    "best_score": "candidate_history.columns.best_score",
}

CANDIDATE_LABEL_TRANSLATION_KEYS = {
    "Interesting but Needs More Data": (
        "candidate_history.values." "candidate_label.interesting_but_needs_more_data"
    ),
}


ACTION_TRANSLATION_KEYS = {
    (
        "This idea looks interesting, but you should test it "
        "carefully and collect more data."
    ): ("candidate_history.values." "action.test_carefully_collect_more_data"),
}


def _prepare_display_dataframe(
    df: pd.DataFrame,
    language: str,
) -> pd.DataFrame:
    """
    DataFrame kolonlarını ve kullanıcıya gösterilen bazı hücre
    değerlerini seçilen dile göre çevirir.

    Orijinal DataFrame, CSV değerleri ve analiz kolonları değiştirilmez.
    """
    display_df = df.copy()

    if "candidate_label" in display_df.columns:
        candidate_label_translations = {
            original_value: t(
                translation_key,
                language,
            )
            for original_value, translation_key in CANDIDATE_LABEL_TRANSLATION_KEYS.items()
        }

        display_df["candidate_label"] = display_df["candidate_label"].replace(
            candidate_label_translations
        )

    if "action" in display_df.columns:
        action_translations = {
            original_value: t(
                translation_key,
                language,
            )
            for original_value, translation_key in ACTION_TRANSLATION_KEYS.items()
        }

        display_df["action"] = display_df["action"].replace(action_translations)

    translated_columns = {
        column: t(
            translation_key,
            language,
        )
        for column, translation_key in DISPLAY_COLUMN_KEYS.items()
        if column in display_df.columns
    }

    return display_df.rename(
        columns=translated_columns,
    )


def render_candidate_history_section(
    language: str,
) -> None:
    """
    Render the Candidate Test History and Candidate History Analytics section.

    This module only manages the Streamlit UI layer. Candidate history loading,
    normalization, summary calculation, and insight generation are handled by
    src.candidate_history_analyzer.
    """
    st.header(
        t(
            "candidate_history.title",
            language,
        )
    )

    try:
        candidate_history_df = load_candidate_history()

    except FileNotFoundError:
        st.info(
            t(
                "candidate_history.file_not_found",
                language,
            )
        )
        return

    except Exception as error:
        st.error(
            t(
                "candidate_history.load_error",
                language,
            ).format(
                error=error,
            )
        )
        return

    if candidate_history_df.empty:
        st.info(
            t(
                "candidate_history.empty",
                language,
            )
        )
        return

    candidate_history_display_df = _prepare_display_dataframe(
        candidate_history_df,
        language,
    )

    st.dataframe(
        candidate_history_display_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader(
        t(
            "candidate_history.summary_title",
            language,
        )
    )

    summary = get_candidate_history_summary(candidate_history_df)

    summary_df = pd.DataFrame([summary])

    summary_display_df = _prepare_display_dataframe(
        summary_df,
        language,
    )

    st.dataframe(
        summary_display_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader(
        t(
            "candidate_history.insights_title",
            language,
        )
    )

    history_insights = generate_candidate_history_insights(
        candidate_history_df,
        language=language,
    )

    for insight in history_insights:
        st.write(f"- {insight}")

    st.subheader(
        t(
            "candidate_history.top_candidates_title",
            language,
        )
    )

    top_candidates_df = get_top_candidates(candidate_history_df)

    top_candidates_display_df = _prepare_display_dataframe(
        top_candidates_df,
        language,
    )

    st.dataframe(
        top_candidates_display_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader(
        t(
            "candidate_history.genre_performance_title",
            language,
        )
    )

    genre_performance_df = get_genre_candidate_performance(candidate_history_df)

    if genre_performance_df.empty:
        st.info(
            t(
                "candidate_history.genre_data_insufficient",
                language,
            )
        )

    else:
        genre_performance_display_df = _prepare_display_dataframe(
            genre_performance_df,
            language,
        )

        st.dataframe(
            genre_performance_display_df,
            width="stretch",
            hide_index=True,
        )

        st.bar_chart(genre_performance_df.set_index("genre")["average_score"])

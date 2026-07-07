import pandas as pd
import streamlit as st

from src.candidate_history_analyzer import (
    load_candidate_history,
    get_candidate_history_summary,
    generate_candidate_history_insights,
    get_top_candidates,
    get_genre_candidate_performance,
)


def render_candidate_history_section() -> None:
    """
    V2.7 / V2.8 Candidate Test History ve Candidate History Analytics ekranını render eder.

    Bu dosya sadece Streamlit UI tarafını yönetir.
    Hesaplama işleri src/candidate_history_analyzer.py içinde kalır.
    """

    st.header("Candidate Test History")

    try:
        candidate_history_df = load_candidate_history()
    except FileNotFoundError:
        st.info("Henüz candidate test history dosyası bulunamadı.")
        return
    except Exception as error:
        st.error(f"Candidate history yüklenirken hata oluştu: {error}")
        return

    if candidate_history_df.empty:
        st.info("Henüz kaydedilmiş candidate test bulunmuyor.")
        return

    st.dataframe(
        candidate_history_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader("Candidate History Summary")

    summary = get_candidate_history_summary(candidate_history_df)
    summary_df = pd.DataFrame([summary])

    st.dataframe(
        summary_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader("Candidate History Insights")

    history_insights = generate_candidate_history_insights(candidate_history_df)

    for insight in history_insights:
        st.write(f"- {insight}")

    st.subheader("Top Candidate Tests")

    top_candidates_df = get_top_candidates(candidate_history_df)

    st.dataframe(
        top_candidates_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader("Genre-Based Candidate Performance")

    genre_performance_df = get_genre_candidate_performance(candidate_history_df)

    if genre_performance_df.empty:
        st.info("Genre bazlı analiz için yeterli veri bulunamadı.")
    else:
        st.dataframe(
            genre_performance_df,
            width="stretch",
            hide_index=True,
        )

        st.bar_chart(
            genre_performance_df.set_index("genre")["average_score"]
        )
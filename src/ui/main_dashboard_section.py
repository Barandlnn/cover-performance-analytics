import streamlit as st

from src.analyzer import get_top_covers, generate_insights


MAIN_TABLE_COLUMNS = [
    "cover_id",
    "snapshot_id",
    "snapshot_date",
    "title",
    "artist",
    "platform",
    "content_type",
    "genre",
    "post_date",
    "post_time",
    "duration_sec",
    "hook_type",
    "vocal_style",
    "language",
    "caption_length",
    "hashtags",
    "hashtag_count",
    "audio_quality_score",
    "thumbnail_score",
    "recording_type",
    "arrangement_type",
    "song_mood",
    "content_origin",
    "views",
    "likes",
    "comments",
    "saves",
    "shares",
    "engagement_rate",
    "save_rate",
    "share_rate",
    "comment_rate",
    "performance_score",
]


TOP_COVERS_COLUMNS = [
    "cover_id",
    "snapshot_id",
    "snapshot_date",
    "title",
    "artist",
    "platform",
    "genre",
    "post_time",
    "duration_sec",
    "hook_type",
    "vocal_style",
    "audio_quality_score",
    "thumbnail_score",
    "recording_type",
    "arrangement_type",
    "song_mood",
    "content_origin",
    "views",
    "likes",
    "comments",
    "saves",
    "shares",
    "engagement_rate",
    "save_rate",
    "share_rate",
    "comment_rate",
    "performance_score",
]


def get_existing_columns(df, columns):
    """
    DataFrame içinde gerçekten var olan kolonları döndürür.

    Bu küçük güvenlik sayesinde ileride bir kolon adı değişirse
    tüm dashboard direkt çökmek yerine mevcut kolonlarla çalışabilir.
    """
    return [column for column in columns if column in df.columns]


def render_overview_metrics(filtered_df):
    """
    Dashboard üstündeki KPI kartlarını gösterir.
    """
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)

    total_covers = len(filtered_df)
    average_engagement = filtered_df["engagement_rate"].mean()
    average_save_rate = filtered_df["save_rate"].mean()
    best_score = filtered_df["performance_score"].max()

    col1.metric("Total Covers", total_covers)
    col2.metric("Avg Engagement Rate", f"{average_engagement:.2f}%")
    col3.metric("Avg Save Rate", f"{average_save_rate:.2f}%")
    col4.metric("Best Score", f"{best_score:.2f}")


def render_all_covers_table(filtered_df):
    """
    Tüm cover kayıtlarını tablo olarak gösterir.
    """
    st.subheader("All Covers")

    st.dataframe(
        filtered_df[get_existing_columns(filtered_df, MAIN_TABLE_COLUMNS)],
        hide_index=True,
        use_container_width=True,
    )


def render_top_covers_table(top_covers):
    """
    En iyi performans gösteren coverları tablo olarak gösterir.
    """
    st.subheader("Top Performing Covers")

    st.dataframe(
        top_covers[get_existing_columns(top_covers, TOP_COVERS_COLUMNS)],
        hide_index=True,
        use_container_width=True,
    )


def render_performance_chart(filtered_df):
    """
    Cover başlığına göre performance_score grafiğini gösterir.
    """
    st.subheader("Performance Score Chart")

    chart_data = filtered_df.set_index("title")["performance_score"]

    st.bar_chart(chart_data)


def render_quick_insights(filtered_df, top_covers):
    """
    En iyi cover üzerinden kısa yorum ve AI-like insight üretir.
    """
    st.subheader("Quick Insights")

    best_cover = top_covers.iloc[0]

    st.success(f"Best performing cover: {best_cover['title']}")

    st.write(f"Artist: **{best_cover['artist']}**")
    st.write(f"Genre: **{best_cover['genre']}**")
    st.write(f"Hook type: **{best_cover['hook_type']}**")
    st.write(f"Vocal style: **{best_cover['vocal_style']}**")
    st.write(f"Performance score: **{best_cover['performance_score']}**")
    st.write(f"Engagement rate: **{best_cover['engagement_rate']}%**")
    st.write(f"Save rate: **{best_cover['save_rate']}%**")
    st.write(f"Share rate: **{best_cover['share_rate']}%**")

    st.info(
        "This result suggests that this type of cover may match your audience better. "
        "To make stronger conclusions, add more real cover data."
    )

    st.subheader("AI-Like Interpretation")

    insights = generate_insights(filtered_df, best_cover)

    for insight in insights:
        st.write(f"- {insight}")


def render_main_dashboard_section(filtered_df):
    """
    Ana dashboard bölümünü tek noktadan render eder.

    Bu fonksiyon şunları yönetir:
    - Overview KPI kartları
    - All Covers tablosu
    - Top Covers tablosu
    - Performance Score grafiği
    - Quick Insights
    """
    render_overview_metrics(filtered_df)
    render_all_covers_table(filtered_df)

    top_covers = get_top_covers(filtered_df)

    render_top_covers_table(top_covers)
    render_performance_chart(filtered_df)
    render_quick_insights(filtered_df, top_covers)
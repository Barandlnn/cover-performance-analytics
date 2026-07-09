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


def _get_existing_columns(df, columns):
    """
    Return only the columns that actually exist in the DataFrame.

    This prevents the dashboard from crashing if a column is renamed,
    removed, or not available yet in older CSV data.
    """
    return [column for column in columns if column in df.columns]


def _get_numeric_mean(df, column_name):
    """
    Safely calculate a numeric column average.
    """
    if column_name not in df.columns or df.empty:
        return 0

    return df[column_name].mean()


def _get_numeric_max(df, column_name):
    """
    Safely calculate a numeric column maximum.
    """
    if column_name not in df.columns or df.empty:
        return 0

    return df[column_name].max()


def _get_row_value(row, column_name, default_value="-"):
    """
    Safely read a value from a pandas Series row.
    """
    if column_name not in row.index:
        return default_value

    return row[column_name]


def _render_overview_metrics(filtered_df):
    """
    Render the main KPI cards at the top of the dashboard.
    """
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)

    total_covers = len(filtered_df)
    average_engagement = _get_numeric_mean(filtered_df, "engagement_rate")
    average_save_rate = _get_numeric_mean(filtered_df, "save_rate")
    best_score = _get_numeric_max(filtered_df, "performance_score")

    col1.metric("Total Covers", total_covers)
    col2.metric("Avg Engagement Rate", f"{average_engagement:.2f}%")
    col3.metric("Avg Save Rate", f"{average_save_rate:.2f}%")
    col4.metric("Best Score", f"{best_score:.2f}")


def _render_all_covers_table(filtered_df):
    """
    Render all filtered cover records as a table.
    """
    st.subheader("All Covers")

    existing_columns = _get_existing_columns(filtered_df, MAIN_TABLE_COLUMNS)

    if not existing_columns:
        st.warning("No displayable columns found for the cover table.")
        return

    st.dataframe(
        filtered_df[existing_columns],
        hide_index=True,
        width="stretch",
    )


def _render_top_covers_table(top_covers):
    """
    Render the best performing covers as a table.
    """
    st.subheader("Top Performing Covers")

    if top_covers.empty:
        st.info("No top cover data available yet.")
        return

    existing_columns = _get_existing_columns(top_covers, TOP_COVERS_COLUMNS)

    if not existing_columns:
        st.warning("No displayable columns found for the top covers table.")
        return

    st.dataframe(
        top_covers[existing_columns],
        hide_index=True,
        width="stretch",
    )


def _render_performance_chart(filtered_df):
    """
    Render the performance score chart by cover title.
    """
    st.subheader("Performance Score Chart")

    required_columns = ["title", "performance_score"]
    missing_columns = [
        column for column in required_columns if column not in filtered_df.columns
    ]

    if missing_columns:
        st.warning(
            "Performance chart cannot be displayed. "
            f"Missing columns: {', '.join(missing_columns)}"
        )
        return

    if filtered_df.empty:
        st.info("No data available for the performance chart.")
        return

    chart_data = filtered_df.set_index("title")["performance_score"]

    st.bar_chart(chart_data)


def _render_quick_insights(filtered_df, top_covers):
    """
    Render a short summary and AI-like insights for the best cover.
    """
    st.subheader("Quick Insights")

    if top_covers.empty:
        st.info("No cover data available for insights yet.")
        return

    best_cover = top_covers.iloc[0]

    st.success(f"Best performing cover: {_get_row_value(best_cover, 'title')}")

    st.write(f"Artist: **{_get_row_value(best_cover, 'artist')}**")
    st.write(f"Genre: **{_get_row_value(best_cover, 'genre')}**")
    st.write(f"Hook type: **{_get_row_value(best_cover, 'hook_type')}**")
    st.write(f"Vocal style: **{_get_row_value(best_cover, 'vocal_style')}**")
    st.write(f"Performance score: **{_get_row_value(best_cover, 'performance_score')}**")
    st.write(f"Engagement rate: **{_get_row_value(best_cover, 'engagement_rate')}%**")
    st.write(f"Save rate: **{_get_row_value(best_cover, 'save_rate')}%**")
    st.write(f"Share rate: **{_get_row_value(best_cover, 'share_rate')}%**")

    st.info(
        "This result suggests that this type of cover may match your audience better. "
        "To make stronger conclusions, add more real cover data."
    )

    st.subheader("AI-Like Interpretation")

    try:
        insights = generate_insights(filtered_df, best_cover)
    except KeyError as error:
        st.warning(f"Insights could not be generated. Missing column: {error}")
        return

    for insight in insights:
        st.write(f"- {insight}")


def render_main_dashboard_section(filtered_df):
    """
    Render the full main dashboard section.

    This function is the public entry point used by app.py.
    Internal rendering details are handled by private helper functions.
    """
    _render_overview_metrics(filtered_df)
    _render_all_covers_table(filtered_df)

    top_covers = get_top_covers(filtered_df)

    _render_top_covers_table(top_covers)
    _render_performance_chart(filtered_df)
    _render_quick_insights(filtered_df, top_covers)
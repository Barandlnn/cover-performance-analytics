import pandas as pd
import streamlit as st


def get_filter_options(df: pd.DataFrame, column_name: str) -> list:
    """
    Return sidebar filter options for the given DataFrame column.

    The returned list always starts with "All". Empty values are ignored
    so they do not appear as selectable filter options.
    """
    if column_name not in df.columns:
        return ["All"]

    options = (
        df[column_name]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return ["All"] + sorted(options)


def apply_sidebar_filters(
    df: pd.DataFrame,
    selected_platform: str,
    selected_genre: str,
) -> pd.DataFrame:
    """
    Apply the selected sidebar filters to the given DataFrame.
    """
    filtered_df = df.copy()

    if selected_platform != "All":
        filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df["genre"] == selected_genre]

    return filtered_df


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar filter widgets and return the filtered DataFrame.
    """
    st.sidebar.header("Filters")

    platform_options = get_filter_options(df, "platform")
    selected_platform = st.sidebar.selectbox(
        "Platform Filter",
        platform_options,
    )

    genre_options = get_filter_options(df, "genre")
    selected_genre = st.sidebar.selectbox(
        "Genre Filter",
        genre_options,
    )

    filtered_df = apply_sidebar_filters(
        df,
        selected_platform,
        selected_genre,
    )

    return filtered_df


def stop_if_filtered_data_empty(filtered_df: pd.DataFrame):
    """
    Stop the Streamlit app when the selected filters return no data.
    """
    if filtered_df.empty:
        st.warning("No covers found for the selected filters.")
        st.stop()
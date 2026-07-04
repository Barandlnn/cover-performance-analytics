import streamlit as st
import pandas as pd


def get_filter_options(df: pd.DataFrame, column_name: str) -> list:
    """
    Verilen kolon için sidebar filtre seçeneklerini üretir.

    Örnek:
    platform kolonu için:
    ["All", "Instagram", "TikTok", "YouTube"]

    Not:
    dropna() kullanıyoruz çünkü boş değerler selectbox içinde sorun çıkarabilir.
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
    Seçilen sidebar filtrelerine göre DataFrame'i filtreler.
    """
    filtered_df = df.copy()

    if selected_platform != "All":
        filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df["genre"] == selected_genre]

    return filtered_df


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sidebar filtrelerini render eder ve filtrelenmiş DataFrame döndürür.

    Şu anda iki filtre var:
    - Platform Filter
    - Genre Filter
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
    Filtre sonucu boşsa kullanıcıya uyarı verir ve uygulama akışını durdurur.
    """
    if filtered_df.empty:
        st.warning("No covers found for the selected filters.")
        st.stop()
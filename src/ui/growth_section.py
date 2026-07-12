import pandas as pd
import streamlit as st

from src.analyzer import (
    get_growth_summary,
    get_cover_snapshot_history,
)
from src.i18n import t


def render_growth_section(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
    language: str,
) -> None:
    """
    V1.6 Growth Analytics ekranını render eder.

    Bu dosyanın sorumluluğu:
    - Cover'ların snapshot bazlı büyümesini göstermek
    - En iyi views / likes / engagement growth metriklerini göstermek
    - Seçili cover için snapshot geçmişini ve trend grafiklerini göstermek

    Hesaplama tarafı src/analyzer.py içinde kalır.
    Bu dosya sadece Streamlit UI tarafını yönetir.
    """
    st.markdown("---")
    st.header(
        t(
            "growth.title",
            language,
        )
    )
    st.caption(
        t(
            "growth.caption",
            language,
        )
    )

    try:
        growth_summary = get_growth_summary(
            covers_df,
            snapshots_df,
        )

        if growth_summary.empty:
            st.info(
                t(
                    "growth.insufficient_data",
                    language,
                )
            )
            return

        render_growth_summary(
            growth_summary,
            language=language,
        )

        render_selected_cover_snapshot_history(
            covers_df,
            snapshots_df,
            language=language,
        )

    except FileNotFoundError:
        st.warning(
            t(
                "growth.missing_snapshots_file",
                language,
            )
        )

    except Exception as error:
        st.error(f"{t('growth.load_error', language)}: {error}")


def render_growth_summary(
    growth_summary: pd.DataFrame,
    language: str,
) -> None:
    """
    Growth summary KPI kartlarını ve tabloyu gösterir.
    """
    st.subheader(
        t(
            "growth.summary.title",
            language,
        )
    )

    best_views_growth = growth_summary.sort_values(
        by="views_growth",
        ascending=False,
    ).iloc[0]

    best_likes_growth = growth_summary.sort_values(
        by="likes_growth",
        ascending=False,
    ).iloc[0]

    best_engagement_growth = growth_summary.sort_values(
        by="total_engagement_growth",
        ascending=False,
    ).iloc[0]

    growth_col1, growth_col2, growth_col3 = st.columns(3)

    growth_col1.metric(
        t(
            "growth.summary.best_views",
            language,
        ),
        best_views_growth["title"],
        int(best_views_growth["views_growth"]),
    )

    growth_col2.metric(
        t(
            "growth.summary.best_likes",
            language,
        ),
        best_likes_growth["title"],
        int(best_likes_growth["likes_growth"]),
    )

    growth_col3.metric(
        t(
            "growth.summary.best_engagement",
            language,
        ),
        best_engagement_growth["title"],
        int(best_engagement_growth["total_engagement_growth"]),
    )

    preferred_columns = [
        "cover_id",
        "title",
        "artist",
        "platform",
        "genre",
        "snapshot_count",
        "first_snapshot_date",
        "latest_snapshot_date",
        "views_growth",
        "likes_growth",
        "comments_growth",
        "saves_growth",
        "shares_growth",
        "total_engagement_growth",
        "views_growth_rate",
        "likes_growth_rate",
    ]

    available_columns = [
        column for column in preferred_columns if column in growth_summary.columns
    ]

    if available_columns:
        st.dataframe(
            growth_summary[available_columns],
            width="stretch",
        )
    else:
        st.dataframe(
            growth_summary,
            width="stretch",
        )

    with st.expander(
        t(
            "growth.summary.debug_columns",
            language,
        )
    ):
        st.write(list(growth_summary.columns))


def render_selected_cover_snapshot_history(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
    language: str,
) -> None:
    """
    Kullanıcının seçtiği cover için snapshot geçmişini
    ve trend grafiklerini gösterir.
    """
    st.markdown("---")
    st.subheader(
        t(
            "growth.history.title",
            language,
        )
    )

    growth_cover_options_df = covers_df.copy()

    if growth_cover_options_df.empty:
        st.info(
            t(
                "growth.history.no_covers",
                language,
            )
        )
        return

    growth_cover_options_df["display_name"] = (
        growth_cover_options_df["cover_id"]
        + " - "
        + growth_cover_options_df["title"]
        + " / "
        + growth_cover_options_df["artist"]
    )

    selected_growth_cover_display = st.selectbox(
        t(
            "growth.history.selector",
            language,
        ),
        growth_cover_options_df["display_name"].tolist(),
        key="growth_cover_selector",
    )

    selected_growth_cover_id = selected_growth_cover_display.split(" - ")[0]

    cover_history = get_cover_snapshot_history(
        snapshots_df=snapshots_df,
        cover_id=selected_growth_cover_id,
    )

    if cover_history.empty:
        st.info(
            t(
                "growth.history.no_history",
                language,
            )
        )
        return

    preferred_history_columns = [
        "snapshot_id",
        "snapshot_date",
        "views",
        "likes",
        "comments",
        "saves",
        "shares",
        "total_engagement",
        "engagement_rate",
    ]

    available_history_columns = [
        column
        for column in preferred_history_columns
        if column in cover_history.columns
    ]

    st.dataframe(
        cover_history[available_history_columns],
        hide_index=True,
        width="stretch",
    )

    chart_history = cover_history.copy()

    chart_history["snapshot_date"] = pd.to_datetime(
        chart_history["snapshot_date"],
        errors="coerce",
    )

    chart_history = chart_history.dropna(subset=["snapshot_date"])

    chart_history = chart_history.set_index("snapshot_date")

    if chart_history.empty:
        return

    st.subheader(
        t(
            "growth.history.views_trend",
            language,
        )
    )

    if "views" in chart_history.columns:
        st.line_chart(chart_history[["views"]])

    engagement_columns = [
        column
        for column in [
            "likes",
            "comments",
            "saves",
            "shares",
            "total_engagement",
        ]
        if column in chart_history.columns
    ]

    if engagement_columns:
        st.subheader(
            t(
                "growth.history.engagement_trend",
                language,
            )
        )

        st.line_chart(chart_history[engagement_columns])

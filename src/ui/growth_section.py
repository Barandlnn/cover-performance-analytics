import pandas as pd
import streamlit as st

from src.analyzer import (
    get_growth_summary,
    get_cover_snapshot_history,
)


def render_growth_section(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
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
    st.header("📈 Growth Analytics")
    st.caption("Cover'ların zaman içindeki performans gelişimini analiz eder.")

    try:
        growth_summary = get_growth_summary(covers_df, snapshots_df)

        if growth_summary.empty:
            st.info(
                "Growth analizi için henüz yeterli snapshot verisi yok. "
                "Bir cover için en az 2 snapshot gerekli."
            )
            return

        render_growth_summary(growth_summary)
        render_selected_cover_snapshot_history(covers_df, snapshots_df)

    except FileNotFoundError:
        st.warning(
            "metrics_snapshots.csv dosyası bulunamadı. "
            "Önce en az bir metric snapshot eklemelisin."
        )

    except Exception as error:
        st.error(f"Growth Analytics yüklenirken bir hata oluştu: {error}")


def render_growth_summary(growth_summary: pd.DataFrame) -> None:
    """
    Growth summary KPI kartlarını ve tabloyu gösterir.
    """

    st.subheader("🚀 Growth Summary")

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
        "Best Views Growth",
        best_views_growth["title"],
        int(best_views_growth["views_growth"]),
    )

    growth_col2.metric(
        "Best Likes Growth",
        best_likes_growth["title"],
        int(best_likes_growth["likes_growth"]),
    )

    growth_col3.metric(
        "Best Engagement Growth",
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
            use_container_width=True,
        )
    else:
        st.dataframe(growth_summary, use_container_width=True)

    with st.expander("Debug: Growth Summary Columns"):
        st.write(list(growth_summary.columns))


def render_selected_cover_snapshot_history(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
) -> None:
    """
    Kullanıcının seçtiği cover için snapshot geçmişini ve trend grafiklerini gösterir.
    """

    st.markdown("---")
    st.subheader("📊 Selected Cover Snapshot History")

    growth_cover_options_df = covers_df.copy()

    if growth_cover_options_df.empty:
        st.info("Snapshot geçmişi göstermek için önce en az bir cover eklemelisin.")
        return

    growth_cover_options_df["display_name"] = (
        growth_cover_options_df["cover_id"]
        + " - "
        + growth_cover_options_df["title"]
        + " / "
        + growth_cover_options_df["artist"]
    )

    selected_growth_cover_display = st.selectbox(
        "Select a cover to inspect snapshot history",
        growth_cover_options_df["display_name"].tolist(),
        key="growth_cover_selector",
    )

    selected_growth_cover_id = selected_growth_cover_display.split(" - ")[0]

    cover_history = get_cover_snapshot_history(
        snapshots_df=snapshots_df,
        cover_id=selected_growth_cover_id,
    )

    if cover_history.empty:
        st.info("Bu cover için henüz snapshot geçmişi bulunamadı.")
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
        column for column in preferred_history_columns if column in cover_history.columns
    ]

    st.dataframe(
        cover_history[available_history_columns],
        hide_index=True,
        use_container_width=True,
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

    st.subheader("📈 Views Trend")
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
        st.subheader("❤️ Engagement Trend")
        st.line_chart(chart_history[engagement_columns])
from pathlib import Path

import pandas as pd

from src.i18n import DEFAULT_LANGUAGE, t

METRIC_COLUMNS = ["views", "likes", "comments", "saves", "shares"]


def _validate_columns(
    df: pd.DataFrame, required_columns: list[str], file_name: str
) -> None:
    """
    Gerekli kolonlar var mı kontrol eder.
    Eksik kolon varsa anlaşılır hata verir.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"{file_name} içinde eksik kolonlar var: {missing_columns}")


def _prepare_snapshots(snapshots_df: pd.DataFrame) -> pd.DataFrame:
    """
    Snapshot verisini analiz için hazırlar:
    - snapshot_date datetime yapılır
    - metrik kolonları numeric yapılır
    - total_engagement hesaplanır
    """
    snapshots = snapshots_df.copy()

    _validate_columns(
        snapshots,
        ["cover_id", "snapshot_date", *METRIC_COLUMNS],
        "metrics_snapshots.csv",
    )

    snapshots["snapshot_date"] = pd.to_datetime(
        snapshots["snapshot_date"],
        errors="coerce",
    )

    snapshots = snapshots.dropna(subset=["snapshot_date"])

    for col in METRIC_COLUMNS:
        snapshots[col] = pd.to_numeric(snapshots[col], errors="coerce").fillna(0)

    snapshots["total_engagement"] = (
        snapshots["likes"]
        + snapshots["comments"]
        + snapshots["saves"]
        + snapshots["shares"]
    )

    sort_columns = ["cover_id", "snapshot_date"]

    if "snapshot_id" in snapshots.columns:
        sort_columns.append("snapshot_id")

    snapshots = snapshots.sort_values(by=sort_columns)

    return snapshots


def load_data(file_path: str | None = None) -> pd.DataFrame:
    """
    Backward compatibility wrapper.

    CSV okuma artık data_manager.py sorumluluğundadır.
    Eski load_data() çağrıları kırılmasın diye bu fonksiyon korunur.
    """
    from src.data_manager import load_current_cover_data

    return load_current_cover_data()

    for col in METRIC_COLUMNS:
        merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce").fillna(0)

    if "snapshot_date" in merged_df.columns:
        merged_df["snapshot_date"] = pd.to_datetime(
            merged_df["snapshot_date"],
            errors="coerce",
        ).dt.date.astype(str)

    return merged_df


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cover performans metriklerini hesaplar.

    total_engagement:
        likes + comments + saves + shares

    engagement_rate:
        total_engagement / views * 100

    performance_score:
        Şimdilik kural tabanlı ağırlıklı skor.
    """
    df = df.copy()

    for col in METRIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["total_engagement"] = df["likes"] + df["comments"] + df["saves"] + df["shares"]

    safe_views = df["views"].replace(0, pd.NA)

    df["engagement_rate"] = (df["total_engagement"] / safe_views) * 100
    df["save_rate"] = (df["saves"] / safe_views) * 100
    df["share_rate"] = (df["shares"] / safe_views) * 100
    df["comment_rate"] = (df["comments"] / safe_views) * 100

    df["performance_score"] = (
        df["engagement_rate"] * 4
        + df["save_rate"] * 10
        + df["share_rate"] * 12
        + df["comment_rate"] * 8
    )

    calculated_columns = [
        "engagement_rate",
        "save_rate",
        "share_rate",
        "comment_rate",
        "performance_score",
    ]

    for col in calculated_columns:
        df[col] = df[col].fillna(0).round(2)

    return df


def calculate_growth_metrics(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Her cover için ilk snapshot ile son snapshot arasındaki büyümeyi hesaplar.

    Growth:
        latest value - first value

    Growth rate:
        growth / first value

    Not:
        Growth analizi için aynı cover'ın en az 2 snapshot'ı olmalıdır.
    """
    if covers_df.empty or snapshots_df.empty:
        return pd.DataFrame()

    covers = covers_df.copy()
    snapshots = _prepare_snapshots(snapshots_df)

    _validate_columns(covers, ["cover_id"], "covers.csv")

    if snapshots.empty:
        return pd.DataFrame()

    snapshot_counts = (
        snapshots.groupby("cover_id").size().reset_index(name="snapshot_count")
    )

    first_snapshots = snapshots.groupby("cover_id", as_index=False).first()
    latest_snapshots = snapshots.groupby("cover_id", as_index=False).last()

    first_columns = ["cover_id", "snapshot_date", *METRIC_COLUMNS, "total_engagement"]
    latest_columns = ["cover_id", "snapshot_date", *METRIC_COLUMNS, "total_engagement"]

    first_snapshots = first_snapshots[first_columns].rename(
        columns={
            "snapshot_date": "first_snapshot_date",
            "views": "first_views",
            "likes": "first_likes",
            "comments": "first_comments",
            "saves": "first_saves",
            "shares": "first_shares",
            "total_engagement": "first_total_engagement",
        }
    )

    latest_snapshots = latest_snapshots[latest_columns].rename(
        columns={
            "snapshot_date": "latest_snapshot_date",
            "views": "latest_views",
            "likes": "latest_likes",
            "comments": "latest_comments",
            "saves": "latest_saves",
            "shares": "latest_shares",
            "total_engagement": "latest_total_engagement",
        }
    )

    growth_df = covers.merge(snapshot_counts, on="cover_id", how="left")
    growth_df = growth_df.merge(first_snapshots, on="cover_id", how="left")
    growth_df = growth_df.merge(latest_snapshots, on="cover_id", how="left")

    growth_df["snapshot_count"] = growth_df["snapshot_count"].fillna(0).astype(int)

    growth_df = growth_df[growth_df["snapshot_count"] >= 2].copy()

    if growth_df.empty:
        return pd.DataFrame()

    growth_df["views_growth"] = growth_df["latest_views"] - growth_df["first_views"]
    growth_df["likes_growth"] = growth_df["latest_likes"] - growth_df["first_likes"]
    growth_df["comments_growth"] = (
        growth_df["latest_comments"] - growth_df["first_comments"]
    )
    growth_df["saves_growth"] = growth_df["latest_saves"] - growth_df["first_saves"]
    growth_df["shares_growth"] = growth_df["latest_shares"] - growth_df["first_shares"]

    growth_df["total_engagement_growth"] = (
        growth_df["latest_total_engagement"] - growth_df["first_total_engagement"]
    )

    growth_df["views_growth_rate"] = growth_df.apply(
        lambda row: (
            row["views_growth"] / row["first_views"] if row["first_views"] > 0 else 0
        ),
        axis=1,
    )

    growth_df["likes_growth_rate"] = growth_df.apply(
        lambda row: (
            row["likes_growth"] / row["first_likes"] if row["first_likes"] > 0 else 0
        ),
        axis=1,
    )

    growth_df["engagement_growth_rate"] = growth_df.apply(
        lambda row: (
            row["total_engagement_growth"] / row["first_total_engagement"]
            if row["first_total_engagement"] > 0
            else 0
        ),
        axis=1,
    )

    rate_columns = [
        "views_growth_rate",
        "likes_growth_rate",
        "engagement_growth_rate",
    ]

    for col in rate_columns:
        growth_df[col] = growth_df[col].fillna(0).round(4)

    growth_df["first_snapshot_date"] = pd.to_datetime(
        growth_df["first_snapshot_date"],
        errors="coerce",
    ).dt.date.astype(str)

    growth_df["latest_snapshot_date"] = pd.to_datetime(
        growth_df["latest_snapshot_date"],
        errors="coerce",
    ).dt.date.astype(str)

    return growth_df


def get_growth_summary(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Growth metriklerini hesaplar ve en çok views_growth alan cover'ları sıralar.
    """
    growth_df = calculate_growth_metrics(covers_df, snapshots_df)

    if growth_df.empty:
        return pd.DataFrame()

    summary_columns = [
        "cover_id",
        "title",
        "artist",
        "platform",
        "genre",
        "snapshot_count",
        "first_snapshot_date",
        "latest_snapshot_date",
        "first_views",
        "latest_views",
        "views_growth",
        "views_growth_rate",
        "first_likes",
        "latest_likes",
        "likes_growth",
        "likes_growth_rate",
        "first_total_engagement",
        "latest_total_engagement",
        "total_engagement_growth",
        "engagement_growth_rate",
    ]

    available_columns = [col for col in summary_columns if col in growth_df.columns]

    growth_summary = growth_df[available_columns].copy()

    growth_summary = growth_summary.sort_values(
        by="views_growth",
        ascending=False,
    )

    return growth_summary


def get_cover_snapshot_history(
    snapshots_df: pd.DataFrame,
    cover_id: str,
) -> pd.DataFrame:
    """
    Seçilen cover'ın tüm snapshot geçmişini getirir.
    V1.6 çizgi grafik bölümünde kullanılacak.
    """
    if snapshots_df.empty:
        return pd.DataFrame()

    snapshots = _prepare_snapshots(snapshots_df)

    cover_history = snapshots[snapshots["cover_id"] == cover_id].copy()

    if cover_history.empty:
        return pd.DataFrame()

    cover_history = cover_history.sort_values(by="snapshot_date")

    cover_history["engagement_rate"] = cover_history.apply(
        lambda row: (
            row["total_engagement"] / row["views"] * 100 if row["views"] > 0 else 0
        ),
        axis=1,
    )

    cover_history["engagement_rate"] = cover_history["engagement_rate"].round(2)

    cover_history["snapshot_date"] = pd.to_datetime(
        cover_history["snapshot_date"],
        errors="coerce",
    ).dt.date.astype(str)

    return cover_history


def get_top_covers(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """
    En iyi performans veren cover'ları getirir.
    """
    if df.empty or "performance_score" not in df.columns:
        return pd.DataFrame()

    return df.sort_values(
        by="performance_score",
        ascending=False,
    ).head(limit)


def generate_insights(
    df: pd.DataFrame,
    best_cover: pd.Series,
    language: str = DEFAULT_LANGUAGE,
) -> list[str]:
    """
    Generate localized rule-based insights for the best performing cover.

    The analysis rules operate on the original dataset values.
    Only the user-facing insight messages are localized.
    """
    insights: list[str] = []

    if df.empty or best_cover.empty:
        return insights

    avg_views = df["views"].mean()
    avg_save_rate = df["save_rate"].mean()
    avg_share_rate = df["share_rate"].mean()
    avg_comment_rate = df["comment_rate"].mean()

    if best_cover["save_rate"] > avg_save_rate:
        insights.append(
            t(
                "analyzer.insights.above_average_save_rate",
                language,
            )
        )

    if best_cover["share_rate"] > avg_share_rate:
        insights.append(
            t(
                "analyzer.insights.above_average_share_rate",
                language,
            )
        )

    if best_cover["comment_rate"] > avg_comment_rate:
        insights.append(
            t(
                "analyzer.insights.above_average_comment_rate",
                language,
            )
        )

    if (
        best_cover["views"] < avg_views
        and best_cover["performance_score"] == df["performance_score"].max()
    ):
        insights.append(
            t(
                "analyzer.insights.best_score_below_average_views",
                language,
            )
        )

    if "hook_type" in best_cover.index:
        hook_type = best_cover["hook_type"]

        if hook_type == "direct chorus":
            insights.append(
                t(
                    "analyzer.insights.direct_chorus_hook",
                    language,
                )
            )

        elif hook_type == "slow intro":
            insights.append(
                t(
                    "analyzer.insights.slow_intro_hook",
                    language,
                )
            )

    if "vocal_style" in best_cover.index:
        vocal_style = best_cover["vocal_style"]

        if vocal_style in ["powerful", "emotional"]:
            insights.append(
                t(
                    "analyzer.insights.strong_vocal_style",
                    language,
                ).format(
                    vocal_style=vocal_style,
                )
            )

    if (
        "genre" in df.columns
        and "genre" in best_cover.index
        and "performance_score" in df.columns
    ):
        genre_performance = (
            df.dropna(subset=["genre"])
            .groupby("genre")["performance_score"]
            .mean()
            .sort_values(ascending=False)
        )

        if not genre_performance.empty:
            top_genre = genre_performance.index[0]

            if best_cover["genre"] == top_genre:
                insights.append(
                    t(
                        "analyzer.insights.strongest_genre",
                        language,
                    ).format(
                        genre=best_cover["genre"],
                    )
                )

    if len(df) < 10:
        insights.append(
            t(
                "analyzer.insights.small_dataset",
                language,
            )
        )

    return insights

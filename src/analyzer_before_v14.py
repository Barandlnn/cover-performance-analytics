import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    """
    CSV dosyasındaki cover verilerini okur.
    """
    return pd.read_csv(file_path)


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cover performans metriklerini hesaplar.
    """
    df = df.copy()

    df["total_engagement"] = df["likes"] + df["comments"] + df["saves"] + df["shares"]

    df["engagement_rate"] = (df["total_engagement"] / df["views"]) * 100
    df["save_rate"] = (df["saves"] / df["views"]) * 100
    df["share_rate"] = (df["shares"] / df["views"]) * 100
    df["comment_rate"] = (df["comments"] / df["views"]) * 100

    df["performance_score"] = (
        df["engagement_rate"] * 4
        + df["save_rate"] * 10
        + df["share_rate"] * 12
        + df["comment_rate"] * 8
    )

    df["engagement_rate"] = df["engagement_rate"].round(2)
    df["save_rate"] = df["save_rate"].round(2)
    df["share_rate"] = df["share_rate"].round(2)
    df["comment_rate"] = df["comment_rate"].round(2)
    df["performance_score"] = df["performance_score"].round(2)

    return df


def get_top_covers(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """
    En iyi performans veren cover'ları getirir.
    """
    return df.sort_values(by="performance_score", ascending=False).head(limit)


def generate_insights(df: pd.DataFrame, best_cover: pd.Series) -> list[str]:
    """
    En iyi cover üzerinden basit yorumlar üretir.
    Bu fonksiyon şimdilik kural tabanlı çalışır.
    """

    insights = []

    avg_views = df["views"].mean()
    avg_save_rate = df["save_rate"].mean()
    avg_share_rate = df["share_rate"].mean()
    avg_comment_rate = df["comment_rate"].mean()

    if best_cover["save_rate"] > avg_save_rate:
        insights.append(
            "This cover has an above-average save rate. "
            "This may suggest that people wanted to revisit or remember this performance."
        )

    if best_cover["share_rate"] > avg_share_rate:
        insights.append(
            "This cover has an above-average share rate. "
            "This may indicate that the song or performance felt shareable to the audience."
        )

    if best_cover["comment_rate"] > avg_comment_rate:
        insights.append(
            "This cover has an above-average comment rate. "
            "This may suggest that it triggered stronger audience reaction or discussion."
        )

    if (
        best_cover["views"] < avg_views
        and best_cover["performance_score"] == df["performance_score"].max()
    ):
        insights.append(
            "This cover did not have the highest view count, but it produced the best performance score. "
            "This means the audience quality may be stronger than the raw reach."
        )

    if best_cover["hook_type"] == "direct chorus":
        insights.append(
            "The cover starts with a direct chorus hook. "
            "This can work well because the audience reaches the recognizable part quickly."
        )

    elif best_cover["hook_type"] == "slow intro":
        insights.append(
            "The cover uses a slow intro. "
            "This may work well when the emotional buildup is strong, but it can also risk early drop-off."
        )

    if best_cover["vocal_style"] in ["powerful", "emotional"]:
        insights.append(
            f"The vocal style is {best_cover['vocal_style']}. "
            "This may be one reason why the cover created stronger engagement."
        )

    top_genre = (
        df.groupby("genre")["performance_score"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    if best_cover["genre"] == top_genre:
        insights.append(
            f"{best_cover['genre']} is currently the strongest genre in your dataset. "
            "You may want to test more covers in this direction."
        )

    if len(df) < 10:
        insights.append(
            "Your dataset is still small. "
            "Add at least 10 real covers before making strong content decisions."
        )

    return insights

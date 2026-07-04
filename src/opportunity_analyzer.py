import pandas as pd


REQUIRED_COLUMNS = [
    "song_title",
    "artist",
    "platform",
    "reference_creator",
    "content_type",
    "genre",
    "vibe",
    "views",
    "likes",
    "comments",
    "saves",
    "shares",
    "saturation_level",
    "production_fit",
    "audience_fit",
    "trend_strength",
    "notes",
]


def load_opportunity_signals(file_path: str) -> pd.DataFrame:
    """
    V3 Opportunity Finder için dış pazar / trend sinyallerini okur.

    Bu dosya bizim kendi cover performanslarımızı değil,
    piyasada gözlemlediğimiz fırsat sinyallerini temsil eder.
    """
    df = pd.read_csv(file_path)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"opportunity_signals.csv içinde eksik kolonlar var: {missing_columns}"
        )

    return df


def calculate_market_reaction_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pazar reaksiyonunu hesaplar.

    Basit mantık:
    - Views yüksekse ilgi var.
    - Like rate yüksekse içerik beğenilmiş.
    - Comment rate yüksekse duygusal/aktif reaksiyon var.
    - Save/share yüksekse içerik tekrar değerli bulunmuş.
    """
    df = df.copy()

    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0)
    df["saves"] = pd.to_numeric(df["saves"], errors="coerce").fillna(0)
    df["shares"] = pd.to_numeric(df["shares"], errors="coerce").fillna(0)

    df["like_rate"] = df.apply(
        lambda row: row["likes"] / row["views"] if row["views"] > 0 else 0,
        axis=1,
    )

    df["comment_rate"] = df.apply(
        lambda row: row["comments"] / row["views"] if row["views"] > 0 else 0,
        axis=1,
    )

    df["save_share_rate"] = df.apply(
        lambda row: (row["saves"] + row["shares"]) / row["views"]
        if row["views"] > 0
        else 0,
        axis=1,
    )

    # Normalize edilmiş kaba pazar skoru.
    # Burada amaç kusursuz istatistik değil, yorumlanabilir karar desteği.
    df["market_reaction_score"] = (
        (df["views"] / df["views"].max() * 40)
        + (df["like_rate"] / df["like_rate"].max() * 25)
        + (df["comment_rate"] / df["comment_rate"].max() * 20)
        + (df["save_share_rate"] / df["save_share_rate"].max() * 15)
    ).round(2)

    return df


def calculate_competition_gap_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rekabet boşluğu skorunu hesaplar.

    saturation_level:
    - low    → fırsat yüksek
    - medium → dengeli
    - high   → rekabet yoğun
    """
    df = df.copy()

    saturation_map = {
        "low": 100,
        "medium": 65,
        "high": 35,
    }

    df["competition_gap_score"] = (
        df["saturation_level"]
        .str.lower()
        .map(saturation_map)
        .fillna(50)
    )

    return df


def calculate_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genel fırsat skorunu hesaplar.

    V3.0 formülü:

    opportunity_score =
        market_reaction_score * 0.35
        + audience_fit * 10 * 0.25
        + production_fit * 10 * 0.20
        + competition_gap_score * 0.10
        + trend_strength * 10 * 0.10

    Neden böyle?
    - En büyük ağırlık pazar reaksiyonunda.
    - Sonra senin kitlene uyum geliyor.
    - Sonra üretim kalitesi / yapabilirlik.
    - Rekabet ve trend gücü destekleyici faktörler.
    """
    df = df.copy()

    df["production_fit"] = pd.to_numeric(
        df["production_fit"], errors="coerce"
    ).fillna(5)

    df["audience_fit"] = pd.to_numeric(
        df["audience_fit"], errors="coerce"
    ).fillna(5)

    df["trend_strength"] = pd.to_numeric(
        df["trend_strength"], errors="coerce"
    ).fillna(5)

    df = calculate_market_reaction_score(df)
    df = calculate_competition_gap_score(df)

    df["opportunity_score"] = (
        df["market_reaction_score"] * 0.35
        + (df["audience_fit"] * 10) * 0.25
        + (df["production_fit"] * 10) * 0.20
        + df["competition_gap_score"] * 0.10
        + (df["trend_strength"] * 10) * 0.10
    ).round(2)

    return df.sort_values(by="opportunity_score", ascending=False)


def classify_opportunity(score: float) -> str:
    """
    Opportunity score değerini okunabilir sınıfa çevirir.
    """
    if score >= 80:
        return "Strong Opportunity"
    elif score >= 65:
        return "Good Opportunity"
    elif score >= 50:
        return "Test First"
    else:
        return "Low Priority"


def generate_opportunity_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Her cover fırsatı için kısa karar önerisi üretir.
    """
    df = df.copy()

    df["opportunity_label"] = df["opportunity_score"].apply(classify_opportunity)

    def build_reason(row):
        reasons = []

        if row["market_reaction_score"] >= 75:
            reasons.append("strong market reaction")
        elif row["market_reaction_score"] >= 55:
            reasons.append("decent market reaction")
        else:
            reasons.append("limited market reaction")

        if row["audience_fit"] >= 8:
            reasons.append("high audience fit")
        elif row["audience_fit"] >= 6:
            reasons.append("moderate audience fit")
        else:
            reasons.append("weak audience fit")

        if row["production_fit"] >= 8:
            reasons.append("strong production fit")
        elif row["production_fit"] >= 6:
            reasons.append("manageable production fit")
        else:
            reasons.append("risky production fit")

        if row["competition_gap_score"] >= 80:
            reasons.append("low saturation")
        elif row["competition_gap_score"] >= 60:
            reasons.append("balanced saturation")
        else:
            reasons.append("high competition")

        return ", ".join(reasons)

    df["recommendation_reason"] = df.apply(build_reason, axis=1)

    return df
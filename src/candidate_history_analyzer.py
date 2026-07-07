import pandas as pd

from src.data_manager import load_candidate_tests_raw

REQUIRED_COLUMNS = [
    "test_date",
    "genre",
    "artist",
    "content_type",
    "candidate_score",
    "candidate_label",
    "needs_more_data_count",
    "action",
]


def load_candidate_history() -> pd.DataFrame:
    """
    Kaydedilmiş candidate test geçmişini data_manager üzerinden okur.

    Bu fonksiyon artık CSV path bilmez.
    Dosyanın nereden okunacağını src/data_manager.py yönetir.
    """
    try:
        df = load_candidate_tests_raw()
    except FileNotFoundError:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    return normalize_candidate_history(df)


def normalize_candidate_history(df: pd.DataFrame) -> pd.DataFrame:
    """
    Candidate history verisini güvenli analiz edilebilir hale getirir.
    Eksik kolonları tamamlar, numeric alanları dönüştürür.
    """
    df = df.copy()

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df["candidate_score"] = pd.to_numeric(
        df["candidate_score"],
        errors="coerce",
    ).fillna(0)

    df["needs_more_data_count"] = pd.to_numeric(
        df["needs_more_data_count"],
        errors="coerce",
    ).fillna(0)

    df["test_date"] = pd.to_datetime(
        df["test_date"],
        errors="coerce",
    )

    df = df.sort_values(
        by="test_date",
        ascending=False,
        na_position="last",
    )

    return df


def get_candidate_history_summary(df: pd.DataFrame) -> dict:
    """
    Candidate test geçmişi için genel özet metrikler üretir.
    """
    df = normalize_candidate_history(df)

    if df.empty:
        return {
            "total_tests": 0,
            "average_candidate_score": 0,
            "best_candidate_score": 0,
            "strong_candidate_count": 0,
            "promising_candidate_count": 0,
            "needs_more_data_count": 0,
        }

    strong_candidate_count = (
        df["candidate_label"].astype(str).str.contains(
            "Strong",
            case=False,
            na=False,
        )
    ).sum()

    promising_candidate_count = (
        df["candidate_label"].astype(str).str.contains(
            "Promising",
            case=False,
            na=False,
        )
    ).sum()

    needs_more_data_count = (
        df["candidate_label"].astype(str).str.contains(
            "Needs More Data",
            case=False,
            na=False,
        )
    ).sum()

    return {
        "total_tests": len(df),
        "average_candidate_score": round(df["candidate_score"].mean(), 2),
        "best_candidate_score": round(df["candidate_score"].max(), 2),
        "strong_candidate_count": int(strong_candidate_count),
        "promising_candidate_count": int(promising_candidate_count),
        "needs_more_data_count": int(needs_more_data_count),
    }


def get_top_candidates(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    En yüksek candidate_score alan testleri döndürür.
    """
    df = normalize_candidate_history(df)

    if df.empty:
        return pd.DataFrame()

    columns = [
        "test_date",
        "genre",
        "artist",
        "content_type",
        "candidate_score",
        "candidate_label",
        "action",
    ]

    available_columns = [column for column in columns if column in df.columns]

    return (
        df.sort_values(by="candidate_score", ascending=False)
        .head(top_n)[available_columns]
        .reset_index(drop=True)
    )


def get_genre_candidate_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genre bazında candidate test performansını hesaplar.
    """
    df = normalize_candidate_history(df)

    if df.empty or "genre" not in df.columns:
        return pd.DataFrame()

    genre_performance = (
        df.groupby("genre", dropna=False)
        .agg(
            test_count=("candidate_score", "count"),
            average_score=("candidate_score", "mean"),
            best_score=("candidate_score", "max"),
        )
        .reset_index()
    )

    genre_performance["average_score"] = genre_performance["average_score"].round(2)
    genre_performance["best_score"] = genre_performance["best_score"].round(2)

    return genre_performance.sort_values(
        by="average_score",
        ascending=False,
    )


def generate_candidate_history_insights(df: pd.DataFrame) -> list[str]:
    """
    Candidate test geçmişinden kısa yorumlar üretir.
    """
    df = normalize_candidate_history(df)

    if df.empty:
        return ["No candidate test history is available yet."]

    insights = []

    summary = get_candidate_history_summary(df)

    insights.append(
        f"You have tested {summary['total_tests']} candidate cover ideas so far."
    )

    insights.append(
        f"Average candidate score is {summary['average_candidate_score']}."
    )

    top_candidates_df = get_top_candidates(df, top_n=1)

    if not top_candidates_df.empty:
        top_candidate = top_candidates_df.iloc[0]

        insights.append(
            f"Best candidate so far: {top_candidate['genre']} / "
            f"{top_candidate['artist']} / {top_candidate['content_type']} "
            f"with score {top_candidate['candidate_score']}."
        )

    genre_performance_df = get_genre_candidate_performance(df)

    if not genre_performance_df.empty:
        best_genre = genre_performance_df.iloc[0]

        insights.append(
            f"Best tested genre is {best_genre['genre']} "
            f"with average score {best_genre['average_score']}."
        )

    if summary["strong_candidate_count"] > 0:
        insights.append(
            f"{summary['strong_candidate_count']} tests were classified as Strong Candidate."
        )

    if summary["needs_more_data_count"] > 0:
        insights.append(
            f"{summary['needs_more_data_count']} tests need more data before making a strong decision."
        )

    return insights
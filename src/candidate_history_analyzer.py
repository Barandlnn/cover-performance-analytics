import pandas as pd


def load_candidate_history(file_path: str) -> pd.DataFrame:
    """
    Candidate test geçmişini CSV dosyasından okur.
    Dosya yoksa veya boşsa boş DataFrame döndürür.
    """
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _find_column(df: pd.DataFrame, possible_names: list[str]) -> str | None:
    """
    DataFrame içinde farklı isimlerle tutulmuş olabilecek kolonları bulur.
    """
    existing_columns = list(df.columns)

    for name in possible_names:
        if name in existing_columns:
            return name

    return None


def _clean_text_value(value, fallback: str) -> str:
    """
    nan / None / boş string gibi değerleri temizler.
    """
    if pd.isna(value):
        return fallback

    text = str(value).strip()

    if text.lower() in ["", "nan", "none", "null", "nat"]:
        return fallback

    return text


def _normalize_score(score_series: pd.Series) -> pd.Series:
    """
    Candidate score değerini 0-100 aralığında tutar.

    Not:
    Bazı eski kayıtlar raw weighted score olarak 100 üstü gelmiş olabilir.
    V2 final dashboard tarafında score değerini 0-100 aralığına sıkıştırıyoruz.
    """
    score_series = pd.to_numeric(score_series, errors="coerce").fillna(0)

    return score_series.clip(lower=0, upper=100).round(2)


def _normalize_confidence(confidence_series: pd.Series | None, row_count: int) -> pd.Series:
    """
    Confidence değerini 0-100 aralığına getirir.
    Eğer eski kayıtlarda confidence yoksa 0 değil, NaN bırakılır.
    Böylece dashboard bunu 'Not tracked' olarak gösterebilir.
    """
    if confidence_series is None:
        return pd.Series([pd.NA] * row_count, dtype="Float64")

    confidence_series = pd.to_numeric(confidence_series, errors="coerce")

    return confidence_series.clip(lower=0, upper=100).round(2)


def normalize_candidate_history(df: pd.DataFrame) -> pd.DataFrame:
    """
    Candidate history verisini standart kolonlara çevirir.
    Eski / farklı kolon isimleriyle kaydedilmiş verileri de güvenli şekilde okur.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    candidate_name_col = _find_column(
        df,
        [
            "candidate_name",
            "candidate",
            "candidate_title",
            "candidate_cover",
            "candidate_song",
            "cover_candidate",
        ],
    )

    song_col = _find_column(
        df,
        [
            "song_title",
            "song",
            "song_name",
            "cover_title",
            "title",
            "target_song",
        ],
    )

    artist_col = _find_column(
        df,
        [
            "artist",
            "original_artist",
            "singer",
            "target_artist",
        ],
    )

    genre_col = _find_column(
        df,
        [
            "genre",
            "music_genre",
            "candidate_genre",
        ],
    )

    score_col = _find_column(
        df,
        [
            "candidate_score",
            "normalized_score",
            "final_score",
            "weighted_score",
            "score",
            "pattern_score",
        ],
    )

    raw_score_col = _find_column(
        df,
        [
            "raw_candidate_score",
            "raw_score",
            "weighted_score",
            "pattern_score",
            "score",
        ],
    )

    confidence_col = _find_column(
        df,
        [
            "confidence",
            "confidence_score",
            "confidence_level",
            "pattern_confidence",
            "candidate_confidence",
        ],
    )

    date_col = _find_column(
        df,
        [
            "test_date",
            "created_at",
            "date",
            "timestamp",
        ],
    )

    recommendation_col = _find_column(
        df,
        [
            "recommendation",
            "decision",
            "result",
            "candidate_recommendation",
        ],
    )

    normalized = pd.DataFrame()

    # Candidate name üretimi
    if candidate_name_col:
        normalized["candidate_name"] = df[candidate_name_col].apply(
            lambda value: _clean_text_value(value, "Unknown Candidate")
        )
    else:
        song_values = (
            df[song_col].apply(lambda value: _clean_text_value(value, "Unknown Song"))
            if song_col
            else pd.Series(["Unknown Song"] * len(df))
        )

        artist_values = (
            df[artist_col].apply(lambda value: _clean_text_value(value, "Unknown Artist"))
            if artist_col
            else pd.Series(["Unknown Artist"] * len(df))
        )

        normalized["candidate_name"] = song_values + " - " + artist_values

    # Song title
    if song_col:
        normalized["song_title"] = df[song_col].apply(
            lambda value: _clean_text_value(value, "Unknown Song")
        )
    else:
        normalized["song_title"] = normalized["candidate_name"]

    # Artist
    if artist_col:
        normalized["artist"] = df[artist_col].apply(
            lambda value: _clean_text_value(value, "Unknown Artist")
        )
    else:
        normalized["artist"] = "Unknown Artist"

    # Genre
    if genre_col:
        normalized["genre"] = df[genre_col].apply(
            lambda value: _clean_text_value(value, "Unknown")
        )
    else:
        normalized["genre"] = "Unknown"

    # Raw score saklanır
    if raw_score_col:
        normalized["raw_candidate_score"] = pd.to_numeric(
            df[raw_score_col],
            errors="coerce",
        ).fillna(0).round(2)
    elif score_col:
        normalized["raw_candidate_score"] = pd.to_numeric(
            df[score_col],
            errors="coerce",
        ).fillna(0).round(2)
    else:
        normalized["raw_candidate_score"] = 0

    # Dashboard score 0-100 aralığında tutulur
    if score_col:
        normalized["candidate_score"] = _normalize_score(df[score_col])
    else:
        normalized["candidate_score"] = 0

    # Confidence
    if confidence_col:
        normalized["confidence"] = _normalize_confidence(df[confidence_col], len(df))
        normalized["confidence_tracked"] = normalized["confidence"].notna()
    else:
        normalized["confidence"] = _normalize_confidence(None, len(df))
        normalized["confidence_tracked"] = False

    # Date
    if date_col:
        normalized["test_date"] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        normalized["test_date"] = pd.NaT

    # Recommendation
    if recommendation_col:
        normalized["recommendation"] = df[recommendation_col].apply(
            lambda value: _clean_text_value(value, "No recommendation")
        )
    else:
        normalized["recommendation"] = normalized["candidate_score"].apply(
            lambda score: (
                "Strong candidate"
                if score >= 75
                else "Testable candidate"
                if score >= 60
                else "Risky candidate"
            )
        )

    return normalized


def get_candidate_history_summary(df: pd.DataFrame) -> dict:
    """
    Candidate test geçmişinden temel özet metrikleri üretir.
    """
    if df.empty:
        return {
            "total_tests": 0,
            "average_score": 0,
            "best_candidate": "-",
            "best_score": 0,
            "average_confidence": "Not tracked",
        }

    best_row = df.sort_values("candidate_score", ascending=False).iloc[0]

    tracked_confidence_df = df[df["confidence_tracked"] == True]

    if tracked_confidence_df.empty:
        average_confidence = "Not tracked"
    else:
        average_confidence = round(tracked_confidence_df["confidence"].mean(), 2)

    return {
        "total_tests": len(df),
        "average_score": round(df["candidate_score"].mean(), 2),
        "best_candidate": best_row["candidate_name"],
        "best_score": round(best_row["candidate_score"], 2),
        "average_confidence": average_confidence,
    }


def get_top_candidates(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """
    En yüksek skorlu candidate testlerini döndürür.
    Display tarafı için confidence değerini güvenli şekilde gösterir.
    """
    if df.empty:
        return pd.DataFrame()

    columns = [
        "candidate_name",
        "genre",
        "candidate_score",
        "raw_candidate_score",
        "confidence",
        "recommendation",
        "test_date",
    ]

    result_df = (
        df.sort_values("candidate_score", ascending=False)
        .head(limit)[columns]
        .reset_index(drop=True)
    )

    # Float64 kolona direkt string basamayız.
    # Bu yüzden önce object/string gösterim kolonuna çeviriyoruz.
    result_df["confidence"] = result_df["confidence"].astype("object")
    result_df["confidence"] = result_df["confidence"].where(
        result_df["confidence"].notna(),
        "Not tracked"
    )

    return result_df

def get_genre_candidate_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genre bazında candidate score ortalamasını hesaplar.
    Confidence yoksa 'Not tracked' olarak güvenli şekilde gösterir.
    """
    if df.empty or "genre" not in df.columns:
        return pd.DataFrame()

    grouped_df = (
        df.groupby("genre", as_index=False)
        .agg(
            average_score=("candidate_score", "mean"),
            test_count=("candidate_score", "count"),
            average_raw_score=("raw_candidate_score", "mean"),
        )
        .sort_values("average_score", ascending=False)
        .round(2)
    )

    tracked_confidence_df = df[df["confidence_tracked"] == True]

    if not tracked_confidence_df.empty:
        confidence_df = (
            tracked_confidence_df.groupby("genre", as_index=False)
            .agg(average_confidence=("confidence", "mean"))
            .round(2)
        )

        grouped_df = grouped_df.merge(confidence_df, on="genre", how="left")
    else:
        grouped_df["average_confidence"] = pd.NA

    # Burada da aynı problem vardı:
    # Sayısal kolona direkt "Not tracked" yazarsak pandas hata verir.
    grouped_df["average_confidence"] = grouped_df["average_confidence"].astype("object")
    grouped_df["average_confidence"] = grouped_df["average_confidence"].where(
        grouped_df["average_confidence"].notna(),
        "Not tracked"
    )

    return grouped_df


def generate_candidate_history_insights(df: pd.DataFrame) -> list[str]:
    """
    Candidate test geçmişinden okunabilir insight üretir.
    """
    insights = []

    if df.empty:
        return [
            "Henüz candidate test geçmişi yok. V2.8 analizleri için önce birkaç candidate test kaydı oluşturmalısın."
        ]

    total_tests = len(df)
    average_score = df["candidate_score"].mean()

    insights.append(
        f"Şu ana kadar {total_tests} candidate test yapılmış. Ortalama candidate score {average_score:.2f}."
    )

    best_row = df.sort_values("candidate_score", ascending=False).iloc[0]

    insights.append(
        f"Geçmiş testlerde en güçlü aday şu an '{best_row['candidate_name']}' görünüyor. Score: {best_row['candidate_score']:.2f}."
    )

    if average_score >= 75:
        insights.append(
            "Genel candidate kalitesi güçlü görünüyor. Test edilen fikirlerin çoğu yayın planına alınabilecek seviyede."
        )
    elif average_score >= 60:
        insights.append(
            "Candidate kalitesi orta-iyi seviyede. Bazı fikirler yayınlanabilir; seçim yaparken genre uyumu ve geçmiş pattern sonuçları birlikte değerlendirilmeli."
        )
    else:
        insights.append(
            "Candidate kalitesi şu an düşük görünüyor. Yeni aday seçimlerinde daha önce iyi çalışan pattern'lere yakın fikirler denenmeli."
        )

    tracked_confidence_df = df[df["confidence_tracked"] == True]

    if tracked_confidence_df.empty:
        insights.append(
            "Eski candidate kayıtlarında confidence bilgisi tutulmamış. Bundan sonraki testlerde confidence kaydedilirse sistem daha güvenilir geçmiş analizi yapabilir."
        )
    else:
        average_confidence = tracked_confidence_df["confidence"].mean()

        if average_confidence >= 70:
            insights.append(
                "Confidence ortalaması güçlü. Sistem geçmiş pattern'lere dayanarak daha güvenli yorum yapabiliyor."
            )
        elif average_confidence >= 40:
            insights.append(
                "Confidence orta seviyede. Daha fazla cover verisi eklendikçe önerilerin güvenilirliği artacaktır."
            )
        else:
            insights.append(
                "Confidence düşük. Şu an öneriler dikkatli yorumlanmalı; veri miktarı arttıkça sistem daha sağlıklı karar verir."
            )

    genre_performance = get_genre_candidate_performance(df)

    if not genre_performance.empty:
        best_genre_row = genre_performance.iloc[0]

        insights.append(
            f"Genre bazında en güçlü alan '{best_genre_row['genre']}' görünüyor. Ortalama score: {best_genre_row['average_score']:.2f}."
        )

    dated_df = df.dropna(subset=["test_date"]).sort_values("test_date")

    if len(dated_df) >= 6:
        previous_avg = dated_df.iloc[:-3]["candidate_score"].mean()
        recent_avg = dated_df.iloc[-3:]["candidate_score"].mean()

        if recent_avg > previous_avg:
            insights.append(
                "Son candidate testlerinde skor trendi yükseliyor. Bu, daha doğru cover fikirleri seçmeye başladığını gösterebilir."
            )
        elif recent_avg < previous_avg:
            insights.append(
                "Son candidate testlerinde skor trendi düşüyor. Yeni aday seçimlerinde önceki güçlü pattern'lere geri bakmak faydalı olabilir."
            )
        else:
            insights.append(
                "Son candidate testlerinde skor trendi stabil. Büyük bir yükseliş ya da düşüş görünmüyor."
            )

    if not tracked_confidence_df.empty:
        average_confidence = tracked_confidence_df["confidence"].mean()

        high_score_low_confidence = df[
            (df["candidate_score"] >= average_score)
            & (df["confidence_tracked"] == True)
            & (df["confidence"] < average_confidence)
        ]

        if not high_score_low_confidence.empty:
            candidate = high_score_low_confidence.sort_values(
                "candidate_score",
                ascending=False,
            ).iloc[0]

            insights.append(
                f"'{candidate['candidate_name']}' yüksek score almış ama confidence görece düşük. Bu aday manuel değerlendirme için iyi bir seçenek olabilir."
            )

    return insights
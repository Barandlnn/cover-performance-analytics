import pandas as pd

try:
    from src.analyzer import calculate_metrics
except Exception:
    try:
        from analyzer import calculate_metrics
    except Exception:
        calculate_metrics = None


METRIC_COLUMNS = ["views", "likes", "comments", "saves", "shares"]


def _find_cover_id_columns(covers_df: pd.DataFrame, snapshots_df: pd.DataFrame) -> tuple[str, str]:
    """
    covers.csv ve metrics_snapshots.csv arasındaki ortak ID kolonlarını bulur.
    V1.4/V1.6 yapısında genelde cover_id kullanıyoruz.
    """

    if "cover_id" in covers_df.columns and "cover_id" in snapshots_df.columns:
        return "cover_id", "cover_id"

    if "id" in covers_df.columns and "cover_id" in snapshots_df.columns:
        return "id", "cover_id"

    raise ValueError(
        "Cover ID kolonu bulunamadı. covers.csv içinde 'cover_id' veya 'id', "
        "metrics_snapshots.csv içinde 'cover_id' olmalı."
    )


def _ensure_numeric_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Metrik kolonlarını sayısal hale getirir.
    Eksik kolon varsa 0 olarak ekler.
    """

    df = df.copy()

    for column in METRIC_COLUMNS:
        if column not in df.columns:
            df[column] = 0

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    return df


def _get_latest_snapshots(
    snapshots_df: pd.DataFrame,
    snapshot_id_column: str,
) -> pd.DataFrame:
    """
    Her cover için en güncel snapshot satırını döndürür.
    """

    if snapshots_df.empty:
        return pd.DataFrame()

    df = snapshots_df.copy()
    df = _ensure_numeric_metrics(df)

    if "snapshot_date" not in df.columns:
        raise ValueError("metrics_snapshots.csv içinde 'snapshot_date' kolonu bulunmalı.")

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    latest_df = (
        df.sort_values("snapshot_date")
        .groupby(snapshot_id_column, as_index=False)
        .tail(1)
        .copy()
    )

    latest_df = latest_df.rename(columns={snapshot_id_column: "__cover_key"})

    return latest_df


def _calculate_growth_by_cover(
    snapshots_df: pd.DataFrame,
    snapshot_id_column: str,
) -> pd.DataFrame:
    """
    Her cover için ilk snapshot ile son snapshot arasındaki büyümeyi hesaplar.
    """

    if snapshots_df.empty:
        return pd.DataFrame()

    df = snapshots_df.copy()
    df = _ensure_numeric_metrics(df)

    if "snapshot_date" not in df.columns:
        raise ValueError("metrics_snapshots.csv içinde 'snapshot_date' kolonu bulunmalı.")

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")
    df = df.sort_values("snapshot_date")

    first_df = df.groupby(snapshot_id_column).first()
    last_df = df.groupby(snapshot_id_column).last()

    growth_df = pd.DataFrame(index=last_df.index)

    for column in METRIC_COLUMNS:
        growth_df[f"{column}_growth"] = last_df[column] - first_df[column]

    growth_df["snapshot_count"] = df.groupby(snapshot_id_column).size()

    growth_df = growth_df.reset_index()
    growth_df = growth_df.rename(columns={snapshot_id_column: "__cover_key"})

    return growth_df


def _calculate_fallback_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    analyzer.py içindeki calculate_metrics fonksiyonu çalışmazsa
    basit bir yedek metrik hesaplama yapar.
    """

    df = df.copy()
    df = _ensure_numeric_metrics(df)

    df["total_engagement"] = (
        df["likes"] + df["comments"] + df["saves"] + df["shares"]
    )

    df["engagement_rate"] = (
        df["total_engagement"] / df["views"].replace(0, pd.NA) * 100
    ).fillna(0)

    df["save_rate"] = (
        df["saves"] / df["views"].replace(0, pd.NA) * 100
    ).fillna(0)

    df["share_rate"] = (
        df["shares"] / df["views"].replace(0, pd.NA) * 100
    ).fillna(0)

    df["performance_score"] = (
        df["engagement_rate"] * 0.70
        + df["save_rate"] * 0.20
        + df["share_rate"] * 0.10
    )

    return df


def _apply_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Öncelik V1'deki calculate_metrics fonksiyonunu kullanmak.
    Böylece eski dashboard ile V2 analizleri aynı skor mantığını paylaşır.
    """

    if calculate_metrics is not None:
        try:
            return calculate_metrics(df)
        except Exception:
            return _calculate_fallback_metrics(df)

    return _calculate_fallback_metrics(df)


def prepare_pattern_dataset(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    V2 pattern analizi için ana veri setini hazırlar.

    Yapılan işlem:
    1. covers.csv alınır.
    2. Her cover'ın en güncel snapshot'ı bulunur.
    3. İlk-son snapshot büyümesi hesaplanır.
    4. Performans metrikleri eklenir.
    """

    covers_id_column, snapshots_id_column = _find_cover_id_columns(
        covers_df,
        snapshots_df,
    )

    covers = covers_df.copy()
    covers["__cover_key"] = covers[covers_id_column]

    latest_snapshots = _get_latest_snapshots(
        snapshots_df,
        snapshots_id_column,
    )

    growth_df = _calculate_growth_by_cover(
        snapshots_df,
        snapshots_id_column,
    )

    merged_df = covers.merge(
        latest_snapshots,
        on="__cover_key",
        how="left",
        suffixes=("", "_latest_snapshot"),
    )

    if not growth_df.empty:
        merged_df = merged_df.merge(
            growth_df,
            on="__cover_key",
            how="left",
        )

    merged_df = _ensure_numeric_metrics(merged_df)
    merged_df = _apply_metrics(merged_df)

    growth_columns = [column for column in merged_df.columns if column.endswith("_growth")]
    for column in growth_columns:
        merged_df[column] = pd.to_numeric(merged_df[column], errors="coerce").fillna(0)

    if "snapshot_count" in merged_df.columns:
        merged_df["snapshot_count"] = pd.to_numeric(
            merged_df["snapshot_count"],
            errors="coerce",
        ).fillna(0)

    return merged_df


def get_pattern_summary(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
    group_by_column: str,
) -> pd.DataFrame:
    """
    Seçilen kategoriye göre performans özeti çıkarır.

    V2.2 güncellemesi:
    - confidence_level
    - confidence_weight
    - weighted_pattern_score
    - decision_label
    """

    df = prepare_pattern_dataset(covers_df, snapshots_df)

    if group_by_column not in df.columns:
        return pd.DataFrame()

    df[group_by_column] = (
        df[group_by_column]
        .fillna("Unknown")
        .astype(str)
        .replace("", "Unknown")
    )

    summary_df = (
        df.groupby(group_by_column)
        .agg(
            cover_count=("__cover_key", "nunique"),
            avg_views=("views", "mean"),
            avg_likes=("likes", "mean"),
            avg_comments=("comments", "mean"),
            avg_saves=("saves", "mean"),
            avg_shares=("shares", "mean"),
            avg_total_engagement=("total_engagement", "mean"),
            avg_engagement_rate=("engagement_rate", "mean"),
            avg_performance_score=("performance_score", "mean"),
            avg_views_growth=("views_growth", "mean"),
            avg_likes_growth=("likes_growth", "mean"),
        )
        .reset_index()
    )

    summary_df["confidence_level"] = summary_df["cover_count"].apply(
        lambda count: _get_confidence_level(int(count))
    )

    summary_df["confidence_weight"] = summary_df["cover_count"].apply(
        lambda count: _get_confidence_weight(int(count))
    )

    summary_df["weighted_pattern_score"] = (
        summary_df["avg_performance_score"] * summary_df["confidence_weight"]
    )

    summary_df["decision_label"] = summary_df.apply(
        lambda row: _get_decision_label(
            row["confidence_level"],
            row["weighted_pattern_score"],
        ),
        axis=1,
    )

    numeric_columns = summary_df.select_dtypes(include="number").columns
    summary_df[numeric_columns] = summary_df[numeric_columns].round(2)

    summary_df = summary_df.sort_values(
        by=["weighted_pattern_score", "cover_count"],
        ascending=[False, False],
    )

    return summary_df


def get_all_pattern_summaries(
    covers_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Dashboard'da kullanmak için temel pattern analizlerini topluca döndürür.
    """

    possible_dimensions = ["genre", "artist", "content_type"]

    summaries = {}

    for dimension in possible_dimensions:
        if dimension in covers_df.columns:
            summaries[dimension] = get_pattern_summary(
                covers_df,
                snapshots_df,
                dimension,
            )

    return summaries

def _get_confidence_level(cover_count: int) -> str:
    """
    Pattern sonucunun kaç cover üzerinden geldiğine göre güven seviyesi üretir.
    """

    if cover_count >= 5:
        return "High"

    if cover_count >= 3:
        return "Medium"

    return "Low"
def _get_confidence_weight(cover_count: int) -> float:
    """
    Cover sayısına göre ağırlık verir.
    Az veri varsa skorun etkisini düşürür.
    """

    if cover_count >= 5:
        return 1.00

    if cover_count >= 3:
        return 0.75

    if cover_count == 2:
        return 0.55

    return 0.35


def _get_decision_label(confidence_level: str, weighted_score: float) -> str:
    """
    Pattern sonucunu karar etiketi haline getirir.
    """

    if confidence_level == "High" and weighted_score >= 100:
        return "Strong Pattern"

    if confidence_level in ["Medium", "High"] and weighted_score >= 60:
        return "Promising Pattern"

    if confidence_level == "Low":
        return "Needs More Data"

    return "Weak Pattern"


def _get_recommendation_text(decision_label: str) -> str:
    """
    Karar etiketine göre aksiyon önerisi üretir.
    """

    if decision_label == "Strong Pattern":
        return "Prioritize this pattern in future cover planning."

    if decision_label == "Promising Pattern":
        return "Test this pattern with a few more covers."

    if decision_label == "Needs More Data":
        return "Do not make a strong decision yet; collect more data first."

    return "This pattern is not strong enough to prioritize right now."


def generate_pattern_insights(pattern_summaries: dict[str, pd.DataFrame]) -> list[str]:
    """
    Weighted pattern summary tablolarından okunabilir insight cümleleri üretir.

    V2.3 güncellemesi:
    - avg_performance_score yerine weighted_pattern_score kullanır.
    - decision_label bilgisini yorumlara ekler.
    - confidence seviyesine göre aksiyon önerisi üretir.
    """

    insights = []

    dimension_names = {
        "genre": "genre",
        "artist": "artist",
        "content_type": "content type",
    }

    for dimension, summary_df in pattern_summaries.items():
        if summary_df.empty:
            continue

        readable_dimension = dimension_names.get(dimension, dimension)

        best_row = summary_df.iloc[0]

        best_name = best_row[dimension]
        avg_score = best_row["avg_performance_score"]
        weighted_score = best_row["weighted_pattern_score"]
        cover_count = int(best_row["cover_count"])
        confidence = best_row["confidence_level"]
        decision_label = best_row["decision_label"]
        recommendation = _get_recommendation_text(decision_label)

        insights.append(
            f"Best weighted {readable_dimension}: {best_name}. "
            f"Weighted pattern score is {weighted_score}, while raw average score is {avg_score}. "
            f"This result is based on {cover_count} cover(s), confidence is {confidence.lower()}, "
            f"and the decision label is '{decision_label}'. "
            f"{recommendation}"
        )

        if len(summary_df) > 1:
            second_row = summary_df.iloc[1]

            second_name = second_row[dimension]
            second_weighted_score = second_row["weighted_pattern_score"]

            weighted_gap = round(weighted_score - second_weighted_score, 2)

            insights.append(
                f"{best_name} is ahead of {second_name} by {weighted_gap} weighted score points "
                f"in the {readable_dimension} analysis."
            )

        needs_more_data_rows = summary_df[
            summary_df["decision_label"] == "Needs More Data"
        ]

        if not needs_more_data_rows.empty:
            needs_more_data_names = ", ".join(
                needs_more_data_rows[dimension].astype(str).head(3).tolist()
            )

            insights.append(
                f"Some {readable_dimension} patterns look interesting but still need more data: "
                f"{needs_more_data_names}."
            )

    if not insights:
        insights.append("Not enough pattern data is available yet.")

    return insights

def _get_recommendation_priority(decision_label: str) -> str:
    """
    Karar etiketine göre planlama önceliği verir.
    """

    if decision_label == "Strong Pattern":
        return "High Priority"

    if decision_label == "Promising Pattern":
        return "Medium Priority"

    if decision_label == "Needs More Data":
        return "Data Needed"

    return "Low Priority"


def _get_planning_action(readable_dimension: str, decision_label: str) -> str:
    """
    Karar etiketine göre cover planlama aksiyonu üretir.
    """

    if decision_label == "Strong Pattern":
        return f"Plan more covers using this {readable_dimension}."

    if decision_label == "Promising Pattern":
        return f"Test this {readable_dimension} with 2-3 more covers."

    if decision_label == "Needs More Data":
        return f"Collect more data before making a strong decision about this {readable_dimension}."

    return f"Do not prioritize this {readable_dimension} right now."


def generate_pattern_recommendations(
    pattern_summaries: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Pattern summary sonuçlarından cover planlama önerileri üretir.

    V2.4:
    - dimension
    - pattern
    - priority
    - decision_label
    - action
    - reason
    """

    records = []

    dimension_names = {
        "genre": "genre",
        "artist": "artist",
        "content_type": "content type",
    }

    priority_rank = {
        "High Priority": 4,
        "Medium Priority": 3,
        "Data Needed": 2,
        "Low Priority": 1,
    }

    for dimension, summary_df in pattern_summaries.items():
        if summary_df.empty:
            continue

        readable_dimension = dimension_names.get(dimension, dimension)

        for _, row in summary_df.iterrows():
            pattern_name = row[dimension]
            cover_count = int(row["cover_count"])
            avg_score = row["avg_performance_score"]
            weighted_score = row["weighted_pattern_score"]
            confidence = row["confidence_level"]
            decision_label = row["decision_label"]

            priority = _get_recommendation_priority(decision_label)
            action = _get_planning_action(readable_dimension, decision_label)

            reason = (
                f"{pattern_name} has a raw average score of {avg_score}, "
                f"a weighted score of {weighted_score}, "
                f"{cover_count} cover(s), and {confidence.lower()} confidence."
            )

            records.append(
                {
                    "dimension": readable_dimension,
                    "pattern": pattern_name,
                    "priority": priority,
                    "decision_label": decision_label,
                    "cover_count": cover_count,
                    "weighted_pattern_score": weighted_score,
                    "action": action,
                    "reason": reason,
                    "_priority_rank": priority_rank.get(priority, 0),
                }
            )

    if not records:
        return pd.DataFrame()

    recommendations_df = pd.DataFrame(records)

    recommendations_df = recommendations_df.sort_values(
        by=["_priority_rank", "weighted_pattern_score", "cover_count"],
        ascending=[False, False, False],
    )

    recommendations_df = recommendations_df.drop(columns=["_priority_rank"])

    return recommendations_df
def _get_decision_multiplier(decision_label: str) -> float:
    """
    Candidate scoring için karar etiketini sayısal etkiye çevirir.
    """

    if decision_label == "Strong Pattern":
        return 1.00

    if decision_label == "Promising Pattern":
        return 0.80

    if decision_label == "Needs More Data":
        return 0.45

    return 0.20


def _get_candidate_label(candidate_score: float, needs_more_data_count: int) -> str:
    """
    Candidate score sonucunu okunabilir etikete çevirir.
    """

    if needs_more_data_count >= 2 and candidate_score >= 120:
        return "Interesting but Needs More Data"

    if candidate_score >= 200:
        return "Strong Candidate"

    if candidate_score >= 100:
        return "Promising Candidate"

    if candidate_score >= 40:
        return "Experimental Candidate"

    return "Weak Candidate"


def _get_candidate_action(candidate_label: str) -> str:
    """
    Candidate label'a göre aksiyon önerisi üretir.
    """

    if candidate_label == "Strong Candidate":
        return "This is a strong cover idea. It is reasonable to prioritize it."

    if candidate_label == "Promising Candidate":
        return "This cover idea is worth testing soon."

    if candidate_label == "Interesting but Needs More Data":
        return "This idea looks interesting, but you should test it carefully and collect more data."

    if candidate_label == "Experimental Candidate":
        return "This can be tested as an experiment, but do not prioritize it over stronger patterns."

    return "This idea is weak based on the current dataset."


def score_cover_candidate(
    pattern_summaries: dict[str, pd.DataFrame],
    candidate: dict[str, str],
) -> tuple[pd.DataFrame, dict]:
    """
    Yeni bir cover fikrini mevcut pattern sonuçlarına göre skorlar.

    Candidate örneği:
    {
        "genre": "Rap",
        "artist": "Sagopa-Kajmer",
        "content_type": "Reels",
    }
    """

    dimension_weights = {
        "genre": 0.35,
        "artist": 0.25,
        "content_type": 0.40,
    }

    dimension_names = {
        "genre": "genre",
        "artist": "artist",
        "content_type": "content type",
    }

    records = []
    total_score = 0
    needs_more_data_count = 0

    for dimension, selected_pattern in candidate.items():
        if not selected_pattern:
            continue

        readable_dimension = dimension_names.get(dimension, dimension)
        dimension_weight = dimension_weights.get(dimension, 0)

        summary_df = pattern_summaries.get(dimension)

        if summary_df is None or summary_df.empty or dimension not in summary_df.columns:
            records.append(
                {
                    "dimension": readable_dimension,
                    "selected_pattern": selected_pattern,
                    "status": "Not Found",
                    "weighted_pattern_score": 0,
                    "decision_label": "Unknown",
                    "confidence_level": "Unknown",
                    "dimension_weight": dimension_weight,
                    "candidate_contribution": 0,
                }
            )
            continue

        matched_rows = summary_df[
            summary_df[dimension].astype(str) == str(selected_pattern)
        ]

        if matched_rows.empty:
            records.append(
                {
                    "dimension": readable_dimension,
                    "selected_pattern": selected_pattern,
                    "status": "Not Found",
                    "weighted_pattern_score": 0,
                    "decision_label": "Unknown",
                    "confidence_level": "Unknown",
                    "dimension_weight": dimension_weight,
                    "candidate_contribution": 0,
                }
            )
            continue

        row = matched_rows.iloc[0]

        weighted_pattern_score = row["weighted_pattern_score"]
        decision_label = row["decision_label"]
        confidence_level = row["confidence_level"]

        decision_multiplier = _get_decision_multiplier(decision_label)

        candidate_contribution = (
            weighted_pattern_score
            * dimension_weight
            * decision_multiplier
        )

        if decision_label == "Needs More Data":
            needs_more_data_count += 1

        total_score += candidate_contribution

        records.append(
            {
                "dimension": readable_dimension,
                "selected_pattern": selected_pattern,
                "status": "Matched",
                "weighted_pattern_score": round(weighted_pattern_score, 2),
                "decision_label": decision_label,
                "confidence_level": confidence_level,
                "dimension_weight": dimension_weight,
                "candidate_contribution": round(candidate_contribution, 2),
            }
        )

    details_df = pd.DataFrame(records)

    candidate_score = round(total_score, 2)
    candidate_label = _get_candidate_label(candidate_score, needs_more_data_count)
    candidate_action = _get_candidate_action(candidate_label)

    summary = {
        "candidate_score": candidate_score,
        "candidate_label": candidate_label,
        "needs_more_data_count": needs_more_data_count,
        "action": candidate_action,
    }

    return details_df, summary

def generate_candidate_explanations(
    candidate_details_df: pd.DataFrame,
    candidate_summary: dict,
) -> list[str]:
    """
    Candidate test sonucundan okunabilir açıklamalar üretir.
    """

    explanations = []

    if candidate_details_df.empty:
        return ["No candidate details are available."]

    candidate_label = candidate_summary.get("candidate_label", "Unknown")
    candidate_score = candidate_summary.get("candidate_score", 0)
    needs_more_data_count = candidate_summary.get("needs_more_data_count", 0)

    explanations.append(
        f"This candidate is classified as '{candidate_label}' with a score of {candidate_score}."
    )

    strong_rows = candidate_details_df[
        candidate_details_df["decision_label"] == "Strong Pattern"
    ]

    promising_rows = candidate_details_df[
        candidate_details_df["decision_label"] == "Promising Pattern"
    ]

    needs_data_rows = candidate_details_df[
        candidate_details_df["decision_label"] == "Needs More Data"
    ]

    not_found_rows = candidate_details_df[
        candidate_details_df["status"] == "Not Found"
    ]

    if not strong_rows.empty:
        strong_parts = ", ".join(
            strong_rows["selected_pattern"].astype(str).tolist()
        )

        explanations.append(
            f"The strongest support for this candidate comes from: {strong_parts}."
        )

    if not promising_rows.empty:
        promising_parts = ", ".join(
            promising_rows["selected_pattern"].astype(str).tolist()
        )

        explanations.append(
            f"These parts look promising but still need more validation: {promising_parts}."
        )

    if not needs_data_rows.empty:
        needs_data_parts = ", ".join(
            needs_data_rows["selected_pattern"].astype(str).tolist()
        )

        explanations.append(
            f"These parts need more data before making a strong decision: {needs_data_parts}."
        )

    if not not_found_rows.empty:
        not_found_parts = ", ".join(
            not_found_rows["selected_pattern"].astype(str).tolist()
        )

        explanations.append(
            f"These selected patterns were not found in the current dataset: {not_found_parts}."
        )

    if needs_more_data_count >= 2:
        explanations.append(
            "This idea should be tested carefully because multiple parts of the candidate have low data confidence."
        )

    if candidate_label == "Strong Candidate":
        explanations.append(
            "This cover idea can be prioritized in the near-term cover plan."
        )

    elif candidate_label == "Promising Candidate":
        explanations.append(
            "This cover idea can be added to the near-term testing list."
        )

    elif candidate_label == "Interesting but Needs More Data":
        explanations.append(
            "This idea is not a guaranteed priority yet, but it is worth testing carefully because at least one part of the candidate has strong support."
        )

    elif candidate_label == "Experimental Candidate":
        explanations.append(
            "This cover idea is better suited for experimentation rather than priority planning."
        )

    else:
        explanations.append(
            "This cover idea should not be prioritized until stronger data appears."
        )

    return explanations
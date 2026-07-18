"""Build compact, deterministic analytics context for a future AI coach."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Any

import pandas as pd


CONTEXT_VERSION = "1.0"

_COUNT_METRICS = ["views", "likes", "comments", "saves", "shares"]
_RATE_METRICS = [
    "engagement_rate",
    "save_rate",
    "share_rate",
    "comment_rate",
    "performance_score",
]
_ANALYSIS_METRICS = [*_COUNT_METRICS, *_RATE_METRICS]

# The first available metric is used for ranking covers and comparing groups.
_PERFORMANCE_PRIORITY = [
    "performance_score",
    "engagement_rate",
    "save_rate",
    "share_rate",
    "comment_rate",
    "views",
    "likes",
    "saves",
    "shares",
    "comments",
]

_SUMMARY_CATEGORIES = ["platform", "genre", "content_type"]
_GROUP_CATEGORIES = [
    "genre",
    "content_type",
    "recording_type",
    "arrangement_type",
    "hook_type",
    "vocal_style",
    "platform",
]
_TOP_COVER_FIELDS = [
    "cover_id",
    "title",
    "artist",
    "platform",
    "content_type",
    "genre",
    "views",
    "engagement_rate",
    "save_rate",
    "share_rate",
    "comment_rate",
    "performance_score",
]
_GROUP_LIMIT = 3


def _finite_numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    """Return a float series where invalid and non-finite values are NaN."""
    numeric = pd.to_numeric(df[column], errors="coerce")

    return numeric.map(
        lambda value: (
            float(value)
            if pd.notna(value) and math.isfinite(float(value))
            else float("nan")
        )
    )


def _json_value(value: Any) -> Any:
    """Convert a scalar to a JSON-compatible Python value or ``None``."""
    try:
        if bool(pd.isna(value)):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, bool):
        return value

    if isinstance(value, Integral):
        return int(value)

    if isinstance(value, Real):
        number = float(value)
        if not math.isfinite(number):
            return None
        rounded = round(number, 4)
        return int(rounded) if rounded.is_integer() else rounded

    if isinstance(value, str):
        return value

    return str(value)


def _count_unique_values(df: pd.DataFrame, column: str) -> int:
    """Count non-empty unique values in a categorical column."""
    values = df[column].dropna().astype(str).str.strip()
    return int(values[values.ne("")].nunique())


def _select_performance_metric(
    numeric_columns: dict[str, pd.Series],
) -> str | None:
    """Select the strongest available ranking metric by fixed priority."""
    for metric in _PERFORMANCE_PRIORITY:
        values = numeric_columns.get(metric)
        if values is not None and values.notna().any():
            return metric

    return None


def _build_data_summary(df: pd.DataFrame) -> dict[str, int]:
    summary = {"cover_count": int(len(df))}

    for column in _SUMMARY_CATEGORIES:
        if column in df.columns:
            summary[f"{column}_count"] = _count_unique_values(df, column)

    return summary


def _build_portfolio_metrics(
    numeric_columns: dict[str, pd.Series],
) -> dict[str, int | float]:
    metrics: dict[str, int | float] = {}

    for column in _COUNT_METRICS:
        values = numeric_columns.get(column)
        if values is not None and values.notna().any():
            metrics[f"total_{column}"] = _json_value(values.dropna().sum())

    for column in _RATE_METRICS:
        values = numeric_columns.get(column)
        if values is not None and values.notna().any():
            metrics[f"average_{column}"] = _json_value(values.dropna().mean())

    views = numeric_columns.get("views")
    if views is not None and views.notna().any():
        metrics["median_views"] = _json_value(views.dropna().median())

    performance_scores = numeric_columns.get("performance_score")
    if performance_scores is not None and performance_scores.notna().any():
        metrics["median_performance_score"] = _json_value(
            performance_scores.dropna().median()
        )

    return metrics


def _get_low_view_indices(
    numeric_columns: dict[str, pd.Series],
) -> set[Any]:
    """Return indices below 10% of median views when evidence is sufficient."""
    views = numeric_columns.get("views")
    if views is None:
        return set()

    positive_views = views[views > 0].dropna()
    if len(positive_views) < 3:
        return set()

    low_view_threshold = positive_views.median() * 0.10
    return set(views[(views > 0) & (views < low_view_threshold)].index)


def _build_top_covers(
    df: pd.DataFrame,
    numeric_columns: dict[str, pd.Series],
    ranking_metric: str | None,
    top_n: int,
) -> list[dict[str, Any]]:
    if df.empty or top_n == 0:
        return []

    ranked = df.copy(deep=True)
    ranked["__source_order"] = range(len(ranked))

    tie_breakers: list[str] = []
    for column in ["cover_id", "title", "artist"]:
        if column in ranked.columns:
            sort_column = f"__sort_{column}"
            ranked[sort_column] = ranked[column].fillna("").astype(str)
            tie_breakers.append(sort_column)

    sort_columns: list[str] = []
    ascending: list[bool] = []

    if ranking_metric is not None:
        ranked["__ranking_metric"] = numeric_columns[ranking_metric]
        sort_columns.append("__ranking_metric")
        ascending.append(False)

    sort_columns.extend(tie_breakers)
    ascending.extend([True] * len(tie_breakers))
    sort_columns.append("__source_order")
    ascending.append(True)

    ranked = ranked.sort_values(
        by=sort_columns,
        ascending=ascending,
        na_position="last",
        kind="mergesort",
    ).head(top_n)

    records: list[dict[str, Any]] = []
    low_view_indices = _get_low_view_indices(numeric_columns)

    for index, row in ranked.iterrows():
        record: dict[str, Any] = {}

        for field in _TOP_COVER_FIELDS:
            if field not in df.columns:
                continue

            if field in numeric_columns:
                value = numeric_columns[field].loc[index]
            else:
                value = row[field]

            clean_value = _json_value(value)
            if clean_value is not None:
                record[field] = clean_value

        evidence_flags = []
        if index in low_view_indices:
            evidence_flags.append("low_view_sample")

        record["evidence_quality"] = "low" if evidence_flags else "standard"
        record["evidence_flags"] = evidence_flags

        records.append(record)

    return records


def _build_group_performance(
    df: pd.DataFrame,
    numeric_columns: dict[str, pd.Series],
    ranking_metric: str | None,
    min_group_size: int,
) -> dict[str, list[dict[str, Any]]]:
    if df.empty or ranking_metric is None:
        return {}

    summaries: dict[str, list[dict[str, Any]]] = {}

    for category in _GROUP_CATEGORIES:
        if category not in df.columns:
            continue

        working = pd.DataFrame(
            {
                "value": df[category],
                "metric": numeric_columns[ranking_metric],
            }
        )
        working = working[working["value"].notna() & working["metric"].notna()]
        working["value"] = working["value"].astype(str).str.strip()
        working = working[working["value"].ne("")]

        if working.empty:
            continue

        grouped = (
            working.groupby("value", as_index=False)
            .agg(
                cover_count=("metric", "size"),
                average_metric=("metric", "mean"),
            )
        )
        grouped = grouped[grouped["cover_count"] >= min_group_size].copy()

        if grouped.empty:
            continue

        grouped = grouped.sort_values(
            by=["average_metric", "cover_count", "value"],
            ascending=[False, False, True],
            kind="mergesort",
        ).head(_GROUP_LIMIT)

        summaries[category] = [
            {
                "value": str(row["value"]),
                "cover_count": int(row["cover_count"]),
                "metric": ranking_metric,
                "average": _json_value(row["average_metric"]),
            }
            for _, row in grouped.iterrows()
        ]

    return summaries


def _build_data_quality(
    df: pd.DataFrame,
    numeric_columns: dict[str, pd.Series],
    ranking_metric: str | None,
    group_performance: dict[str, list[dict[str, Any]]],
    top_covers: list[dict[str, Any]],
) -> dict[str, Any]:
    limitations: list[str] = []

    if df.empty:
        limitations.append("empty_dataset")

    if len(df) < 3:
        limitations.append("insufficient_cover_count")

    performance_score = numeric_columns.get("performance_score")
    if performance_score is None or not performance_score.notna().any():
        limitations.append("missing_performance_score")

    if ranking_metric is None:
        limitations.append("missing_analysis_metrics")

    has_group_comparison = any(
        len(category_groups) >= 2
        for category_groups in group_performance.values()
    )
    if not has_group_comparison:
        limitations.append("limited_group_comparison")

    if any(
        "low_view_sample" in cover["evidence_flags"]
        for cover in top_covers
    ):
        limitations.append("low_view_rate_outlier")

    missing_columns = [
        column for column in _ANALYSIS_METRICS if column not in df.columns
    ]

    return {
        "is_sufficient": len(df) >= 3 and ranking_metric is not None,
        "limitations": limitations,
        "missing_columns": missing_columns,
    }


def build_ai_creator_context(
    cover_data: pd.DataFrame,
    top_n: int = 3,
    min_group_size: int = 2,
) -> dict[str, Any]:
    """Build a compact analytics context without mutating ``cover_data``.

    Cover and group ranking uses ``performance_score`` when it contains finite
    values. Otherwise, the next available metric in ``_PERFORMANCE_PRIORITY``
    is used. If no numeric evidence exists, covers fall back to identifier and
    original-row ordering, while group comparisons remain empty.
    """
    if top_n < 0:
        raise ValueError("top_n must be zero or greater")

    if min_group_size < 1:
        raise ValueError("min_group_size must be at least one")

    df = cover_data.copy(deep=True)
    numeric_columns = {
        column: _finite_numeric_series(df, column)
        for column in _ANALYSIS_METRICS
        if column in df.columns
    }
    ranking_metric = _select_performance_metric(numeric_columns)
    group_performance = _build_group_performance(
        df,
        numeric_columns,
        ranking_metric,
        min_group_size,
    )
    top_covers = _build_top_covers(
        df,
        numeric_columns,
        ranking_metric,
        top_n,
    )

    return {
        "context_version": CONTEXT_VERSION,
        "data_summary": _build_data_summary(df),
        "portfolio_metrics": _build_portfolio_metrics(numeric_columns),
        "top_covers": top_covers,
        "group_performance": group_performance,
        "data_quality": _build_data_quality(
            df,
            numeric_columns,
            ranking_metric,
            group_performance,
            top_covers,
        ),
    }

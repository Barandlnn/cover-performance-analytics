from datetime import datetime

import pandas as pd

from src.analyzer import generate_insights, get_top_covers
from src.i18n import t


def dataframe_to_csv_bytes(
    df: pd.DataFrame,
) -> bytes:
    """
    Convert a DataFrame to UTF-8 encoded CSV bytes.

    UTF-8 with BOM is used so Turkish characters open correctly
    in spreadsheet applications such as Microsoft Excel.
    """
    return df.to_csv(
        index=False,
    ).encode("utf-8-sig")


def text_to_utf8_bytes(
    text: str,
) -> bytes:
    """
    Convert a text report to UTF-8 encoded bytes.
    """
    return text.encode("utf-8")


def _get_numeric_mean(
    df: pd.DataFrame,
    column_name: str,
) -> float:
    """
    Safely calculate the average of a numeric DataFrame column.
    """
    if column_name not in df.columns or df.empty:
        return 0.0

    numeric_values = pd.to_numeric(
        df[column_name],
        errors="coerce",
    )

    mean_value = numeric_values.mean()

    if pd.isna(mean_value):
        return 0.0

    return float(mean_value)


def _get_numeric_max(
    df: pd.DataFrame,
    column_name: str,
) -> float:
    """
    Safely calculate the maximum of a numeric DataFrame column.
    """
    if column_name not in df.columns or df.empty:
        return 0.0

    numeric_values = pd.to_numeric(
        df[column_name],
        errors="coerce",
    )

    max_value = numeric_values.max()

    if pd.isna(max_value):
        return 0.0

    return float(max_value)


def _get_row_value(
    row: pd.Series,
    column_name: str,
    default_value: str = "-",
):
    """
    Safely read a value from a pandas Series.
    """
    if column_name not in row.index:
        return default_value

    value = row[column_name]

    if pd.isna(value):
        return default_value

    return value


def build_performance_summary_report(
    df: pd.DataFrame,
    language: str,
) -> str:
    """
    Build a localized plain-text performance summary report.

    The report is generated from the currently filtered dashboard
    data and does not modify the source DataFrame.
    """
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    report_lines = [
        t(
            "report_export.report_title",
            language,
        ),
        "=" * 50,
        t(
            "report_export.generated_at",
            language,
        ).format(
            generated_at=generated_at,
        ),
        "",
    ]

    if df.empty:
        report_lines.append(
            t(
                "report_export.no_data",
                language,
            )
        )

        return "\n".join(report_lines)

    total_covers = len(df)

    average_engagement = _get_numeric_mean(
        df,
        "engagement_rate",
    )

    average_save_rate = _get_numeric_mean(
        df,
        "save_rate",
    )

    best_score = _get_numeric_max(
        df,
        "performance_score",
    )

    report_lines.extend(
        [
            t(
                "report_export.summary_title",
                language,
            ),
            "-" * 50,
            t(
                "report_export.total_covers",
                language,
            ).format(
                total_covers=total_covers,
            ),
            t(
                "report_export.average_engagement",
                language,
            ).format(
                average_engagement=average_engagement,
            ),
            t(
                "report_export.average_save_rate",
                language,
            ).format(
                average_save_rate=average_save_rate,
            ),
            t(
                "report_export.best_score",
                language,
            ).format(
                best_score=best_score,
            ),
        ]
    )

    top_covers_df = get_top_covers(df)

    if top_covers_df.empty:
        return "\n".join(report_lines)

    best_cover = top_covers_df.iloc[0]

    report_lines.extend(
        [
            "",
            t(
                "report_export.best_cover_title",
                language,
            ),
            "-" * 50,
            t(
                "report_export.cover_title",
                language,
            ).format(
                title=_get_row_value(
                    best_cover,
                    "title",
                ),
            ),
            t(
                "report_export.artist",
                language,
            ).format(
                artist=_get_row_value(
                    best_cover,
                    "artist",
                ),
            ),
            t(
                "report_export.genre",
                language,
            ).format(
                genre=_get_row_value(
                    best_cover,
                    "genre",
                ),
            ),
            t(
                "report_export.cover_score",
                language,
            ).format(
                performance_score=_get_row_value(
                    best_cover,
                    "performance_score",
                ),
            ),
            "",
            t(
                "report_export.insights_title",
                language,
            ),
            "-" * 50,
        ]
    )

    try:
        insights = generate_insights(
            df,
            best_cover,
            language=language,
        )
    except KeyError:
        insights = []

    if insights:
        report_lines.extend(f"- {insight}" for insight in insights)
    else:
        report_lines.append(
            t(
                "report_export.no_insights",
                language,
            )
        )

    return "\n".join(report_lines)

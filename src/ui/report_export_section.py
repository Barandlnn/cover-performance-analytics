from datetime import datetime

import pandas as pd
import streamlit as st

from src.i18n import t
from src.report_exporter import (
    build_performance_summary_report,
    dataframe_to_csv_bytes,
    text_to_utf8_bytes,
)


def render_report_export_section(
    filtered_df: pd.DataFrame,
    language: str,
) -> None:
    """
    Render report download controls for the filtered dashboard data.

    Export operations use in-memory data and do not modify CSV files
    or application state.
    """
    st.subheader(
        t(
            "report_export.section_title",
            language,
        )
    )

    st.caption(
        t(
            "report_export.section_description",
            language,
        )
    )

    if filtered_df.empty:
        st.info(
            t(
                "report_export.no_export_data",
                language,
            )
        )
        return

    generated_date = datetime.now().strftime("%Y-%m-%d")

    csv_bytes = dataframe_to_csv_bytes(filtered_df)

    summary_report = build_performance_summary_report(
        filtered_df,
        language=language,
    )

    summary_bytes = text_to_utf8_bytes(summary_report)

    csv_column, summary_column = st.columns(2)

    with csv_column:
        st.download_button(
            label=t(
                "report_export.download_csv",
                language,
            ),
            data=csv_bytes,
            file_name=("cover_performance_filtered_" f"{generated_date}.csv"),
            mime="text/csv",
            help=t(
                "report_export.download_csv_help",
                language,
            ),
        )

    with summary_column:
        st.download_button(
            label=t(
                "report_export.download_summary",
                language,
            ),
            data=summary_bytes,
            file_name=("cover_performance_summary_" f"{language}_{generated_date}.txt"),
            mime="text/plain",
            help=t(
                "report_export.download_summary_help",
                language,
            ),
        )

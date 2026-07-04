import os
from datetime import datetime

import pandas as pd


def save_candidate_test_result(
    file_path: str,
    genre: str,
    artist: str,
    content_type: str,
    candidate_summary: dict,
) -> None:
    """
    Candidate test sonucunu CSV dosyasına kaydeder.

    Bu dosya UI değil, veri yazma sorumluluğunu taşır.
    """

    new_record = {
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "genre": genre,
        "artist": artist,
        "content_type": content_type,
        "candidate_score": candidate_summary["candidate_score"],
        "candidate_label": candidate_summary["candidate_label"],
        "needs_more_data_count": candidate_summary["needs_more_data_count"],
        "action": candidate_summary["action"],
    }

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    new_df = pd.DataFrame([new_record])

    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df

    updated_df.to_csv(file_path, index=False)
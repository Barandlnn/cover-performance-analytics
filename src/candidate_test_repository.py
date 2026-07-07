from datetime import datetime

from src.data_manager import append_candidate_test


def save_candidate_test_result(
    genre: str,
    artist: str,
    content_type: str,
    candidate_summary: dict,
) -> None:
    """
    Candidate test sonucunu kayda hazırlar.

    CSV yazma işlemi src/data_manager.py içindeki
    append_candidate_test fonksiyonu üzerinden yapılır.
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

    append_candidate_test(new_record)
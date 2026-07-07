from pathlib import Path
import pandas as pd

from src.analyzer import load_data


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_PATH = DATA_DIR / "covers.csv"
SNAPSHOTS_PATH = DATA_DIR / "metrics_snapshots.csv"
CANDIDATE_TESTS_PATH = DATA_DIR / "candidate_tests.csv"

def append_row_to_csv(file_path, row_data: dict) -> None:
    """
    Verilen CSV dosyasına tek satırlık yeni veri ekler.

    Bu helper fonksiyon doğrudan app.py tarafından kullanılmaz.
    Diğer özel save/append fonksiyonları tarafından kullanılır.
    """
    existing_df = pd.read_csv(file_path)

    new_row_df = pd.DataFrame([row_data])

    # CSV'deki mevcut kolon sırasını korur.
    # Böylece app.py yanlış sırada veri gönderse bile dosya düzeni bozulmaz.
    new_row_df = new_row_df.reindex(columns=existing_df.columns)

    updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)

    updated_df.to_csv(file_path, index=False)


def append_new_cover(cover_data: dict) -> None:
    """
    covers.csv dosyasına yeni cover metadata satırı ekler.
    """
    append_row_to_csv(DATA_PATH, cover_data)


def append_metric_snapshot(snapshot_data: dict) -> None:
    """
    metrics_snapshots.csv dosyasına yeni metric snapshot satırı ekler.
    """
    append_row_to_csv(SNAPSHOTS_PATH, snapshot_data)


def append_candidate_test(candidate_test_data: dict) -> None:
    """
    candidate_tests.csv dosyasına yeni candidate test satırı ekler.
    """
    append_row_to_csv(CANDIDATE_TESTS_PATH, candidate_test_data)


def load_current_cover_data() -> pd.DataFrame:
    """
    Ana dashboard için güncel cover verisini yükler.

    src.analyzer.load_data(), covers.csv ile metrics_snapshots.csv
    içindeki en güncel snapshot verisini birleştirir.
    """
    return load_data(str(DATA_PATH))


def load_covers_raw() -> pd.DataFrame:
    """
    covers.csv dosyasını ham haliyle yükler.
    Growth analytics gibi bölümler cover metadata'sını ayrı kullanır.
    """
    return pd.read_csv(DATA_PATH)


def load_snapshots_raw() -> pd.DataFrame:
    """
    metrics_snapshots.csv dosyasını ham haliyle yükler.
    Zaman bazlı büyüme analizlerinde kullanılır.
    """
    return pd.read_csv(SNAPSHOTS_PATH)


def load_candidate_tests_raw() -> pd.DataFrame:
    """
    candidate_tests.csv dosyasını yükler.

    Dosya yoksa boş DataFrame döndürür.
    Böylece uygulama ilk çalıştırmada çökmez.
    """
    if not CANDIDATE_TESTS_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(CANDIDATE_TESTS_PATH)
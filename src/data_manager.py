from pathlib import Path

import pandas as pd

from src.analyzer import load_data


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_PATH = DATA_DIR / "covers.csv"
SNAPSHOTS_PATH = DATA_DIR / "metrics_snapshots.csv"
CANDIDATE_TESTS_PATH = DATA_DIR / "candidate_tests.csv"


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
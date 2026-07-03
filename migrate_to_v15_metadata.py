from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"

COVERS_PATH = DATA_DIR / "covers.csv"
BACKUP_PATH = DATA_DIR / "covers_before_v15.csv"


new_columns_with_defaults = {
    "post_time": "20:00",
    "caption_length": 0,
    "hashtags": "",
    "hashtag_count": 0,
    "audio_quality_score": 3,
    "thumbnail_score": 3,
    "recording_type": "home",
    "arrangement_type": "acoustic",
    "song_mood": "emotional",
    "content_origin": "cover",
}


df = pd.read_csv(COVERS_PATH)

df.to_csv(BACKUP_PATH, index=False, encoding="utf-8-sig")

for column_name, default_value in new_columns_with_defaults.items():
    if column_name not in df.columns:
        df[column_name] = default_value


df.to_csv(COVERS_PATH, index=False, encoding="utf-8-sig")

print("V1.5 metadata migration completed.")
print(f"Backup created: {BACKUP_PATH}")
print(f"Updated covers file: {COVERS_PATH}")
print("\nCurrent columns:")
print(df.columns.tolist())

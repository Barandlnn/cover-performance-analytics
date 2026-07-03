from pathlib import Path
from datetime import date
import pandas as pd

# Project paths
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

COVERS_PATH = DATA_DIR / "covers.csv"
COVERS_BACKUP_PATH = DATA_DIR / "covers_before_v14.csv"
SNAPSHOTS_PATH = DATA_DIR / "metrics_snapshots.csv"


# 1. Read current covers.csv
df = pd.read_csv(COVERS_PATH)


# 2. Columns that describe the cover itself
stable_cols = [
    "title",
    "artist",
    "platform",
    "content_type",
    "genre",
    "post_date",
    "duration_sec",
    "hook_type",
    "vocal_style",
    "language",
]


# 3. Columns that change over time
metric_cols = [
    "views",
    "likes",
    "comments",
    "saves",
    "shares",
]


# 4. Safety check
required_cols = stable_cols + metric_cols
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    raise ValueError(f"Missing columns in covers.csv: {missing_cols}")


# 5. Add cover_id if it does not exist
if "cover_id" not in df.columns:
    df.insert(0, "cover_id", [f"C{i + 1:03d}" for i in range(len(df))])


# 6. Backup old covers.csv before changing it
df.to_csv(COVERS_BACKUP_PATH, index=False)


# 7. Create new clean covers.csv
covers_df = df[["cover_id"] + stable_cols].copy()


# 8. Create metrics_snapshots.csv
snapshots_df = df[["cover_id"] + metric_cols].copy()

snapshots_df.insert(0, "snapshot_id", [f"S{i + 1:03d}" for i in range(len(df))])
snapshots_df.insert(2, "snapshot_date", date.today().isoformat())


# 9. Make sure metric columns are numeric
for col in metric_cols:
    snapshots_df[col] = (
        pd.to_numeric(snapshots_df[col], errors="coerce").fillna(0).astype(int)
    )


# 10. Save new files
covers_df.to_csv(COVERS_PATH, index=False)
snapshots_df.to_csv(SNAPSHOTS_PATH, index=False)


print("V1.4 migration completed.")
print(f"Backup created: {COVERS_BACKUP_PATH}")
print(f"Updated covers file: {COVERS_PATH}")
print(f"New snapshots file: {SNAPSHOTS_PATH}")

print("\nNew covers.csv:")
print(covers_df.head())

print("\nNew metrics_snapshots.csv:")
print(snapshots_df.head())

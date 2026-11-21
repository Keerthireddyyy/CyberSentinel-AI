
import pandas as pd
from pathlib import Path
from collections import defaultdict

AUTH_FILE = Path("data/raw/auth.txt.gz")
OUTPUT_FILE = Path(
    "data/processed/full_network_behavior.csv"
)

columns = [
    "time",
    "source_user",
    "destination_user",
    "source_computer",
    "destination_computer",
    "auth_type",
    "logon_type",
    "auth_orientation",
    "status"
]

# Store daily event counts and failure counts
counts = defaultdict(lambda: [0, 0])

# Store exact distinct users and destinations
# This can consume substantial memory on the full dataset.
destinations = defaultdict(set)
users = defaultdict(set)

reader = pd.read_csv(
    AUTH_FILE,
    compression="gzip",
    header=None,
    names=columns,
    chunksize=100_000,
    na_values=["?"]
)

print("Building full-network behavioral features...")

total_rows = 0

for chunk_number, chunk in enumerate(reader, start=1):
    chunk["dataset_day"] = (
        chunk["time"] // 86400
    ).astype(int)

    chunk["is_failure"] = (
        chunk["status"] == "Fail"
    ).astype(int)

    grouped = chunk.groupby(
        ["source_computer", "dataset_day"]
    )

    summary = grouped.agg(
        total_events=("time", "size"),
        failed_logins=("is_failure", "sum")
    )

    for key, row in summary.iterrows():
        counts[key][0] += int(row["total_events"])
        counts[key][1] += int(row["failed_logins"])

    for key, group in grouped:
        destinations[key].update(
            group["destination_computer"].dropna()
        )
        users[key].update(
            group["source_user"].dropna()
        )

    total_rows += len(chunk)

    if chunk_number % 500 == 0:
        print(
            f"Processed {total_rows:,} authentication events"
        )

print("\nPreparing behavioral dataset...")

rows = []

for key, (total, failures) in counts.items():
    source_computer, day = key

    rows.append({
        "source_computer": source_computer,
        "dataset_day": day,
        "total_events": total,
        "unique_destinations": len(destinations[key]),
        "unique_users": len(users[key]),
        "failed_logins": failures,
        "failure_rate": failures / total
    })

result = pd.DataFrame(rows)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(OUTPUT_FILE, index=False)

print("\nFull-network behavioral dataset created!")
print("Total authentication events:", total_rows)
print("Source-day records:", len(result))
print(
    "Unique source computers:",
    result["source_computer"].nunique()
)

print("\nSaved to:", OUTPUT_FILE)

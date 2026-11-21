
import pandas as pd
from pathlib import Path

AUTH_FILE = Path("data/raw/auth.txt.gz")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COMPUTER = "C17693"
OUTPUT_FILE = OUTPUT_DIR / "c17693_history.csv"

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

# LANL timestamps are relative seconds
# We inspect the first 35 dataset days.
MAX_TIME = 35 * 86400

total_scanned = 0
total_found = 0

# Start fresh if the script is rerun
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

reader = pd.read_csv(
    AUTH_FILE,
    compression="gzip",
    header=None,
    names=columns,
    chunksize=100_000,
    na_values=["?"]
)

print("Investigating source computer:", TARGET_COMPUTER)

for chunk_number, chunk in enumerate(reader, start=1):

    # Only consider events in the selected time range
    chunk = chunk[chunk["time"] <= MAX_TIME]

    if chunk.empty:
        break

    total_scanned += len(chunk)

    matches = chunk[
        chunk["source_computer"] == TARGET_COMPUTER
    ]

    if not matches.empty:
        matches.to_csv(
            OUTPUT_FILE,
            mode="a",
            header=not OUTPUT_FILE.exists(),
            index=False
        )

        total_found += len(matches)

    if chunk_number % 500 == 0:
        print(
            f"Processed {total_scanned:,} events | "
            f"Target events: {total_found:,}"
        )

print("\nInvestigation complete!")
print("Authentication events scanned:", total_scanned)
print("Target computer events found:", total_found)

if OUTPUT_FILE.exists():
    history = pd.read_csv(OUTPUT_FILE)

    print(
        "Unique destination computers:",
        history["destination_computer"].nunique()
    )

    print(
        "Unique source users:",
        history["source_user"].nunique()
    )

    print("\nAuthentication status:")
    print(history["status"].value_counts())

    print("\nSaved to:", OUTPUT_FILE)
else:
    print("No matching events found.")

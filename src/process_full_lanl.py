
import pandas as pd
from pathlib import Path

# ----------------------------------
# Configuration
# ----------------------------------

AUTH_FILE = Path("data/raw/auth.txt.gz")
REDTEAM_FILE = Path("data/raw/redteam.txt.gz")

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ATTACK_OUTPUT = OUTPUT_DIR / "lanl_known_attacks.csv"
SAMPLE_OUTPUT = OUTPUT_DIR / "lanl_auth_sample.csv"

CHUNK_SIZE = 100_000
SAMPLE_PER_CHUNK = 100

auth_columns = [
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

match_columns = [
    "time",
    "source_user",
    "source_computer",
    "destination_computer"
]

# ----------------------------------
# Load red-team reference events
# ----------------------------------

redteam = pd.read_csv(
    REDTEAM_FILE,
    compression="gzip",
    header=None,
    names=match_columns
)

redteam_keys = pd.MultiIndex.from_frame(
    redteam[match_columns]
)

print("Known red-team records:", len(redteam))
print("Starting full authentication scan...")

# ----------------------------------
# Process authentication chunks
# ----------------------------------

total_events = 0
total_matches = 0
sample_count = 0
chunk_count = 0

# Remove previous outputs so reruns do not duplicate rows
for output_file in [ATTACK_OUTPUT, SAMPLE_OUTPUT]:
    if output_file.exists():
        output_file.unlink()

reader = pd.read_csv(
    AUTH_FILE,
    compression="gzip",
    header=None,
    names=auth_columns,
    chunksize=CHUNK_SIZE,
    na_values=["?"]
)

for chunk in reader:
    chunk_count += 1
    total_events += len(chunk)

    # Compare against known red-team events
    auth_keys = pd.MultiIndex.from_frame(
        chunk[match_columns]
    )

    chunk["known_redteam_event"] = (
        auth_keys.isin(redteam_keys).astype("int8")
    )

    attacks = chunk[
        chunk["known_redteam_event"] == 1
    ]

    total_matches += len(attacks)

    # Save all matching events
    if not attacks.empty:
        attacks.to_csv(
            ATTACK_OUTPUT,
            mode="a",
            header=not ATTACK_OUTPUT.exists(),
            index=False
        )

    # Sample unmatched events for exploratory analysis
    unmatched = chunk[
        chunk["known_redteam_event"] == 0
    ]

    sample = unmatched.sample(
        n=min(SAMPLE_PER_CHUNK, len(unmatched)),
        random_state=42
    )

    sample.to_csv(
        SAMPLE_OUTPUT,
        mode="a",
        header=not SAMPLE_OUTPUT.exists(),
        index=False
    )

    sample_count += len(sample)

    if chunk_count % 100 == 0:
        print(
            f"Chunks: {chunk_count:,} | "
            f"Events: {total_events:,} | "
            f"Known matches: {total_matches:,}"
        )

print("\nFull dataset processing complete!")
print("Total events:", f"{total_events:,}")
print("Known red-team matches:", f"{total_matches:,}")
print("Unmatched sample records:", f"{sample_count:,}")
print("Attack output:", ATTACK_OUTPUT)
print("Sample output:", SAMPLE_OUTPUT)


import pandas as pd
from pathlib import Path

# Location of the real LANL authentication dataset
AUTH_FILE = Path("data/raw/auth.txt.gz")

# The nine columns in the LANL authentication data
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

# Read the file in manageable chunks
CHUNK_SIZE = 100_000

print("Starting LANL authentication processing...")

reader = pd.read_csv(
    AUTH_FILE,
    compression="gzip",
    header=None,
    names=columns,
    chunksize=CHUNK_SIZE,
    na_values=["?"]
)

# Read only the first chunk for our initial test
first_chunk = next(reader)

print("\nFirst 5 authentication events:")
print(first_chunk.head().to_string(index=False))

print("\nTotal events in this chunk:", len(first_chunk))

print("\nAuthentication status counts:")
print(first_chunk["status"].value_counts())

print("\nMissing values by column:")
print(first_chunk.isna().sum())

print("\nFirst chunk processed successfully!")


# -----------------------------------
# Match known LANL red-team events
# -----------------------------------

redteam_columns = [
    "time",
    "source_user",
    "source_computer",
    "destination_computer"
]

redteam = pd.read_csv(
    "data/raw/redteam.txt.gz",
    compression="gzip",
    header=None,
    names=redteam_columns
)

print("\nTotal known red-team records:", len(redteam))

# Use the four fields shared by both datasets
match_columns = [
    "time",
    "source_user",
    "source_computer",
    "destination_computer"
]

redteam_keys = pd.MultiIndex.from_frame(
    redteam[match_columns]
)

auth_keys = pd.MultiIndex.from_frame(
    first_chunk[match_columns]
)

first_chunk["known_redteam_event"] = (
    auth_keys.isin(redteam_keys).astype(int)
)

print("\nKnown red-team matches in first chunk:")
print(first_chunk["known_redteam_event"].sum())

# Save the first chunk for further analysis
output_path = "data/processed/lanl_first_chunk.csv"

from pathlib import Path
Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

first_chunk.to_csv(output_path, index=False)

print("\nProcessed authentication data saved to:", output_path)



import pandas as pd

# Read the compressed LANL red-team dataset
columns = [
    "time",
    "user",
    "source_computer",
    "destination_computer"
]

df = pd.read_csv(
    "data/raw/redteam.txt.gz",
    compression="gzip",
    header=None,
    names=columns
)

# Display dataset information
print("\nTotal known red-team events:", len(df))

print("\nFirst 10 events:")
print(df.head(10).to_string(index=False))

print("\nUnique users:", df["user"].nunique())

print(
    "Unique source computers:",
    df["source_computer"].nunique()
)

print(
    "Unique destination computers:",
    df["destination_computer"].nunique()
)

# Save a convenient CSV copy
df.to_csv(
    "data/redteam_events.csv",
    index=False
)

print("\nRed-team events saved successfully!")

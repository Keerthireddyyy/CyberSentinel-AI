
import pandas as pd
from pathlib import Path

# Load the processed authentication data
DATA_DIR = Path("data/processed")

sample = pd.read_csv(
    DATA_DIR / "lanl_auth_sample.csv"
)

attacks = pd.read_csv(
    DATA_DIR / "lanl_known_attacks.csv"
)

print("Unmatched sample records:", len(sample))
print("Known attack records:", len(attacks))

# Combine data for feature exploration
df = pd.concat(
    [sample, attacks],
    ignore_index=True
)

# Create basic authentication features
df["is_failure"] = (
    df["status"] == "Fail"
).astype(int)

df["is_success"] = (
    df["status"] == "Success"
).astype(int)

df["is_network_logon"] = (
    df["logon_type"] == "Network"
).astype(int)

df["is_ntlm"] = (
    df["auth_type"] == "NTLM"
).astype(int)

# LANL time is measured in seconds
# from the dataset's starting point
df["dataset_day"] = (
    df["time"] // 86400
).astype(int)

# Save the new dataset
output_file = DATA_DIR / "lanl_features.csv"

df.to_csv(output_file, index=False)

print("\nFeature engineering completed!")
print("Total records:", len(df))
print("Known attack records:", df["known_redteam_event"].sum())

print("\nFeature preview:")
print(
    df[
        [
            "is_failure",
            "is_success",
            "is_network_logon",
            "is_ntlm",
            "dataset_day"
        ]
    ].head()
)

print("\nSaved to:", output_file)

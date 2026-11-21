
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")

# Load sampled unmatched authentication events
sample = pd.read_csv(
    DATA_DIR / "lanl_auth_sample.csv"
)

# Load known attack matches separately
attacks = pd.read_csv(
    DATA_DIR / "lanl_known_attacks.csv"
)

# Build features ONLY from the unmatched sample.
# Known attacks are kept separate for later analysis.
sample["dataset_day"] = (
    sample["time"] // 86400
).astype(int)

sample["is_failure"] = (
    sample["status"] == "Fail"
).astype(int)

behavior = (
    sample.groupby(
        ["source_computer", "dataset_day"]
    )
    .agg(
        sampled_events=("time", "size"),
        unique_destinations=(
            "destination_computer",
            "nunique"
        ),
        unique_users=("source_user", "nunique"),
        failed_logins=("is_failure", "sum")
    )
    .reset_index()
)

behavior["failure_rate"] = (
    behavior["failed_logins"]
    / behavior["sampled_events"]
)

# Add reference attack counts for analysis only.
# Do not use this column as a model feature.
attacks["dataset_day"] = (
    attacks["time"] // 86400
).astype(int)

attack_counts = (
    attacks.groupby(
        ["source_computer", "dataset_day"]
    )
    .size()
    .reset_index(name="known_attack_matches")
)

behavior = behavior.merge(
    attack_counts,
    on=["source_computer", "dataset_day"],
    how="left"
)

behavior["known_attack_matches"] = (
    behavior["known_attack_matches"]
    .fillna(0)
    .astype(int)
)

output_file = (
    DATA_DIR / "network_behavior_sample.csv"
)

behavior.to_csv(output_file, index=False)

print("\nNetwork-wide behavior dataset created!")
print("Source-day records:", len(behavior))
print(
    "Unique source computers:",
    behavior["source_computer"].nunique()
)
print(
    "Rows with known attack matches:",
    (behavior["known_attack_matches"] > 0).sum()
)

print("\nFeature preview:")
print(behavior.head(10).to_string(index=False))

print("\nSaved to:", output_file)

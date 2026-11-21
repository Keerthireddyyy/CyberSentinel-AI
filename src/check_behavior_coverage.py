
import pandas as pd

DATA_DIR = "data/processed/"

behavior = pd.read_csv(
    DATA_DIR + "network_behavior_sample.csv"
)

attacks = pd.read_csv(
    DATA_DIR + "lanl_known_attacks.csv"
)

attacks["dataset_day"] = (
    attacks["time"] // 86400
).astype(int)

# Unique source-day combinations with known attacks
attack_days = (
    attacks[
        ["source_computer", "dataset_day"]
    ]
    .drop_duplicates()
)

# Check whether each combination appears in the sample
coverage = attack_days.merge(
    behavior[
        ["source_computer", "dataset_day"]
    ],
    on=["source_computer", "dataset_day"],
    how="left",
    indicator=True
)

covered = (
    coverage["_merge"] == "both"
).sum()

total = len(attack_days)

print("\nBehavioral dataset coverage report")
print("----------------------------------")
print("Known attack source-day combinations:", total)
print("Covered by sampled dataset:", covered)
print("Missing from sampled dataset:", total - covered)

print(
    "Coverage percentage:",
    round(covered / total * 100, 2)
    if total else 0,
    "%"
)

print("\nCoverage by source computer:")
print(
    coverage.assign(
        covered=coverage["_merge"] == "both"
    )
    .groupby("source_computer")["covered"]
    .agg(["sum", "count"])
    .to_string()
)

print("\nCoverage analysis completed!")


import pandas as pd
import duckdb

# Load complete behavioral features
con = duckdb.connect()

behavior = con.execute(
    """
    SELECT source_computer, dataset_day
    FROM read_parquet(
        'data/processed/full_network_behavior.parquet'
    )
    """
).df()

# Load known red-team authentication matches
attacks = pd.read_csv(
    "data/processed/lanl_known_attacks.csv"
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

coverage = attack_days.merge(
    behavior,
    on=["source_computer", "dataset_day"],
    how="left",
    indicator=True
)

covered = (
    coverage["_merge"] == "both"
).sum()

total = len(attack_days)

print("\nFull behavioral dataset coverage")
print("--------------------------------")
print("Known attack source-day combinations:", total)
print("Covered:", covered)
print("Missing:", total - covered)

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

con.close()

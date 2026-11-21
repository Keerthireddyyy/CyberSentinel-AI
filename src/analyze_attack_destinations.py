
import pandas as pd
import duckdb

FEATURE_FILE = (
    "data/processed/behavior_with_new_destinations.parquet"
)

ATTACK_FILE = (
    "data/processed/lanl_known_attacks.csv"
)

con = duckdb.connect()

df = con.execute(
    "SELECT * FROM read_parquet(?)",
    [FEATURE_FILE]
).df()

con.close()

attacks = pd.read_csv(ATTACK_FILE)

attacks["dataset_day"] = (
    attacks["time"] // 86400
).astype(int)

attack_days = (
    attacks.groupby(["source_computer", "dataset_day"])
    .size()
    .reset_index(name="known_attack_matches")
)

known = df.merge(
    attack_days,
    on=["source_computer", "dataset_day"],
    how="inner"
)

print("\nKNOWN ATTACK SOURCE-DAY CONNECTION BEHAVIOR")
print("=" * 85)

columns = [
    "source_computer",
    "dataset_day",
    "known_attack_matches",
    "total_events",
    "unique_destinations",
    "new_destinations",
    "new_destination_ratio"
]

print(
    known[columns]
    .sort_values(
        ["source_computer", "dataset_day"]
    )
    .to_string(index=False)
)

print("\nSUMMARY")
print("=" * 50)

print("Known attack source-days:", len(known))

print(
    "Attack source-days with new destinations:",
    (known["new_destinations"] > 0).sum()
)

print(
    "Average new-destination ratio on known attack days:",
    round(known["new_destination_ratio"].mean(), 4)
)

print(
    "Average new-destination ratio across all source-days:",
    round(df["new_destination_ratio"].mean(), 4)
)

print("\nAnalysis completed!")

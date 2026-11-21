
import pandas as pd

# Load daily source-computer activity
daily = pd.read_csv(
    "data/processed/c17693_daily_activity.csv"
)

# Load known red-team authentication matches
attacks = pd.read_csv(
    "data/processed/lanl_known_attacks.csv"
)

# Keep attacks originating from C17693
attacks = attacks[
    attacks["source_computer"] == "C17693"
].copy()

# Convert relative seconds to dataset days
attacks["dataset_day"] = (
    attacks["time"] // 86400
)

# Count known attack matches per day
attack_counts = (
    attacks.groupby("dataset_day")
    .size()
    .reset_index(name="known_attack_matches")
)

# Combine activity and attack counts
comparison = daily.merge(
    attack_counts,
    on="dataset_day",
    how="left"
)

comparison["known_attack_matches"] = (
    comparison["known_attack_matches"]
    .fillna(0)
    .astype(int)
)

print("\nC17693 activity versus known attack matches:")
print(comparison.to_string(index=False))

comparison.to_csv(
    "data/processed/c17693_attack_comparison.csv",
    index=False
)

print("\nComparison saved successfully!")

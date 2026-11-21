
import pandas as pd

# Load sampled authentication events
sample = pd.read_csv(
    "data/processed/lanl_auth_sample.csv"
)

# Load known red-team matches
attacks = pd.read_csv(
    "data/processed/lanl_known_attacks.csv"
)

print("\nAnalyzing source-computer behavior...")

# Summarize activity by source computer
source_summary = (
    sample.groupby("source_computer")
    .agg(
        sampled_events=("time", "size"),
        unique_destinations=(
            "destination_computer",
            "nunique"
        ),
        unique_users=("source_user", "nunique"),
        failures=(
            "status",
            lambda x: (x == "Fail").sum()
        )
    )
    .reset_index()
)

# Add known red-team match counts
attack_counts = (
    attacks["source_computer"]
    .value_counts()
    .rename_axis("source_computer")
    .reset_index(name="known_attack_matches")
)

source_summary = source_summary.merge(
    attack_counts,
    on="source_computer",
    how="left"
)

source_summary["known_attack_matches"] = (
    source_summary["known_attack_matches"]
    .fillna(0)
    .astype(int)
)

print("\nTop 10 source computers by sampled events:")
print(
    source_summary.sort_values(
        "sampled_events",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\nBehavior of known red-team source computers:")
print(
    source_summary[
        source_summary["source_computer"].isin(
            attacks["source_computer"].unique()
        )
    ].to_string(index=False)
)

# Save analysis
output_file = (
    "data/processed/source_behavior_summary.csv"
)

source_summary.to_csv(
    output_file,
    index=False
)

print("\nSource behavior analysis saved to:", output_file)

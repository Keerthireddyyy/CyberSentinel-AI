
import pandas as pd

HISTORICAL_FILE = (
    "data/processed/historical_network_comparison.csv"
)

NETWORK_FILE = (
    "data/processed/network_aware_model_results.csv"
)

FEATURE_FILE = (
    "data/processed/behavior_with_new_destinations.parquet"
)

historical = pd.read_csv(HISTORICAL_FILE)
network = pd.read_csv(NETWORK_FILE)

# Calculate anomaly ranks within each model.
# Lower anomaly scores indicate greater anomaly.
for df in [historical, network]:
    df.sort_values(
        ["anomaly_score", "source_computer", "dataset_day"],
        inplace=True
    )

    df["rank_percentile"] = (
        range(1, len(df) + 1)
    )

    df["rank_percentile"] = (
        df["rank_percentile"] / len(df) * 100
    )

historical = historical[
    [
        "source_computer",
        "dataset_day",
        "rank_percentile"
    ]
].rename(
    columns={
        "rank_percentile": "historical_percentile"
    }
)

network = network[
    [
        "source_computer",
        "dataset_day",
        "known_attack_matches",
        "rank_percentile"
    ]
].rename(
    columns={
        "rank_percentile": "network_percentile"
    }
)

comparison = historical.merge(
    network,
    on=["source_computer", "dataset_day"]
)

known = comparison[
    comparison["known_attack_matches"] > 0
].copy()


import duckdb

con = duckdb.connect()

features = con.execute(
    """
    SELECT
        source_computer,
        dataset_day,
        new_destinations,
        new_destination_ratio
    FROM read_parquet(?)
    """,
    [FEATURE_FILE]
).df()

con.close()


known = known.merge(
    features,
    on=["source_computer", "dataset_day"],
    how="left"
)

known["ranking_change"] = (
    known["historical_percentile"]
    - known["network_percentile"]
)

print("\nKNOWN ATTACK SOURCE-DAY RANKING CHANGES")
print("=" * 100)

print(
    known.sort_values(
        "ranking_change",
        ascending=False
    ).to_string(index=False)
)

print("\nSUMMARY")
print("=" * 50)

print(
    "Attack days ranked higher by network model:",
    (known["ranking_change"] > 0).sum()
)

print(
    "Attack days ranked lower by network model:",
    (known["ranking_change"] < 0).sum()
)

print(
    "Attack days with unchanged ranks:",
    (known["ranking_change"] == 0).sum()
)

print("\nAnalysis completed!")

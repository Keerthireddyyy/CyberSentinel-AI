
import math
from pathlib import Path

import duckdb
import pandas as pd

RESULTS_FILE = (
    "data/processed/three_model_comparison.csv"
)

FEATURES_FILE = (
    "data/processed/behavior_with_user_relationships.parquet"
)

OUTPUT_FILE = (
    "data/processed/security_alerts.csv"
)

ALERT_BUDGET = 0.01

print("Loading network-aware anomaly scores...", flush=True)

results = pd.read_csv(RESULTS_FILE)

results = results[
    results["model"] == "Network-aware"
].copy()

results = results.sort_values(
    ["anomaly_score", "source_computer", "dataset_day"]
).reset_index(drop=True)

alert_count = math.ceil(
    len(results) * ALERT_BUDGET
)

alerts = results.head(alert_count).copy()

# Rank is based on anomaly score:
# lower scores are more anomalous.
alerts["anomaly_rank"] = range(1, len(alerts) + 1)

# These severity levels are operational prioritization
# bands, not calibrated probabilities of maliciousness.
alerts["severity"] = "LOW"

alerts.loc[
    alerts["anomaly_rank"] <= math.ceil(alert_count * 0.10),
    "severity"
] = "CRITICAL"

alerts.loc[
    (alerts["anomaly_rank"] > math.ceil(alert_count * 0.10))
    & (alerts["anomaly_rank"] <= math.ceil(alert_count * 0.40)),
    "severity"
] = "HIGH"

alerts.loc[
    (alerts["anomaly_rank"] > math.ceil(alert_count * 0.40))
    & (alerts["anomaly_rank"] <= math.ceil(alert_count * 0.70)),
    "severity"
] = "MEDIUM"

print("Loading behavioral evidence...", flush=True)

con = duckdb.connect()

features = con.execute(
    """
    SELECT
        source_computer,
        dataset_day,
        total_events,
        unique_destinations,
        unique_users,
        failed_logins,
        failure_rate,
        events_vs_history,
        destinations_vs_history,
        new_destinations,
        new_destination_ratio,
        new_user_destination_pairs
    FROM read_parquet(?)
    """,
    [FEATURES_FILE]
).df()

con.close()

alerts = alerts.merge(
    features,
    on=["source_computer", "dataset_day"],
    how="left",
    validate="one_to_one"
)

alerts["alert_id"] = [
    f"CS-{i:06d}"
    for i in range(1, len(alerts) + 1)
]

alerts["alert_type"] = "BEHAVIORAL_ANOMALY"

alerts["description"] = (
    "Unusual authentication behavior detected for source "
    + alerts["source_computer"].astype(str)
    + " on dataset day "
    + alerts["dataset_day"].astype(str)
)

# known_attack_matches is retained for offline evaluation,
# not as evidence available to a live security analyst.
alerts = alerts.drop(
    columns=["known_attack_matches"],
    errors="ignore"
)

columns = [
    "alert_id",
    "source_computer",
    "dataset_day",
    "alert_type",
    "severity",
    "anomaly_score",
    "anomaly_rank",
    "description",
    "total_events",
    "unique_destinations",
    "unique_users",
    "failed_logins",
    "failure_rate",
    "events_vs_history",
    "destinations_vs_history",
    "new_destinations",
    "new_destination_ratio",
    "new_user_destination_pairs"
]

alerts = alerts[columns]

Path(OUTPUT_FILE).parent.mkdir(
    parents=True,
    exist_ok=True
)

alerts.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSECURITY ALERT GENERATION SUMMARY")
print("=" * 55)
print("Total test records:", len(results))
print("Alert budget:", f"{ALERT_BUDGET * 100:.0f}%")
print("Alerts generated:", len(alerts))

print("\nSeverity distribution:")
print(alerts["severity"].value_counts())

print("\nSample alerts:")
print(
    alerts[
        [
            "alert_id",
            "source_computer",
            "dataset_day",
            "severity",
            "anomaly_score",
            "new_destinations"
        ]
    ].head(10).to_string(index=False)
)

print("\nOutput file:", OUTPUT_FILE)
print("Security alert generation completed!")

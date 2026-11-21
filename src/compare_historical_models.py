
import pandas as pd
import numpy as np
import duckdb

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_FILE = "data/processed/historical_behavior_features.parquet"
ATTACK_FILE = "data/processed/lanl_known_attacks.csv"

TRAIN_END_DAY = 14

print("Loading historical behavioral dataset...")

con = duckdb.connect()

df = con.execute(
    "SELECT * FROM read_parquet(?)",
    [DATA_FILE]
).df()

con.close()

# Known red-team events are used for evaluation only.
attacks = pd.read_csv(ATTACK_FILE)

attacks["dataset_day"] = (
    attacks["time"] // 86400
).astype(int)

attack_days = (
    attacks.groupby(["source_computer", "dataset_day"])
    .size()
    .reset_index(name="known_attack_matches")
)

df = df.merge(
    attack_days,
    on=["source_computer", "dataset_day"],
    how="left"
)

df["known_attack_matches"] = (
    df["known_attack_matches"]
    .fillna(0)
    .astype(int)
)

train = df[df["dataset_day"] <= TRAIN_END_DAY].copy()
test = df[df["dataset_day"] > TRAIN_END_DAY].copy()

baseline_features = [
    "total_events",
    "unique_destinations",
    "unique_users",
    "failed_logins",
    "failure_rate"
]

historical_features = baseline_features + [
    "history_days",
    "avg_events_7d",
    "avg_destinations_7d",
    "avg_users_7d",
    "avg_failures_7d",
    "events_vs_history",
    "destinations_vs_history",
    "users_vs_history",
    "failures_vs_history"
]

def evaluate_model(name, features):
    scaler = StandardScaler()

    X_train = scaler.fit_transform(
        train[features].fillna(0)
    )

    X_test = scaler.transform(
        test[features].fillna(0)
    )

    model = IsolationForest(
        n_estimators=200,
        contamination=0.01,
        random_state=42,
        n_jobs=-1
    )

    print(f"\nTraining {name}...")

    model.fit(X_train)

    scores = model.decision_function(X_test)
    predictions = model.predict(X_test)

    results = test[
        [
            "source_computer",
            "dataset_day",
            "known_attack_matches"
        ]
    ].copy()

    results["anomaly_score"] = scores
    results["is_anomaly"] = (predictions == -1).astype(int)

    results["anomaly_rank"] = (
        results["anomaly_score"]
        .rank(method="first", ascending=True)
    )

    results["anomaly_percentile"] = (
        results["anomaly_rank"] / len(results) * 100
    )

    known = results[
        results["known_attack_matches"] > 0
    ]

    print("Flagged source-days:", results["is_anomaly"].sum())
    print("Known attack source-days:", len(known))
    print("Known attack source-days flagged:", known["is_anomaly"].sum())

    if len(known) > 0:
        print(
            "Known attack source-day flag rate:",
            round(known["is_anomaly"].mean() * 100, 2),
            "%"
        )

        print(
            "Known attack source-days in top 5%:",
            (known["anomaly_percentile"] <= 5).sum()
        )

        print(
            "Known attack source-days in top 10%:",
            (known["anomaly_percentile"] <= 10).sum()
        )

        print(
            "Median known attack percentile:",
            round(known["anomaly_percentile"].median(), 2)
        )

    return results

baseline = evaluate_model(
    "Baseline Isolation Forest",
    baseline_features
)

historical = evaluate_model(
    "Historical Isolation Forest",
    historical_features
)

baseline.to_csv(
    "data/processed/baseline_model_comparison.csv",
    index=False
)

historical.to_csv(
    "data/processed/historical_model_comparison.csv",
    index=False
)

print("\nModel comparison completed!")

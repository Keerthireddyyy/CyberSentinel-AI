
import math

import duckdb
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_FILE = (
    "data/processed/behavior_with_user_relationships.parquet"
)

ATTACK_FILE = "data/processed/lanl_known_attacks.csv"

OUTPUT_FILE = (
    "data/processed/three_model_comparison.csv"
)

print("Loading behavioral dataset...", flush=True)

con = duckdb.connect()

df = con.execute(
    "SELECT * FROM read_parquet(?)",
    [DATA_FILE]
).df()

con.close()

attacks = pd.read_csv(ATTACK_FILE)

attacks["dataset_day"] = (
    attacks["time"] // 86400
).astype(int)

attack_days = (
    attacks.groupby(
        ["source_computer", "dataset_day"]
    )
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

# Stable ordering for reproducibility.
df = df.sort_values(
    ["dataset_day", "source_computer"]
).reset_index(drop=True)

train = df[df["dataset_day"] <= 14].copy()
test = df[df["dataset_day"] > 14].copy()

historical_features = [
    "total_events",
    "unique_destinations",
    "unique_users",
    "failed_logins",
    "failure_rate",
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

network_features = historical_features + [
    "new_destinations",
    "new_destination_ratio"
]

user_features = network_features + [
    "new_user_destination_pairs",
    "new_user_relationship_ratio"
]

models = {
    "Historical": historical_features,
    "Network-aware": network_features,
    "User-relationship-aware": user_features
}

all_results = []

print("Training records:", len(train))
print("Testing records:", len(test))

for model_name, features in models.items():

    print(
        f"\nTraining {model_name} model...",
        flush=True
    )

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

    model.fit(X_train)

    scores = model.decision_function(X_test)

    results = test[
        [
            "source_computer",
            "dataset_day",
            "known_attack_matches"
        ]
    ].copy()

    results["anomaly_score"] = scores
    results["model"] = model_name

    results = results.sort_values(
        ["anomaly_score", "source_computer", "dataset_day"]
    ).reset_index(drop=True)

    total_known = (
        results["known_attack_matches"] > 0
    ).sum()

    for budget in [0.01, 0.02, 0.05]:

        alert_count = math.ceil(
            len(results) * budget
        )

        alerts = results.head(alert_count)

        found = (
            alerts["known_attack_matches"] > 0
        ).sum()

        print(
            f"Top {budget * 100:.0f}%: "
            f"{found}/{total_known} "
            f"known attack source-days "
            f"({alert_count} alerts)",
            flush=True
        )

    all_results.append(results)

combined = pd.concat(
    all_results,
    ignore_index=True
)

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nAll three models evaluated!")
print("Results saved to:", OUTPUT_FILE)


import pandas as pd
import duckdb
import math

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_FILE = (
    "data/processed/behavior_with_new_destinations.parquet"
)

ATTACK_FILE = "data/processed/lanl_known_attacks.csv"

TRAIN_END_DAY = 14

print("Loading network behavioral features...")

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

def train_and_rank(name, features):
    print(f"\nTraining {name}...")

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

    results = test[
        [
            "source_computer",
            "dataset_day",
            "known_attack_matches"
        ]
    ].copy()

    results["anomaly_score"] = (
        model.decision_function(X_test)
    )

    ranked = results.sort_values(
        ["anomaly_score", "source_computer", "dataset_day"]
    )

    total_known = (
        results["known_attack_matches"] > 0
    ).sum()

    for budget in [0.01, 0.02, 0.05]:
        alert_count = math.ceil(
            len(ranked) * budget
        )

        alerts = ranked.head(alert_count)

        found = (
            alerts["known_attack_matches"] > 0
        ).sum()

        print(
            f"Top {budget * 100:.0f}%: "
            f"{found}/{total_known} "
            f"known attack source-days found "
            f"({alert_count} alerts)"
        )

    return results

historical = train_and_rank(
    "Historical Model",
    historical_features
)

network = train_and_rank(
    "Network-Aware Model",
    network_features
)

historical.to_csv(
    "data/processed/historical_network_comparison.csv",
    index=False
)

network.to_csv(
    "data/processed/network_aware_model_results.csv",
    index=False
)

print("\nNetwork model comparison completed!")

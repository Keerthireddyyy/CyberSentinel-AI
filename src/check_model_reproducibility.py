
import duckdb
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_FILE = (
    "data/processed/behavior_with_user_relationships.parquet"
)

FEATURES = [
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

print("Loading data...", flush=True)

con = duckdb.connect()

df = con.execute(
    "SELECT * FROM read_parquet(?)",
    [DATA_FILE]
).df()

con.close()

df = df.sort_values(
    ["dataset_day", "source_computer"]
).reset_index(drop=True)

train = df[df["dataset_day"] <= 14]
test = df[df["dataset_day"] > 14]

scaler = StandardScaler()

X_train = scaler.fit_transform(
    train[FEATURES].fillna(0)
)

X_test = scaler.transform(
    test[FEATURES].fillna(0)
)

def train_model(run_number):
    print(
        f"Training reproducibility run {run_number}...",
        flush=True
    )

    model = IsolationForest(
        n_estimators=200,
        contamination=0.01,
        random_state=42,
        n_jobs=1
    )

    model.fit(X_train)

    return model.decision_function(X_test)

scores_1 = train_model(1)
scores_2 = train_model(2)

print("\nREPRODUCIBILITY RESULTS")
print("=" * 50)

print(
    "Scores identical:",
    np.array_equal(scores_1, scores_2)
)

print(
    "Maximum absolute difference:",
    np.max(np.abs(scores_1 - scores_2))
)

print(
    "Training records:",
    len(train)
)

print(
    "Testing records:",
    len(test)
)

print("\nReproducibility check completed!")

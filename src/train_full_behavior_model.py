
import pandas as pd
import duckdb
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_FILE = "data/processed/full_network_behavior.parquet"
ATTACK_FILE = "data/processed/lanl_known_attacks.csv"

# Load complete behavioral features
con = duckdb.connect()

df = con.execute(
    "SELECT * FROM read_parquet(?)",
    [DATA_FILE]
).df()

con.close()

# Load known red-team events for evaluation only
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

# Chronological split
TRAIN_END_DAY = 14

train = df[df["dataset_day"] <= TRAIN_END_DAY].copy()
test = df[df["dataset_day"] > TRAIN_END_DAY].copy()

features = [
    "total_events",
    "unique_destinations",
    "unique_users",
    "failed_logins",
    "failure_rate"
]

print("Training source-day records:", len(train))
print("Testing source-day records:", len(test))

# Fit preprocessing on training data only
scaler = StandardScaler()

X_train = scaler.fit_transform(
    train[features].fillna(0)
)

X_test = scaler.transform(
    test[features].fillna(0)
)

# Train anomaly detection model
model = IsolationForest(
    n_estimators=200,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)

print("\nTraining full-network Isolation Forest...")

model.fit(X_train)

test["anomaly_score"] = model.decision_function(X_test)

test["is_anomaly"] = (
    model.predict(X_test) == -1
).astype(int)

# Evaluate against known red-team source-days
known_attack_days = test[
    test["known_attack_matches"] > 0
]

flagged_attack_days = known_attack_days[
    known_attack_days["is_anomaly"] == 1
]

print("\nEvaluation results:")
print("Total test source-days:", len(test))
print("Flagged source-days:", test["is_anomaly"].sum())
print("Known attack source-days in test:", len(known_attack_days))
print("Known attack source-days flagged:", len(flagged_attack_days))

if len(known_attack_days) > 0:
    print(
        "Known attack source-day flag rate:",
        round(
            len(flagged_attack_days)
            / len(known_attack_days) * 100,
            2
        ),
        "%"
    )

output_file = "data/processed/full_behavior_ml_results.csv"

test.to_csv(output_file, index=False)

print("\nResults saved to:", output_file)

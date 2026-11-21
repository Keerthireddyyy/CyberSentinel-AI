
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Load daily behavioral summary
df = pd.read_csv(
    "data/processed/c17693_daily_activity.csv"
)

features = [
    "total_events",
    "unique_destinations",
    "unique_users",
    "failed_logins"
]

X = df[features]

# Scale behavioral features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train exploratory anomaly detector
model = IsolationForest(
    n_estimators=100,
    contamination=0.2,
    random_state=42
)

df["anomaly_label"] = model.fit_predict(X_scaled)

df["anomaly_score"] = model.decision_function(X_scaled)

df["is_anomaly"] = (
    df["anomaly_label"] == -1
).astype(int)

print("\nBehavioral anomaly detection results:")
print(
    df[
        [
            "dataset_day",
            "total_events",
            "unique_destinations",
            "unique_users",
            "failed_logins",
            "is_anomaly",
            "anomaly_score"
        ]
    ].to_string(index=False)
)

print("\nAnomalous days:")
print(
    df[df["is_anomaly"] == 1][
        [
            "dataset_day",
            "total_events",
            "unique_destinations",
            "unique_users"
        ]
    ].to_string(index=False)
)

df.to_csv(
    "data/processed/c17693_behavioral_anomalies.csv",
    index=False
)

print("\nBehavioral anomaly results saved!")


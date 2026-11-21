
import pandas as pd
from sklearn.ensemble import IsolationForest

# Load security events
df = pd.read_csv("data/security_logs.csv")

# Convert timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Extract numerical features
df["login_hour"] = df["timestamp"].dt.hour
df["is_failed"] = (df["status"] == "failed").astype(int)

# Count failed attempts for each user and IP
df["failed_attempts"] = df.groupby(
    ["user_id", "ip_address"]
)["is_failed"].transform("sum")

# Features for anomaly detection
features = df[
    ["login_hour", "is_failed", "failed_attempts"]
]

# Create Isolation Forest model
model = IsolationForest(
    n_estimators=100,
    contamination=0.2,
    random_state=42
)

# Train model and predict anomalies
df["anomaly"] = model.fit_predict(features)

# -1 means anomaly, 1 means normal
df["prediction"] = df["anomaly"].map({
    -1: "Suspicious",
    1: "Normal"
})

# Display results
print("\nMachine Learning Detection Results:\n")

print(df[
    ["user_id", "login_hour", "failed_attempts", "prediction"]
])

# Save results
df.to_csv("data/ml_detection_results.csv", index=False)

print("\nML detection results saved successfully!")

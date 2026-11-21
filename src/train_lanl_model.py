
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path("data/processed")

# Load engineered features
df = pd.read_csv(
    DATA_DIR / "lanl_features.csv"
)

features = [
    "is_failure",
    "is_success",
    "is_network_logon",
    "is_ntlm",
    "dataset_day"
]

X = df[features].fillna(0)

print("Training records:", len(X))

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train only on sampled unmatched events.
# These events are unlabeled, not confirmed benign.
training_mask = df["known_redteam_event"] == 0

model = IsolationForest(
    n_estimators=100,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)

print("\nTraining Isolation Forest...")

model.fit(X_scaled[training_mask])

# Score all events
# Lower scores indicate more unusual events.
df["anomaly_score"] = model.decision_function(X_scaled)

df["ml_anomaly"] = (
    model.predict(X_scaled) == -1
).astype(int)

# Compare with known red-team events
known_attacks = df[
    df["known_redteam_event"] == 1
]

detected_attacks = known_attacks[
    known_attacks["ml_anomaly"] == 1
]

print("\nModel results:")
print("Total flagged anomalies:", df["ml_anomaly"].sum())
print("Known red-team events:", len(known_attacks))
print("Known red-team events flagged:", len(detected_attacks))

if len(known_attacks) > 0:
    print(
        "Known attack flag rate:",
        round(
            len(detected_attacks) / len(known_attacks) * 100,
            2
        ),
        "%"
    )

# Save results
output_file = DATA_DIR / "lanl_ml_results.csv"

df.to_csv(output_file, index=False)

print("\nResults saved to:", output_file)


import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import train_test_split

# Step 1: Load dataset
df = pd.read_csv("data/large_security_logs.csv")

# Step 2: Convert timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Step 3: Create numerical features
df["login_hour"] = df["timestamp"].dt.hour
df["is_failed"] = (df["status"] == "failed").astype(int)

# Use only features available to the detector.
# Do not use simulated_attack as an input.
features = ["login_hour", "is_failed"]

X = df[features]
y = df["simulated_attack"]

# Step 4: Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Step 5: Create Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.109,
    random_state=42
)

# Step 6: Train model
model.fit(X_train)

# Step 7: Predict test anomalies
predictions = model.predict(X_test)

# Convert predictions:
# -1 = anomaly (1), 1 = normal (0)
y_pred = (predictions == -1).astype(int)

# Step 8: Evaluate
print("\nClassification Report:\n")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Normal", "Simulated Attack"],
        zero_division=0
    )
)

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# Step 9: Save test predictions
results = df.loc[X_test.index].copy()
results["ml_prediction"] = y_pred

results.to_csv(
    "data/model_predictions.csv",
    index=False
)

print("\nModel predictions saved successfully!")

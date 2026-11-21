
import pandas as pd
import numpy as np

# Make the generated dataset reproducible
rng = np.random.default_rng(42)

# Generate 1,000 synthetic login events
records = []
start_date = pd.Timestamp("2026-10-01")

for i in range(1000):
    user = f"user{rng.integers(100, 150)}"

    # Most events are normal
    is_attack = rng.random() < 0.10

    if is_attack:
        hour = int(rng.choice([0, 1, 2, 3, 4]))
        status = "failed"
        ip = f"203.0.113.{rng.integers(1, 255)}"
    else:
        hour = int(rng.integers(8, 19))
        status = rng.choice(
            ["success", "failed"],
            p=[0.95, 0.05]
        )
        ip = f"192.0.2.{rng.integers(1, 255)}"

    timestamp = (
        start_date
        + pd.Timedelta(days=int(rng.integers(0, 30)))
        + pd.Timedelta(hours=hour)
        + pd.Timedelta(
            minutes=int(rng.integers(0, 60))
        )
    )

    records.append({
        "timestamp": timestamp,
        "user_id": user,
        "ip_address": ip,
        "event_type": "login",
        "status": status,
        "simulated_attack": int(is_attack)
    })

df = pd.DataFrame(records)
df = df.sort_values("timestamp").reset_index(drop=True)

# Save separately so we preserve the original dataset
df.to_csv(
    "data/large_security_logs.csv",
    index=False
)

print("Dataset generated successfully!")
print("Total events:", len(df))
print("\nSimulated attack labels:")
print(df["simulated_attack"].value_counts())
print("\nFirst five events:")
print(df.head())

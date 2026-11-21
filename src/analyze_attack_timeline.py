
import pandas as pd

# Load previously extracted source-computer history
df = pd.read_csv(
    "data/processed/c17693_history.csv"
)

# Calculate dataset day from relative seconds
df["dataset_day"] = df["time"] // 86400

# Summarize authentication activity by day
daily = (
    df.groupby("dataset_day")
    .agg(
        total_events=("time", "size"),
        unique_destinations=("destination_computer", "nunique"),
        unique_users=("source_user", "nunique"),
        failed_logins=(
            "status",
            lambda x: (x == "Fail").sum()
        )
    )
    .reset_index()
)

print("\nC17693 daily authentication activity:")
print(daily.to_string(index=False))

daily.to_csv(
    "data/processed/c17693_daily_activity.csv",
    index=False
)

print("\nDaily activity analysis saved successfully!")


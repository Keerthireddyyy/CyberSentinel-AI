
import pandas as pd

# Step 1: Load the security logs
df = pd.read_csv("data/security_logs.csv")

# Convert timestamp strings into datetime objects
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort events by time
df = df.sort_values("timestamp")

print("Total security events:", len(df))

# Step 2: Create a list to store suspicious activities
alerts = []

# Step 3: Analyze login events for each user and IP
for (user, ip), group in df.groupby(
    ["user_id", "ip_address"]
):

    failed_logins = group[
        (group["event_type"] == "login") &
        (group["status"] == "failed")
    ]

    successful_logins = group[
        (group["event_type"] == "login") &
        (group["status"] == "success")
    ]

    # Step 4: Check failed attempts before each success
    for _, success in successful_logins.iterrows():

        start_time = success["timestamp"] - pd.Timedelta(
            minutes=10
        )

        recent_failures = failed_logins[
            (failed_logins["timestamp"] >= start_time) &
            (failed_logins["timestamp"] < success["timestamp"])
        ]

        # Step 5: Generate an alert
        if len(recent_failures) >= 5:

            alerts.append({
                "user_id": user,
                "ip_address": ip,
                "failed_attempts": len(recent_failures),
                "successful_login": success["timestamp"]
            })

# Step 6: Display results
if alerts:
    print("\nSuspicious activity detected!")

    for alert in alerts:
        print(alert)

else:
    print("\nNo suspicious login patterns detected.")

# Step 7: Save detected threats to a CSV file

if alerts:
    alerts_df = pd.DataFrame(alerts)

    alerts_df["severity"] = "HIGH"
    alerts_df["alert_type"] = "Multiple Failed Logins Followed by Success"

    alerts_df.to_csv(
        "data/security_alerts.csv",
        index=False
    )

    print("\nSecurity alerts saved successfully!")

else:
    print("\nNo alerts to save.")

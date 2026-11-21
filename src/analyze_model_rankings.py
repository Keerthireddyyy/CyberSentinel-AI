
import pandas as pd

FILE = "data/processed/full_behavior_ml_results.csv"

df = pd.read_csv(FILE)

# Lower scores indicate greater anomaly
df = df.sort_values("anomaly_score").reset_index(drop=True)

df["anomaly_rank"] = df.index + 1

df["anomaly_percentile"] = (
    df["anomaly_rank"] / len(df) * 100
)

attacks = df[
    df["known_attack_matches"] > 0
].copy()

print("\nKnown attack source-day anomaly rankings:")
print(
    attacks[
        [
            "source_computer",
            "dataset_day",
            "known_attack_matches",
            "total_events",
            "unique_destinations",
            "unique_users",
            "anomaly_score",
            "anomaly_rank",
            "anomaly_percentile",
            "is_anomaly"
        ]
    ].to_string(index=False)
)

print("\nRanking summary:")
print("Total test source-days:", len(df))
print("Known attack source-days:", len(attacks))

if len(attacks) > 0:
    print(
        "Median attack anomaly percentile:",
        round(attacks["anomaly_percentile"].median(), 2)
    )

    print(
        "Known attack source-days in top 1%:",
        (attacks["anomaly_percentile"] <= 1).sum()
    )

    print(
        "Known attack source-days in top 5%:",
        (attacks["anomaly_percentile"] <= 5).sum()
    )

    print(
        "Known attack source-days in top 10%:",
        (attacks["anomaly_percentile"] <= 10).sum()
    )

print("\nAnalysis completed!")


import pandas as pd
import math

BASELINE_FILE = (
    "data/processed/baseline_model_comparison.csv"
)

HISTORICAL_FILE = (
    "data/processed/historical_model_comparison.csv"
)

models = {
    "Baseline": pd.read_csv(BASELINE_FILE),
    "Historical": pd.read_csv(HISTORICAL_FILE)
}

alert_budgets = [0.01, 0.02, 0.05]

print("\nFIXED ALERT BUDGET EVALUATION")
print("=" * 65)

for budget in alert_budgets:
    print(f"\nTop {budget * 100:.0f}% alert budget")
    print("-" * 65)

    for name, df in models.items():

        # Lower anomaly score = more anomalous
        ranked = df.sort_values(
            ["anomaly_score", "source_computer", "dataset_day"],
            ascending=[True, True, True]
        )

        alert_count = math.ceil(len(ranked) * budget)

        alerts = ranked.head(alert_count)

        known_attack_days = (
            df["known_attack_matches"] > 0
        ).sum()

        detected = (
            alerts["known_attack_matches"] > 0
        ).sum()

        detection_rate = (
            detected / known_attack_days * 100
            if known_attack_days else 0
        )

        print(
            f"{name:12} | "
            f"Alerts: {alert_count:6} | "
            f"Known attack days found: "
            f"{detected:2}/{known_attack_days} | "
            f"Flag rate: {detection_rate:.2f}%"
        )

print("\nEvaluation completed!")

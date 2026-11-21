
import duckdb
from pathlib import Path

INPUT_FILE = "data/processed/full_network_behavior.parquet"
OUTPUT_FILE = "data/processed/historical_behavior_features.parquet"

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")

print("Building historical behavioral features...")

# Window calculations use earlier observed days only.
# No future-day information is included.
con.execute(
    """
    COPY (
        WITH history AS (
            SELECT
                *,
                COUNT(*) OVER (
                    PARTITION BY source_computer
                    ORDER BY dataset_day
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) AS history_days,

                AVG(total_events) OVER (
                    PARTITION BY source_computer
                    ORDER BY dataset_day
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) AS avg_events_7d,

                AVG(unique_destinations) OVER (
                    PARTITION BY source_computer
                    ORDER BY dataset_day
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) AS avg_destinations_7d,

                AVG(unique_users) OVER (
                    PARTITION BY source_computer
                    ORDER BY dataset_day
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) AS avg_users_7d,

                AVG(failed_logins) OVER (
                    PARTITION BY source_computer
                    ORDER BY dataset_day
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) AS avg_failures_7d

            FROM read_parquet(?)
        )
        SELECT
            *,
            total_events / (COALESCE(avg_events_7d, 0) + 1)
                AS events_vs_history,

            unique_destinations /
                (COALESCE(avg_destinations_7d, 0) + 1)
                AS destinations_vs_history,

            unique_users /
                (COALESCE(avg_users_7d, 0) + 1)
                AS users_vs_history,

            failed_logins /
                (COALESCE(avg_failures_7d, 0) + 1)
                AS failures_vs_history

        FROM history
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
    [OUTPUT_FILE, INPUT_FILE]
)

print("\nHistorical features created!")

summary = con.execute(
    """
    SELECT
        COUNT(*) AS total_records,
        COUNT(*) FILTER (WHERE history_days >= 3)
            AS records_with_history,
        COUNT(DISTINCT source_computer)
            AS unique_computers
    FROM read_parquet(?)
    """,
    [OUTPUT_FILE]
).fetchone()

print("Total source-day records:", summary[0])
print("Records with at least 3 previous observed days:", summary[1])
print("Unique source computers:", summary[2])
print("Saved to:", OUTPUT_FILE)

con.close()

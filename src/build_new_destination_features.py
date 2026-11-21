
import duckdb
from pathlib import Path

DATA_DIR = Path("data/processed")

FIRST_SEEN_FILE = (
    DATA_DIR / "first_seen_connections_full.parquet"
)

BEHAVIOR_FILE = (
    DATA_DIR / "historical_behavior_features.parquet"
)

OUTPUT_FILE = (
    DATA_DIR / "behavior_with_new_destinations.parquet"
)

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")

print("Building new-destination behavioral features...")

# Count first-seen destination relationships per source/day.
# These are new inter-computer connections.
con.execute(
    """
    COPY (
        WITH new_destinations AS (
            SELECT
                source_computer,
                first_seen_day AS dataset_day,
                COUNT(*) AS new_destinations
            FROM read_parquet(?)
            GROUP BY
                source_computer,
                first_seen_day
        )
        SELECT
            b.*,
            COALESCE(n.new_destinations, 0)
                AS new_destinations,

            COALESCE(n.new_destinations, 0) * 1.0
                / GREATEST(b.unique_destinations, 1)
                AS new_destination_ratio

        FROM read_parquet(?) AS b

        LEFT JOIN new_destinations AS n
          ON b.source_computer = n.source_computer
         AND b.dataset_day = n.dataset_day
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
    [
        str(OUTPUT_FILE),
        str(FIRST_SEEN_FILE),
        str(BEHAVIOR_FILE)
    ]
)

print("\nNew-destination features created!")

result = con.execute(
    """
    SELECT
        COUNT(*) AS total_records,
        COUNT(*) FILTER (
            WHERE new_destinations > 0
        ) AS records_with_new_destinations,
        MAX(new_destinations) AS maximum_new_destinations,
        AVG(new_destination_ratio)
            AS average_new_destination_ratio
    FROM read_parquet(?)
    """,
    [str(OUTPUT_FILE)]
).fetchone()

print("Total source-day records:", result[0])
print("Records with new destinations:", result[1])
print("Maximum new destinations in one source-day:", result[2])
print(
    "Average new-destination ratio:",
    round(result[3], 4)
)

print("Saved to:", OUTPUT_FILE)

con.close()

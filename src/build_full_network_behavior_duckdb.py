
import duckdb
from pathlib import Path

DATA_DIR = Path("data/processed")
PARQUET_DIR = DATA_DIR / "lanl_parquet"
OUTPUT_FILE = DATA_DIR / "full_network_behavior.parquet"
TEMP_DIR = DATA_DIR / "duckdb_temp"

TEMP_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")
con.execute(
    f"SET temp_directory = '{TEMP_DIR.as_posix()}'"
)

print("Starting full-network behavioral aggregation...")

con.execute(
    """
    COPY (
        SELECT
            source_computer,
            dataset_day,
            COUNT(*) AS total_events,
            COUNT(DISTINCT destination_computer)
                AS unique_destinations,
            COUNT(DISTINCT source_user)
                AS unique_users,
            COUNT(*) FILTER (WHERE status = 'Fail')
                AS failed_logins,
            COUNT(*) FILTER (WHERE status = 'Fail')
                * 1.0 / COUNT(*) AS failure_rate
        FROM read_parquet(?)
        WHERE source_computer IS NOT NULL
        GROUP BY source_computer, dataset_day
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
    [
        str(OUTPUT_FILE),
        str(PARQUET_DIR / "auth_part_*.parquet")
    ]
)

print("\nFull-network behavioral dataset created!")

summary = con.execute(
    """
    SELECT
        COUNT(*) AS source_day_records,
        COUNT(DISTINCT source_computer)
            AS unique_source_computers,
        SUM(total_events) AS total_events
    FROM read_parquet(?)
    """,
    [str(OUTPUT_FILE)]
).fetchone()

print("Source-day records:", summary[0])
print("Unique source computers:", summary[1])
print("Total events represented:", summary[2])
print("Saved to:", OUTPUT_FILE)

con.close()

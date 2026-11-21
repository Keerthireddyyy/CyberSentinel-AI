
import duckdb
from pathlib import Path

BATCH_DIR = Path(
    "data/processed/user_connection_batches"
)

OUTPUT_FILE = Path(
    "data/processed/first_seen_user_destinations.parquet"
)

TEMP_DIR = Path(
    "data/processed/duckdb_temp"
)

TEMP_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(
    BATCH_DIR.glob("user_connections_batch_*.parquet")
)

print("Starting user-destination relationship merge...")
print("Batch files found:", len(files), flush=True)

if len(files) != 106:
    raise RuntimeError(
        f"Expected 106 batches, found {len(files)}"
    )

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")
con.execute(
    f"SET temp_directory = '{TEMP_DIR.as_posix()}'"
)

input_pattern = str(
    BATCH_DIR / "user_connections_batch_*.parquet"
)

print("Merging duplicate user-destination pairs...", flush=True)

# Keep the earliest day for each unique relationship.
# DuckDB COPY parameter order is output first, input second.
con.execute(
    """
    COPY (
        SELECT
            source_user,
            destination_computer,
            MIN(first_seen_day) AS first_seen_day
        FROM read_parquet(?)
        GROUP BY
            source_user,
            destination_computer
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
    [str(OUTPUT_FILE), input_pattern]
)

print("Merge completed!", flush=True)
print("Validating merged dataset...", flush=True)

summary = con.execute(
    """
    SELECT
        COUNT(*) AS unique_user_destination_pairs,
        COUNT(DISTINCT source_user) AS unique_users,
        COUNT(DISTINCT destination_computer) AS unique_destinations,
        MIN(first_seen_day) AS earliest_day,
        MAX(first_seen_day) AS latest_day
    FROM read_parquet(?)
    """,
    [str(OUTPUT_FILE)]
).fetchone()

print("\nMERGED USER RELATIONSHIP SUMMARY")
print("=" * 55)
print("Unique user-destination pairs:", summary[0])
print("Unique users:", summary[1])
print("Unique destination computers:", summary[2])
print("Earliest first-seen day:", summary[3])
print("Latest first-seen day:", summary[4])

print("\nOutput file:", OUTPUT_FILE)
print("User relationship merge completed successfully!")

con.close()
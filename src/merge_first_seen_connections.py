
import duckdb
from pathlib import Path

BATCH_DIR = Path("data/processed/connection_batches")
OUTPUT_DIR = Path("data/processed")
TEMP_DIR = OUTPUT_DIR / "duckdb_temp"

OUTPUT_FILE = (
    OUTPUT_DIR / "first_seen_connections_full.parquet"
)

TEMP_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(
    BATCH_DIR.glob("connections_batch_*.parquet")
)

print("Connection batch files found:", len(files))

if len(files) != 106:
    raise RuntimeError(
        f"Expected 106 batch files, found {len(files)}"
    )

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")
con.execute(
    f"SET temp_directory = '{TEMP_DIR.as_posix()}'"
)

print("\nMerging connection batches...", flush=True)

# Parameter order: COPY output first, read_parquet input second.
con.execute(
    """
    COPY (
        SELECT
            source_computer,
            destination_computer,
            MIN(first_seen_day) AS first_seen_day
        FROM read_parquet(?)
        GROUP BY
            source_computer,
            destination_computer
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
    [
        str(OUTPUT_FILE),
        str(BATCH_DIR / "connections_batch_*.parquet")
    ]
)

print("\nFull first-seen connection dataset created!")

result = con.execute(
    """
    SELECT
        COUNT(*) AS unique_connections,
        COUNT(DISTINCT source_computer)
            AS unique_sources,
        COUNT(DISTINCT destination_computer)
            AS unique_destinations,
        MIN(first_seen_day) AS earliest_day,
        MAX(first_seen_day) AS latest_day
    FROM read_parquet(?)
    """,
    [str(OUTPUT_FILE)]
).fetchone()

print("Unique source-destination pairs:", result[0])
print("Unique source computers:", result[1])
print("Unique destination computers:", result[2])
print("Earliest first-seen day:", result[3])
print("Latest first-seen day:", result[4])
print("Saved to:", OUTPUT_FILE)

con.close()

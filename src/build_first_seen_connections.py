
import duckdb
from pathlib import Path

PARQUET_DIR = Path("data/processed/lanl_parquet")
OUTPUT_DIR = Path("data/processed")
TEMP_DIR = OUTPUT_DIR / "duckdb_temp"

TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Start with 10 files for a safe test.
TEST_FILES = 10

files = sorted(
    PARQUET_DIR.glob("auth_part_*.parquet")
)

selected_files = files[:TEST_FILES]

if len(selected_files) != TEST_FILES:
    raise RuntimeError(
        f"Expected {TEST_FILES} files, found {len(selected_files)}"
    )

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")
con.execute(
    f"SET temp_directory = '{TEMP_DIR.as_posix()}'"
)

print("Building first-seen connection test...")
print("Parquet files selected:", len(selected_files))

# This is a test output, not the full dataset.
output_file = (
    OUTPUT_DIR / "first_seen_connections_test.parquet"
)

# DuckDB can read a list of Parquet paths.
paths = [str(path) for path in selected_files]

con.execute(
    """
    COPY (
        SELECT
            source_computer,
            destination_computer,
            MIN(dataset_day) AS first_seen_day
        FROM read_parquet(?)
        WHERE source_computer IS NOT NULL
          AND destination_computer IS NOT NULL
          AND source_computer <> destination_computer
        GROUP BY
            source_computer,
            destination_computer
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
    [str(output_file), paths]
)

result = con.execute(
    """
    SELECT
        COUNT(*) AS unique_connections,
        COUNT(DISTINCT source_computer) AS source_computers,
        MIN(first_seen_day) AS earliest_day,
        MAX(first_seen_day) AS latest_day
    FROM read_parquet(?)
    """,
    [str(output_file)]
).fetchone()

print("\nFirst-seen connection test completed!")
print("Unique source-destination pairs:", result[0])
print("Source computers:", result[1])
print("Earliest first-seen day:", result[2])
print("Latest first-seen day:", result[3])
print("Saved to:", output_file)

con.close()


import duckdb
from pathlib import Path

PARQUET_DIR = Path("data/processed/lanl_parquet")
OUTPUT_DIR = Path("data/processed")
BATCH_DIR = OUTPUT_DIR / "connection_batches"
TEMP_DIR = OUTPUT_DIR / "duckdb_temp"

BATCH_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 20

files = sorted(
    PARQUET_DIR.glob("auth_part_*.parquet")
)

if len(files) != 2103:
    raise RuntimeError(
        f"Expected 2103 files, found {len(files)}"
    )

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")
con.execute(
    f"SET temp_directory = '{TEMP_DIR.as_posix()}'"
)

total_batches = (
    len(files) + BATCH_SIZE - 1
) // BATCH_SIZE

print("Starting full first-seen connection extraction...")
print("Input Parquet files:", len(files))
print("Total batches:", total_batches)

for batch_number, start in enumerate(
    range(0, len(files), BATCH_SIZE),
    start=1
):
    batch_files = files[start:start + BATCH_SIZE]

    output_file = (
        BATCH_DIR /
        f"connections_batch_{batch_number:04d}.parquet"
    )

    # Reuse completed batches if the process is restarted.
    if output_file.exists():
        print(
            f"Skipping existing batch "
            f"{batch_number}/{total_batches}",
            flush=True
        )
        continue

    paths = [str(path) for path in batch_files]

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

    print(
        f"Completed batch {batch_number}/{total_batches}",
        flush=True
    )

print("\nAll connection batches completed!")
print("Batch directory:", BATCH_DIR)

con.close()

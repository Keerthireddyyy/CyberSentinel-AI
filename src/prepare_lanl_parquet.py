
import pandas as pd
import duckdb
from pathlib import Path

AUTH_FILE = Path("data/raw/auth.txt.gz")
OUTPUT_DIR = Path("data/processed/lanl_parquet")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

columns = [
    "time",
    "source_user",
    "destination_user",
    "source_computer",
    "destination_computer",
    "auth_type",
    "logon_type",
    "auth_orientation",
    "status"
]

con = duckdb.connect()
con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")

reader = pd.read_csv(
    AUTH_FILE,
    compression="gzip",
    header=None,
    names=columns,
    chunksize=500_000,
    na_values=["?"]
)

print("Starting LANL Parquet conversion...")

total_rows = 0


for chunk_number, chunk in enumerate(reader, start=1):

    chunk["dataset_day"] = (
        chunk["time"] // 86400
    ).astype("int32")

    output_file = (
        OUTPUT_DIR / f"auth_part_{chunk_number:05d}.parquet"
    )

    con.register("auth_chunk", chunk)

    con.execute(
        """
        COPY (
            SELECT
                time,
                source_user,
                source_computer,
                destination_computer,
                status,
                dataset_day
            FROM auth_chunk
        )
        TO ?
        (FORMAT PARQUET, COMPRESSION ZSTD)
        """,
        [str(output_file)]
    )

    con.unregister("auth_chunk")

    total_rows += len(chunk)

    if chunk_number % 100 == 0:
        print(
            f"Converted {total_rows:,} events "
            f"into {chunk_number} Parquet files"
        )

print("\nConversion completed!")
print("Total events:", total_rows)
print(
    "Parquet files created:",
    len(list(OUTPUT_DIR.glob("auth_part_*.parquet")))
)
print("Output directory:", OUTPUT_DIR)

con.close()

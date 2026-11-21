
import duckdb
from pathlib import Path

DATA_DIR = Path("data/processed/lanl_parquet")

files = list(DATA_DIR.glob("auth_part_*.parquet"))

print("Parquet files found:", len(files))

con = duckdb.connect()
con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")

# Count records using Parquet metadata where possible
result = con.execute(
    """
    SELECT COUNT(*)
    FROM read_parquet(?)
    """,
    [str(DATA_DIR / "auth_part_*.parquet")]
).fetchone()

total_rows = result[0]

print("Total Parquet records:", total_rows)

expected_rows = 1_051_430_459

if total_rows == expected_rows and len(files) == 2103:
    print("\nVALIDATION SUCCESSFUL!")
else:
    print("\nVALIDATION FAILED - check file counts.")

con.close()

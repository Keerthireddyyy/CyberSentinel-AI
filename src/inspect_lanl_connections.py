
import duckdb

PARQUET_PATH = (
    "data/processed/lanl_parquet/auth_part_*.parquet"
)

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")

print("\nLANL AUTHENTICATION SCHEMA")
print("=" * 50)

schema = con.execute(
    """
    DESCRIBE SELECT *
    FROM read_parquet(?)
    """,
    [PARQUET_PATH]
).df()

print(schema.to_string(index=False))

print("\nDATASET DAY RANGE")
print("=" * 50)

days = con.execute(
    """
    SELECT
        MIN(dataset_day) AS first_day,
        MAX(dataset_day) AS last_day,
        COUNT(DISTINCT dataset_day) AS unique_days
    FROM read_parquet(?)
    """,
    [PARQUET_PATH]
).fetchone()

print("First day:", days[0])
print("Last day:", days[1])
print("Unique days:", days[2])

print("\nSAMPLE AUTHENTICATION CONNECTIONS")
print("=" * 50)

sample = con.execute(
    """
    SELECT
        dataset_day,
        source_computer,
        destination_computer,
        source_user,
        status
    FROM read_parquet(?)
    LIMIT 10
    """,
    [PARQUET_PATH]
).df()

print(sample.to_string(index=False))

con.close()

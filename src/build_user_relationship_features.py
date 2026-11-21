
import duckdb
from pathlib import Path

AUTH_DIR = Path("data/processed/lanl_parquet")

USER_RELATIONSHIPS = (
    "data/processed/first_seen_user_destinations.parquet"
)

BEHAVIOR_FILE = (
    "data/processed/behavior_with_new_destinations.parquet"
)

OUTPUT_FILE = (
    "data/processed/behavior_with_user_relationships.parquet"
)

TEMP_DIR = Path("data/processed/duckdb_temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

auth_pattern = str(AUTH_DIR / "auth_part_*.parquet")

con = duckdb.connect()

con.execute("SET threads = 2")
con.execute("SET memory_limit = '2GB'")
con.execute(
    f"SET temp_directory = '{TEMP_DIR.as_posix()}'"
)

print("Building new user-destination features...", flush=True)

# Find distinct source/user/destination/day combinations
# that occur on the relationship's first-seen day.
#
# A relationship can be attributed to multiple source
# computers if they used it on the same first-seen day.

query = """
COPY (
    WITH first_day_source_relationships AS (
        SELECT DISTINCT
            a.source_computer,
            a.dataset_day,
            a.source_user,
            a.destination_computer
        FROM read_parquet(?) a
        INNER JOIN read_parquet(?) r
            ON a.source_user = r.source_user
           AND a.destination_computer = r.destination_computer
           AND a.dataset_day = r.first_seen_day
        WHERE a.source_computer IS NOT NULL
    ),
    new_user_relationships AS (
        SELECT
            source_computer,
            dataset_day,
            COUNT(*) AS new_user_destination_pairs
        FROM first_day_source_relationships
        GROUP BY
            source_computer,
            dataset_day
    )
    SELECT
        b.*,
        COALESCE(
            n.new_user_destination_pairs, 0
        ) AS new_user_destination_pairs,
        COALESCE(
            n.new_user_destination_pairs, 0
        ) * 1.0
        / GREATEST(b.total_events, 1)
        AS new_user_relationship_ratio
    FROM read_parquet(?) b
    LEFT JOIN new_user_relationships n
        ON b.source_computer = n.source_computer
       AND b.dataset_day = n.dataset_day
)
TO ?
(FORMAT PARQUET, COMPRESSION ZSTD)
"""

# In this DuckDB COPY query, output-path parameter
# binding precedes the read_parquet parameters.
con.execute(
    query,
    [
        OUTPUT_FILE,
        auth_pattern,
        USER_RELATIONSHIPS,
        BEHAVIOR_FILE
    ]
)

print("Feature generation completed!", flush=True)

summary = con.execute(
    """
    SELECT
        COUNT(*) AS total_records,
        COUNT(*) FILTER (
            WHERE new_user_destination_pairs > 0
        ) AS records_with_new_relationships,
        MAX(new_user_destination_pairs) AS max_new_relationships,
        AVG(new_user_relationship_ratio) AS average_ratio
    FROM read_parquet(?)
    """,
    [OUTPUT_FILE]
).fetchone()

print("\nUSER RELATIONSHIP FEATURE SUMMARY")
print("=" * 60)
print("Total source-day records:", summary[0])
print("Records with new relationships:", summary[1])
print("Maximum new relationships in one source-day:", summary[2])
print("Average new user-relationship ratio:", round(summary[3], 4))

print("\nOutput file:", OUTPUT_FILE)
print("User relationship feature engineering completed!")

con.close()

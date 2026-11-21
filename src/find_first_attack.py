
import pandas as pd

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

redteam_columns = [
    "time",
    "source_user",
    "source_computer",
    "destination_computer"
]

# Load known red-team events
redteam = pd.read_csv(
    "data/raw/redteam.txt.gz",
    compression="gzip",
    header=None,
    names=redteam_columns
)

first_attack_time = int(redteam["time"].min())

print("First known attack timestamp:", first_attack_time)

match_columns = [
    "time",
    "source_user",
    "source_computer",
    "destination_computer"
]

redteam_keys = pd.MultiIndex.from_frame(
    redteam[match_columns]
)

# Stream authentication data in chunks
reader = pd.read_csv(
    "data/raw/auth.txt.gz",
    compression="gzip",
    header=None,
    names=columns,
    chunksize=100_000,
    na_values=["?"]
)

found = False

for chunk_number, chunk in enumerate(reader, start=1):

    # Skip chunks before the first known attack
    if chunk["time"].max() < first_attack_time:
        continue

    # Match the authentication events
    auth_keys = pd.MultiIndex.from_frame(
        chunk[match_columns]
    )

    matches = chunk.loc[
        auth_keys.isin(redteam_keys)
    ]

    
    if not matches.empty:
        print("\nKnown red-team authentication event found!")
        print(matches.head().to_string(index=False))
        print("\nChunk number:", chunk_number)
        
        # Create a folder for processed datasets
        from pathlib import Path
        
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save confirmed attack matches
        output_file = output_dir / "first_known_attacks.csv"
        
        matches.to_csv(output_file, index=False)
        
        print("\nAttack records saved to:", output_file)
        
        found = True
        break


    if chunk_number % 100 == 0:
        print(
            f"Scanned {chunk_number * 100_000:,} "
            "authentication events..."
        )

if not found:
    print(
        "\nNo exact matches found. "
        "We may need to inspect the matching fields."
    )


import pandas as pd

# Load known red-team authentication matches
df = pd.read_csv(
    "data/processed/lanl_known_attacks.csv"
)

print("\nTotal known attack matches:", len(df))

print("\nAuthentication status:")
print(df["status"].value_counts(dropna=False))

print("\nAuthentication types:")
print(df["auth_type"].value_counts(dropna=False))

print("\nLogon types:")
print(df["logon_type"].value_counts(dropna=False))

print("\nMost frequent source computers:")
print(df["source_computer"].value_counts().head(10))

print("\nMost frequent destination computers:")
print(df["destination_computer"].value_counts().head(10))

print("\nMost frequent users:")
print(df["source_user"].value_counts().head(10))

print("\nAttack time range:")
print("Earliest:", df["time"].min())
print("Latest:", df["time"].max())

print("\nAnalysis completed!")

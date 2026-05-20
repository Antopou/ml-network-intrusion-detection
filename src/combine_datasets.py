from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

files = [
    ROOT / "data/raw/Monday-WorkingHours.pcap_ISCX.csv",
    ROOT / "data/raw/Tuesday-WorkingHours.pcap_ISCX.csv",
    ROOT / "data/raw/Wednesday-workingHours.pcap_ISCX.csv",
    ROOT / "data/raw/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    ROOT / "data/raw/Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    ROOT / "data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv",
    ROOT / "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    ROOT / "data/raw/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
]

dfs = []
for path in files:
    print(f"  Loading {path.name}...")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    dfs.append(df)

print("Combining...")
combined = pd.concat(dfs, ignore_index=True)

print("Cleaning (removing inf and NaN rows)...")
rows_before = len(combined)
combined.replace([np.inf, -np.inf], np.nan, inplace=True)
combined.dropna(inplace=True)
rows_after = len(combined)
print(f"  Dropped {rows_before - rows_after:,} rows with inf/NaN values")

out_path = ROOT / "data/processed/combined_dataset.csv"
combined.to_csv(out_path, index=False)
print(f"\nSaved {rows_after:,} rows to {out_path}")

print("\nClass distribution:")
print(combined["Label"].value_counts().to_string())

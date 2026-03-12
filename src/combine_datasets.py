import pandas as pd

files = [
    "data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "data/raw/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "data/raw/Wednesday-workingHours.pcap_ISCX.csv"
]

dfs = []
for file in files:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv("data/processed/combined_dataset.csv", index=False)

print("Combined dataset saved.")
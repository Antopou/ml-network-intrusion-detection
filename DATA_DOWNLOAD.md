Large data files were removed from this repository to keep the Git history small.

To reproduce the full working environment on another machine:

1. Download the original dataset CSVs (these are large):
   - Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
   - Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
   - Friday-WorkingHours-Morning.pcap_ISCX.csv
   - Monday-WorkingHours.pcap_ISCX.csv
   - Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
   - Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
   - Tuesday-WorkingHours.pcap_ISCX.csv
   - Wednesday-workingHours.pcap_ISCX.csv
   - combined_dataset.csv

2. Place the raw CSVs under `data/raw/` and the combined file under `data/processed/`.

3. Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Run the preprocessing or training scripts as described in the project README.

Notes:
- A local branch `backup-before-filter` contains your pre-filter local history (kept locally). Do NOT push that branch to the remote unless you intentionally want the large files back on GitHub.
- If you need me to host the dataset elsewhere (e.g., a release, cloud storage, or Git LFS), I can help set that up.

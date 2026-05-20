# Dataset Download & Full Setup Guide

This guide gets you from a completely fresh machine (no dataset, no model, nothing)
to a fully running project with trained model and working dashboard.

Follow every step in order. Do not skip steps.

---

## Step 1 — Clone the project

```bash
git clone <your-repo-url>
cd ml-network-intrusion-detection
```

---

## Step 2 — Download the CICIDS2017 dataset

**Official source:** University of New Brunswick, Canada
**Download page:** https://www.unb.ca/cic/datasets/ids-2017.html

### How to download:

1. Go to https://www.unb.ca/cic/datasets/ids-2017.html
2. Scroll down to the **"Download"** section
3. Click **"MachineLearningCVE"** — this is the pre-extracted CSV version (what this project uses)
4. You will need to fill in a short registration form (name, institution, email)
5. You will receive a download link by email or directly on the page
6. Download all 8 CSV files listed below

### Files to download (all 8 are required):

| Filename | Size (approx) | Contains |
|---|---|---|
| `Monday-WorkingHours.pcap_ISCX.csv` | ~50 MB | BENIGN only |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | ~90 MB | BENIGN, FTP-Patator, SSH-Patator |
| `Wednesday-workingHours.pcap_ISCX.csv` | ~170 MB | BENIGN, DoS attacks, Heartbleed |
| `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | ~17 MB | BENIGN, Web Attacks |
| `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv` | ~27 MB | BENIGN, Infiltration |
| `Friday-WorkingHours-Morning.pcap_ISCX.csv` | ~58 MB | BENIGN, Bot |
| `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` | ~80 MB | BENIGN, DDoS |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | ~47 MB | BENIGN, PortScan |

**Total download size: ~540 MB**

### Where to put the files:

```
ml-network-intrusion-detection/
└── data/
    └── raw/
        ├── Monday-WorkingHours.pcap_ISCX.csv
        ├── Tuesday-WorkingHours.pcap_ISCX.csv
        ├── Wednesday-workingHours.pcap_ISCX.csv
        ├── Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
        ├── Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
        ├── Friday-WorkingHours-Morning.pcap_ISCX.csv
        ├── Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
        └── Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
```

Create the folder if it does not exist:
```bash
mkdir -p data/raw data/processed artifacts/models artifacts/logs
```

---

## Step 3 — Set up Python environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

---

## Step 4 — Combine all 8 CSV files into one dataset

```bash
cd src
python combine_datasets.py
```

Expected output:
```
  Loading Monday-WorkingHours.pcap_ISCX.csv...
  Loading Tuesday-WorkingHours.pcap_ISCX.csv...
  ...
  Dropped 2,867 rows with inf/NaN values
  Saved 2,827,876 rows to data/processed/combined_dataset.csv

  Class distribution:
  BENIGN        2271320
  DoS Hulk       230124
  PortScan       158804
  ...
```

This creates `data/processed/combined_dataset.csv` (~1.5 GB).
**Takes about 2–3 minutes.**

---

## Step 5 — Train the model

```bash
python train_model.py
```

Expected output:
```
[1/4] Loading dataset...
      Loaded 2,827,876 rows, 79 columns
[2/4] Preprocessing (scaling + train/test split)...
      Train: 2,262,300 rows | Test: 565,576 rows | Features: 78
[3/4] Training Random Forest (this may take a few minutes)...
      Class distribution in training set:
      BENIGN    1817055
      DoS Hulk   184099
      ...
      Training complete.
[4/4] Saving artifacts...
      Model    -> artifacts/models/model.pkl
      Scaler   -> artifacts/models/scaler.pkl
      Features -> artifacts/models/feature_columns.pkl

Done. All artifacts saved.
```

**Takes about 5–10 minutes.**
After this step you will have 3 files in `artifacts/models/`:
- `model.pkl` — the trained Random Forest
- `scaler.pkl` — the fitted StandardScaler
- `feature_columns.pkl` — the ordered list of 78 feature names

---

## Step 6 — Evaluate the model (optional but recommended)

```bash
python evaluate_model.py
```

Prints a full classification report and AUC-ROC score.
Confirm you see accuracy above 0.998 before launching the dashboard.

---

## Step 7 — Launch the dashboard

```bash
streamlit run dashboard.py
```

Open your browser at: http://localhost:8501

Upload any of the raw CSV files from `data/raw/` to test predictions.

---

## Step 8 — Run model comparison (optional)

Only needed if you want to regenerate the comparison table and charts.
**Warning: takes ~30 minutes.**

```bash
python compare_models.py
```

This retrains 3 models and saves results to `artifacts/logs/model_comparison.csv`.

---

## Step 9 — Run the EDA notebook (optional)

Only needed to regenerate the 5 chart PNG files in `docs/`.

```bash
cd ..
jupyter notebook notebooks/eda.ipynb
```

Run all cells top to bottom. Charts are saved to `docs/`.

---

## Quick reference — command order for a fresh machine

```bash
# 1. Setup
git clone <your-repo-url> && cd ml-network-intrusion-detection
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data/raw data/processed artifacts/models artifacts/logs

# 2. Put the 8 CSVs into data/raw/  (download from UNB link above)

# 3. Build dataset + train
cd src
python combine_datasets.py
python train_model.py

# 4. Launch
streamlit run dashboard.py
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `FileNotFoundError: data/raw/...csv` | CSV not placed in the right folder | Check filenames match exactly, including capitalisation |
| `FileNotFoundError: artifacts/models/model.pkl` | Training not run yet | Run `python train_model.py` first |
| `FileNotFoundError: artifacts/models/scaler.pkl` | Old model from before Task 1 fix | Re-run `python train_model.py` |
| `ModuleNotFoundError: streamlit` | venv not activated or packages not installed | Run `pip install -r requirements.txt` |
| Dashboard shows no local CSV files | Running from wrong directory | Always run scripts from inside `src/` |
| `UserWarning: least populated class has only 1 member` | Heartbleed class too rare for CV folds | Expected warning — safe to ignore |

---

## Notes

- The raw CSVs and combined dataset are excluded from git (see `.gitignore`) — they are too large
- The trained model files (`artifacts/`) are also excluded from git — always retrain on the new machine
- All scripts resolve paths relative to the project root so they work whether run from `src/` or the project root

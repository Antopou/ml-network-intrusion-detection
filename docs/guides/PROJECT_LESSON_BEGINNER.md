# Beginner Lesson: How This NIDS Project Works

This guide explains your project as if the reader is new to cybersecurity and machine learning.

---

## 1) What this project does (simple version)

Your project is an **AI security guard for network traffic**.

- It reads network traffic data (from CSV files).
- It learns patterns of normal vs attack behavior.
- It predicts whether new traffic is benign or malicious.
- It shows the results in a dashboard and simulation view.

---

## 2) Where things come from in this project

### Data
- Raw traffic CSVs: `data/raw/`
- Combined training dataset: `data/processed/combined_dataset.csv`

### Model
- Trained model file: `artifacts/models/model.pkl`

### Main code
- Dashboard app: `src/dashboard.py`
- Train model: `src/train_model.py`
- Evaluate model: `src/evaluate_model.py`
- Live simulation script: `src/simulate_live_traffic.py`

---

## 3) End-to-end flow (important)

1. **Prepare data**
   - Traffic flows are loaded from CSV.
   - Missing/invalid values are cleaned.
2. **Train model**
   - Random Forest is trained on processed features.
   - Saved as `artifacts/models/model.pkl`.
3. **Evaluate model**
   - Classification report + confusion matrix are printed.
4. **Use dashboard**
   - Upload CSV, get predictions, confidence, and summaries.
5. **Run simulation**
   - Process traffic in batches like a live monitoring stream.

---

## 4) How to run the project

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Train
```bash
python src/train_model.py
```

### Evaluate
```bash
python src/evaluate_model.py
```

### Dashboard
```bash
streamlit run src/dashboard.py
```

---

## 5) Dashboard lesson: tab by tab

The dashboard has two tabs:

## A) Prediction Dashboard

Use this when you want standard analysis on one CSV file.

### What happens when you upload CSV

1. **Cleaning**
   - Removes bad numeric values (`inf`, `NaN`).
2. **Label detection**
   - Looks for `Label` column (with robust matching).
3. **Schema check**
   - Ensures your file has the expected feature columns.
4. **Numeric coercion**
   - Converts features to numbers, drops invalid rows.
5. **Scaling alignment**
   - Applies the same scaling style used in training.
6. **Prediction**
   - Model predicts attack class.
7. **Confidence**
   - Uses `predict_proba` to show certainty.

### What each section means

- **Dataset Preview**: first rows so you can verify input.
- **Dataset Info**: row/column count and cleaning status.
- **Prediction Results**: counts per predicted class.
- **Attack Distribution**: chart of predicted classes.
- **Prediction Confidence**:
  - Average confidence: overall certainty
  - Lowest confidence: weakest decision
- **Actual vs Predicted Sample**:
  - Only appears if label column exists
  - Lets you compare ground truth vs model output
- **Quick Accuracy**:
  - Fast estimate on uploaded labeled file
- **Prediction Summary**:
  - BENIGN count vs attack count
- **Top 15 Most Important Features**:
  - Shows which features most influence model decisions
- **Download Predictions CSV**:
  - Saves output for report/analysis

---

## B) Live Simulation

Use this when you want to demonstrate near real-time behavior.

Instead of processing the entire CSV as one block, it processes it in **windows (batches)**.

### Controls explained

- **Simulation data source**
  - `Uploaded file`: use file from uploader
  - `Local sample file`: use pre-existing file from `data/raw`

- **Batch size**
  - Number of rows processed per simulation step.
  - Example: `500` means every step reads 500 traffic rows.
  - Smaller batch = more steps, more granular timeline.
  - Larger batch = fewer steps, faster completion.

- **Max batches**
  - How many steps to run before stopping.
  - Example: If batch size is 500 and max batches is 8, simulation processes up to 4000 rows.

- **Delay between batches (sec)**
  - Wait time between simulation steps.
  - `0.7` sec makes it look like live streaming.
  - `0` sec runs quickly for testing.

- **High-confidence alert threshold**
  - Confidence cutoff for “strong alerts.”
  - Example: `0.80` means alert only if model is at least 80% confident.

- **Shuffle rows before simulation**
  - Mixes rows so batch windows are varied.
  - Good for demo realism if original file is ordered.

### Simulation output meaning

For each batch, you get:

- **Status**: `ALERT` if attacks detected, else `OK`
- **Predicted Attacks**: count in that batch
- **Attack Rate**: attack percentage in that batch
- **Top Attack**: most common attack type in that batch
- **Avg Confidence**: model certainty in that batch
- **High-Confidence Alerts**: attack predictions above your threshold

At the end:
- total predicted attacks
- rows simulated
- downloadable batch log CSV

---

## 6) Why we need each part

- **Cleaning**: bad values can crash or mislead the model.
- **Schema validation**: prevents wrong-column inputs from producing fake results.
- **Scaling alignment**: model must see input in the same feature style used during training.
- **Confidence scores**: useful for deciding which alerts deserve urgent action.
- **Simulation**: helps non-experts understand operational monitoring, not just offline testing.

---

## 7) Common beginner mistakes (and fixes)

### “No columns to parse from file”
- Cause: uploaded stream got consumed.
- Fix: dashboard now reads upload bytes safely.

### “Schema mismatch: missing required columns”
- Cause: uploaded CSV doesn’t match training feature set.
- Fix: use compatible CICIDS-format data or rebuild processed dataset.

### Model file not found
- Cause: model not trained yet.
- Fix:
```bash
python src/train_model.py
```

### Simulation runs but no alerts
- Cause: selected segment may mostly be benign.
- Fix: increase max batches, change source file, or reduce threshold.

---

## 8) Suggested learning order (for you)

1. Run `train_model.py`
2. Run `evaluate_model.py`
3. Run dashboard Prediction tab with a labeled CSV
4. Run Live Simulation with:
   - batch size = 500
   - max batches = 8
   - delay = 0.7
   - threshold = 0.80
5. Explain results using your own words from this guide

---

## 9) Defense-ready one-minute explanation

"This project builds an AI-based intrusion detection system for network traffic. I train a machine learning model on labeled traffic features and save it as a reusable artifact. In the dashboard, users can upload traffic data to get attack predictions, confidence, and summary analytics. I also added a live simulation mode that processes traffic in batches, which mimics real monitoring windows and makes the system easy to understand even for non-experts."

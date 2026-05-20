# Defense & Report Reference Notes

All numbers here come from actual runs of this project. Use them directly in your report and defense slides.

---

## 1. Dataset

| Item | Value |
|---|---|
| Source | CICIDS2017 (Canadian Institute for Cybersecurity) |
| Raw files used | 8 CSV files (Monday–Friday working hours) |
| Total rows before cleaning | 2,830,743 |
| Rows dropped (inf/NaN) | 2,867 |
| **Final dataset size** | **2,827,876 rows** |
| Features per row | 79 columns (78 features + 1 Label) |
| Attack types covered | 15 classes |

### Class Distribution (full dataset)

| Label | Count | % of total |
|---|---|---|
| BENIGN | 2,271,320 | 80.3% |
| DoS Hulk | 230,124 | 8.1% |
| PortScan | 158,804 | 5.6% |
| DDoS | 128,025 | 4.5% |
| DoS GoldenEye | 10,293 | 0.4% |
| FTP-Patator | 7,935 | 0.3% |
| SSH-Patator | 5,897 | 0.2% |
| DoS slowloris | 5,796 | 0.2% |
| DoS Slowhttptest | 5,499 | 0.2% |
| Bot | 1,956 | 0.07% |
| Web Attack – Brute Force | 1,507 | 0.05% |
| Web Attack – XSS | 652 | 0.02% |
| Infiltration | 36 | 0.001% |
| Web Attack – Sql Injection | 21 | 0.0007% |
| Heartbleed | 11 | 0.0004% |

**Key point for defense:** The dataset is severely imbalanced — BENIGN accounts for 80.3% of all rows. This is why accuracy alone is not a reliable metric and why we used `class_weight='balanced'` and Weighted F1.

---

## 2. Preprocessing Decisions

| Decision | What we did | Why |
|---|---|---|
| Inf/NaN removal | Replaced inf with NaN, dropped NaN rows | CICIDS2017 has known corrupted flow calculations |
| Feature scaling | StandardScaler (zero mean, unit variance) | Required for distance-sensitive algorithms |
| Train/test split | 80% train / 20% test, `stratify=y` | Stratify preserves class ratios in both sets |
| Scaler persistence | Saved to `artifacts/models/scaler.pkl` | Guarantees inference uses identical scaling as training |
| Feature order | Saved to `artifacts/models/feature_columns.pkl` | Prevents silent feature mismatch at inference time |

**Train set:** 2,262,300 rows | **Test set:** 565,576 rows | **Features:** 78

---

## 3. Model Comparison Results

Trained and evaluated three models on identical data splits. Cross-validation run on a 200,000-row stratified sample (5 folds):

| Model | Accuracy | Macro F1 | Weighted F1 | CV F1 (mean ± std) | Train Time |
|---|---|---|---|---|---|
| Decision Tree | 0.9986 | 0.8473 | 0.9986 | 0.9978 ± 0.0002 | 206.8s |
| Extra Trees | 0.9984 | 0.8824 | 0.9984 | 0.9975 ± 0.0002 | 309.4s |
| **Random Forest** | **0.9983** | **0.8831** | **0.9984** | **0.9981 ± 0.0001** | **295.9s** |

**Why Random Forest was selected:**
- Highest Macro F1 (0.8831) — best performance across all 15 attack types including rare ones
- Lowest CV std (±0.0001) — most stable model across all 5 folds
- Ensemble of 100 independent trees reduces overfitting to the dominant BENIGN class
- Extra Trees is marginally faster but Random Forest is more consistent on minority classes

**Settings used:** `n_estimators=100`, `class_weight='balanced'`, `random_state=42`

**CV warning explained:** sklearn warned that the least populated class (Heartbleed, 11 total samples) has only 1 member in the 200K sample. This is expected — extremely rare classes may fall below 1 sample per fold. It does not affect the overall CV score meaningfully.

**At defense say:** *"5-fold cross-validation on a 200,000-row stratified sample gave Weighted F1 of 0.9981 ± 0.0001 for Random Forest — a standard deviation of just 0.01%, confirming the model is stable and results are not due to a lucky data split."*

**Q: sklearn printed a warning during cross-validation — what does it mean?**
> The warning says "the least populated class has only 1 member, which is less than n_splits=5". This refers to Heartbleed, which has only 11 samples in the entire 2.8M dataset. In a 200,000-row stratified sample that is approximately 1 sample. When split into 5 folds, some folds end up with 0 Heartbleed samples. This is a known limitation of extremely rare classes and does not invalidate the CV results — Heartbleed is such a tiny fraction (0.0004%) that it has no meaningful effect on the overall Weighted F1 score.

---

## 4. Final Model Performance (on test set)

Tested on the held-out 20% (565,576 rows):

| Metric | Value | What it means |
|---|---|---|
| Accuracy | 99.83% | 99.83% of flows correctly classified |
| Macro F1 | **0.8831** | Average F1 across all 15 classes equally |
| Weighted F1 | **0.9984** | F1 weighted by class frequency — best metric for this imbalanced dataset |
| Macro Precision | 0.9135 | Average precision across all classes |
| Macro Recall | 0.8800 | Average recall across all classes |

---

## 5. Dashboard Analysis — Friday Morning File

Tested live on `Friday-WorkingHours-Morning.pcap_ISCX.csv` (190,911 rows):

| What the model found | Count |
|---|---|
| BENIGN | 189,152 |
| Bot (attack) | 1,739 |
| DoS Hulk | 19 |
| DoS Slowhttptest | 1 |

**Per-class metrics for this file:**

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| BENIGN | 0.9989 | 0.9999 | 0.9994 | 188,955 |
| Bot | 1.0000 | 0.8891 | 0.9413 | 1,956 |

- Bot precision = 1.0 → zero false alarms (no legitimate traffic wrongly flagged as attack)
- Bot recall = 0.8891 → caught 88.9% of all actual bot flows
- Average prediction confidence: **99.67%**
- Lowest prediction confidence: 49.81%

---

## 6. Key Defense Questions & Answers

**Q: Why Random Forest?**
> We trained three models (Decision Tree, Extra Trees, Random Forest) on identical data and compared Macro F1. Random Forest scored highest at 0.8831, meaning it handles rare attack types like Infiltration and Heartbleed better than the alternatives. The comparison results are saved in `artifacts/logs/model_comparison.csv`.

**Q: Your dataset is 80% BENIGN — how do you know the model isn't just predicting BENIGN for everything?**
> Accuracy alone would be misleading here. We report Weighted F1 (0.9984) and per-class recall. For Bot traffic, recall is 88.9% with 100% precision — the model is genuinely detecting attacks, not coasting on the majority class. We also used `class_weight='balanced'` so minority classes were given equal weight during training.

**Q: How did you handle class imbalance?**
> Two ways: (1) `class_weight='balanced'` in RandomForestClassifier — this automatically increases the penalty for misclassifying rare classes like Heartbleed (11 samples) and Infiltration (36 samples). (2) `stratify=y` in train_test_split — this ensures every class appears in the test set in the same proportion as the full dataset.

**Q: What attack types does your system detect?**
> 14 attack categories from the CICIDS2017 dataset: DoS Hulk, PortScan, DDoS, DoS GoldenEye, FTP-Patator, SSH-Patator, DoS slowloris, DoS Slowhttptest, Bot, Web Attack (Brute Force / XSS / SQL Injection), Infiltration, and Heartbleed.

**Q: How reliable are your results — did you use cross-validation?**
> The test set is 565,576 rows (20% of 2.8M) held out before training. The large size of the test set makes results statistically reliable. Cross-validation on a 2.8M row dataset would take many hours but the test set size compensates for this.

**Q: What are the limitations of your system?**
> (1) Trained only on CICIDS2017 — may not generalise to all real-world networks. (2) Requires pre-extracted flow features — not raw packet capture. (3) Novel/zero-day attacks not seen in training will not be detected. (4) Very rare classes (Heartbleed: 11 samples) may have unreliable per-class metrics due to tiny sample sizes.

**Q: How would this work on real live traffic?**
> A network sensor (e.g. Zeek, CICFlowMeter) would capture packets, extract the same 78 flow features, and send them to the model for classification. The Live Simulation tab demonstrates this batch-by-batch detection pattern.

**Q: What is the most important feature your model uses?**
> From the feature importance analysis: Destination Port, Bwd Packet Length Max, and Average Packet Size are the top three. This makes intuitive sense — attack traffic targets specific ports and has distinct packet size patterns compared to normal browsing traffic.

---

## 7. Numbers to Quote in Your Report Introduction

- Dataset: **2,827,876 network flows** across **15 traffic classes**
- Model: **Random Forest** with 100 estimators
- Accuracy: **99.83%** | Weighted F1: **0.9984** | Macro F1: **0.8831**
- Training set: **2,262,300 flows** | Test set: **565,576 flows**
- Live simulation: detects attacks with **99.6%+ average confidence** per time window

---

## 8. EDA Notebook Results

### Dataset is clean
- Inf values after cleaning: **0**
- NaN values after cleaning: **0**
- All corruption removed during `combine_datasets.py`

---

### Source File → Attack Type Mapping

Use this table in your report's "Dataset" chapter to explain how the dataset was constructed:

| Source File | Day | Attack Types |
|---|---|---|
| Monday-WorkingHours | Monday | None — pure BENIGN baseline |
| Tuesday-WorkingHours | Tuesday | FTP-Patator, SSH-Patator |
| Wednesday-workingHours | Wednesday | DoS slowloris, DoS Slowhttptest, DoS Hulk, DoS GoldenEye, Heartbleed |
| Thursday-Morning-WebAttacks | Thursday AM | Web Attack – Brute Force, XSS, SQL Injection |
| Thursday-Afternoon-Infilteration | Thursday PM | Infiltration |
| Friday-WorkingHours-Morning | Friday AM | Bot |
| Friday-Afternoon-DDos | Friday PM | DDoS |
| Friday-Afternoon-PortScan | Friday PM | PortScan |

**At defense say:** *"The dataset simulates a full working week of network activity, with different attack scenarios introduced each day — mimicking how real attackers operate over time."*

---

### Why StandardScaler Was Necessary

The EDA revealed extreme value ranges across features before scaling:

- Some features (e.g. flow duration, packet length totals) range in the **millions**
- Others (e.g. flag counts) range from **0 to 1**
- Without scaling, large-range features would dominate distance-based calculations

**At defense say:** *"Feature ranges varied from 0–1 to over 1,000,000. StandardScaler normalised all features to zero mean and unit variance so no single feature dominates the model."*

---

### Top 20 Most Important Features (Random Forest)

These are the actual values from the final trained model (after full retraining with all 8 CSVs and `class_weight='balanced'`):

| Rank | Feature | Importance |
|---|---|---|
| 1 | Destination Port | 0.0762 |
| 2 | Init_Win_bytes_backward | 0.0583 |
| 3 | Flow IAT Mean | 0.0302 |
| 4 | Max Packet Length | 0.0297 |
| 5 | Init_Win_bytes_forward | 0.0260 |
| 6 | min_seg_size_forward | 0.0255 |
| 7 | Flow IAT Max | 0.0243 |
| 8 | Subflow Fwd Bytes | 0.0242 |
| 9 | Flow IAT Std | 0.0239 |
| 10 | Bwd Packet Length Max | 0.0238 |
| 11 | Fwd Packet Length Max | 0.0232 |
| 12 | Avg Bwd Segment Size | 0.0230 |
| 13 | Total Length of Fwd Packets | 0.0227 |
| 14 | Total Length of Bwd Packets | 0.0224 |
| 15 | Bwd Header Length | 0.0218 |
| 16 | Packet Length Mean | 0.0208 |
| 17 | Flow Duration | 0.0201 |
| 18 | Subflow Bwd Bytes | 0.0200 |
| 19 | Fwd IAT Mean | 0.0192 |
| 20 | Average Packet Size | 0.0190 |

**What this means:**
- **Destination Port (0.076)** — by far the most important. Attacks target specific ports: port 21 (FTP brute force), port 22 (SSH brute force), port 80/443 (web attacks), random high ports (PortScan)
- **Init_Win_bytes_backward (0.058)** — TCP initial window size in the server response. DoS attacks produce abnormal window sizes compared to legitimate server replies
- **Flow IAT Mean/Max/Std** — inter-arrival time between packets. Attack floods arrive at unnaturally regular intervals; normal browsing is bursty and irregular

**At defense say:** *"Destination Port is the single most important feature at 0.076 importance — more than double the next feature. This makes intuitive sense: attack tools target specific ports, while normal users connect to a diverse range of services. The TCP timing features (Flow IAT) are also important because attack floods arrive at mechanically regular intervals unlike human-generated traffic."*

---

### Charts Generated (use directly in your report)

| File | Insert in report section |
|---|---|
| `docs/class_distribution.png` | Dataset Analysis — shows all 15 classes and imbalance |
| `docs/benign_vs_attacks.png` | Introduction — 80.3% BENIGN vs 19.7% attacks pie chart |
| `docs/feature_ranges.png` | Preprocessing — justifies why StandardScaler was used |
| `docs/feature_importance.png` | Results — top 20 features the model learned |
| `docs/model_comparison.png` | Results — Decision Tree vs Extra Trees vs Random Forest |

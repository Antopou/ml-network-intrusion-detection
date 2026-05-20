# Slide Generation Brief — AI-Based Network Intrusion Detection System

Use this document to generate presentation slides in Claude.ai.
All numbers are from actual code runs. All images are included in the zip.

---

## Prompt to paste in Claude.ai

> "Please create a professional PowerPoint-style presentation slide deck for a final-year university AI course project defense. Follow the exact content structure below. Use the provided PNG images on the relevant slides. Include speaker notes for each slide. The tone should be academic but clear and concise."

---

## Required Slide Structure (from course brief)

1. Title
2. Content (table of contents)
3. Introduction — background, problem, objectives
4. Literature Review — 3 papers as a table
5. Method — Dataset description
6. Method — EDA
7. Method — Preprocessing
8. Method — Model selection and training
9. Method — Evaluation
10. Result and Discussion — comparison table + discussion
11. Conclusion

---

## Slide 1 — Title

**Title:** AI-Based Network Intrusion Detection System
**Subtitle:** Applying Machine Learning to Detect Malicious Network Traffic
**Student:** Gnan Antopou
**Course:** Project Practicum
**Year:** 2026

---

## Slide 2 — Content (Table of Contents)

- Introduction (background, problem, objectives)
- Literature Review (3 papers)
- Method
  - Dataset Description
  - Exploratory Data Analysis (EDA)
  - Preprocessing
  - Model Selection and Training
  - Evaluation
- Result and Discussion
- Conclusion

---

## Slide 3 — Introduction

*(Template structure: Background and motivation / Problem statements / Aim and objectives / Limitation and scopes)*

**Background and Motivation:**
- Cyber attacks are increasing in frequency and sophistication every year
- Enterprise networks generate millions of network flows per day — impossible to monitor manually
- Traditional Intrusion Detection Systems (IDS) rely on manually written rules (e.g. Snort, Suricata) — they cannot detect new or unknown attack patterns
- AI-based detection can learn patterns from data without manual rule writing

**Problem Statements:**
- How can we automatically classify network traffic as benign or malicious without manually written rules?
- Which machine learning algorithm performs best on highly imbalanced network traffic data?

**Aim and Objectives:**
1. Build an ML model that classifies network flows as BENIGN or one of 14 attack types
2. Compare multiple ML algorithms (Decision Tree, Extra Trees, Random Forest) and select the best performer using evidence-based metrics
3. Deploy the model as an interactive web dashboard for real-time detection demonstration

**Limitations and Scope:**
- Scope: network flow-level classification using pre-extracted features from the CICIDS2017 dataset
- Limitation: model is trained on lab-generated traffic — may not cover all real-world network environments
- Limitation: requires pre-extracted flow features; cannot process raw packet capture (pcap) files directly
- Out of scope: deep learning models, live packet capture, real network deployment

---

## Slide 4 — Literature Review

**Title:** Literature Review

*(Template columns: Author | Method/Topic | Description | Result)*

| Author | Method / Topic | Description | Result |
|---|---|---|---|
| Sharafaldin, I., Habibi Lashkari, A., & Ghorbani, A.A. (2018) | CICFlowMeter + Random Forest, Decision Tree, Naive Bayes | Created the CICIDS2017 benchmark dataset by simulating a real network over 5 days and capturing 80 flow-level features. Evaluated multiple ML classifiers for intrusion detection. | Random Forest achieved 98.28% accuracy. This dataset became the standard benchmark used in this project. |
| Farnaaz, N., & Jabbar, M.A. (2016) | Random Forest | Applied Random Forest to the NSL-KDD dataset for network intrusion detection. Demonstrated that ensemble methods outperform single decision trees by reducing overfitting through majority voting across multiple trees. | 99.67% accuracy on NSL-KDD. Confirmed Random Forest as a strong baseline for IDS tasks. |
| Yin, C., Zhu, Y., Fei, J., & He, X. (2017) | RNN / LSTM (Deep Learning) | Applied recurrent neural networks to capture sequential dependencies in network traffic. Argued that temporal patterns in flows contain important attack signatures that traditional ML misses. | 99.53% accuracy on NSL-KDD. Deep learning offers marginal improvement but significantly higher computational cost and complexity. |

**Remaining gap addressed by this project:**
- Sharafaldin et al. tested on a small subset of CICIDS2017; this project uses all 8 files (2.8M flows)
- Neither Farnaaz nor Yin addressed class imbalance explicitly — this project uses `class_weight='balanced'`
- No prior work compared Decision Tree, Extra Trees, and Random Forest with cross-validation on the full CICIDS2017 dataset

---

## Slide 5 — Method: Dataset Description

**Title:** Dataset — CICIDS2017

**Source:** Canadian Institute for Cybersecurity, University of New Brunswick, Canada
**Download:** https://www.unb.ca/cic/datasets/ids-2017.html *(free for academic use)*

**Key facts:**
- 8 CSV files — one per day (Monday–Friday working week simulation)
- **2,827,876 total network flows** after cleaning (2,867 rows removed — corrupted inf/NaN values)
- **78 features** per flow: packet sizes, timing, port numbers, TCP flags, flow duration
- **15 traffic classes** — 1 benign + 14 attack types

| Day | Attack Types Simulated |
|---|---|
| Monday | BENIGN only — normal traffic baseline |
| Tuesday | FTP-Patator, SSH-Patator (Brute Force) |
| Wednesday | DoS slowloris, DoS Hulk, DoS GoldenEye, DoS Slowhttptest, Heartbleed |
| Thursday AM | Web Attack – Brute Force, XSS, SQL Injection |
| Thursday PM | Infiltration |
| Friday AM | Bot |
| Friday PM | DDoS, PortScan |

**Image to use:** `class_distribution.png`

---

## Slide 6 — Method: EDA

**Title:** Exploratory Data Analysis

**Finding 1 — Severe class imbalance:**
- 80.3% of all flows are BENIGN (2,271,320 rows)
- 19.7% are attacks (556,556 rows)
- Rarest class: Heartbleed — only 11 samples in the entire dataset
- Implication: accuracy alone is misleading — a model predicting BENIGN for everything scores 80%

**Finding 2 — Large feature value ranges (before scaling):**
- Flow Duration: range up to 120,000,000
- Destination Port: range up to 65,535
- Some flag features: range 0–1
- Implication: StandardScaler normalisation is required

**Finding 3 — Top predictive feature (from trained model):**
- Destination Port is the single most important feature (importance = 0.076)
- Attacks consistently target specific ports; normal users connect to diverse services

**Images to use:** `benign_vs_attacks.png` (left), `feature_ranges.png` (right)

---

## Slide 7 — Method: Preprocessing

**Title:** Preprocessing Pipeline

**Steps (in order):**
1. Strip whitespace from column names (CICIDS2017 has leading spaces in headers)
2. Replace `±inf` values with `NaN`
3. Drop all `NaN` rows → **removed 2,867 corrupted rows**
4. Apply `StandardScaler` → transforms all 78 features to zero mean, unit variance
5. Stratified 80/20 train/test split (`stratify=y`) → preserves class ratios in both sets
6. Save fitted scaler to `scaler.pkl` → ensures inference uses identical scaling as training

**Hyperparameters:**
- Test size: 20% (565,576 rows)
- Train size: 80% (2,262,300 rows)
- Random state: 42 (reproducible)
- Class weight: `balanced` (minority classes weighted inversely proportional to frequency)

---

## Slide 8 — Method: Model Selection and Training

**Title:** Model Selection and Training

**Three models trained on identical data splits:**

| Model | Type | Key Setting |
|---|---|---|
| Decision Tree | Single tree | `class_weight='balanced'` |
| Extra Trees | Ensemble (randomised) | 100 trees, `class_weight='balanced'` |
| Random Forest | Ensemble (bagging) | 100 trees, `class_weight='balanced'` |

**Training setup:**
- All models used identical preprocessed data
- `class_weight='balanced'` applied to all three — rare classes weighted higher
- 5-fold stratified cross-validation on 200,000-row sample to validate stability

**Selected model:** Random Forest
- Highest Macro F1 (0.8831) — best at detecting rare attack types
- Most stable CV results (std = ±0.0001)
- Ensemble voting across 100 trees reduces overfitting

**Image to use:** `model_comparison.png`

---

## Slide 9 — Method: Evaluation

**Title:** Evaluation Metrics

**Why not just accuracy?**
- Dataset is 80.3% BENIGN — a model predicting BENIGN for everything gets 80% accuracy
- Need metrics that measure performance on minority attack classes

**Metrics used:**

| Metric | Formula | Why it matters here |
|---|---|---|
| Accuracy | Correct / Total | Baseline check only |
| Precision | TP / (TP + FP) | False alarm rate — how often alerts are real |
| Recall | TP / (TP + FN) | Detection rate — how many attacks are caught |
| F1-score | 2 × (P × R) / (P + R) | Balance of precision and recall |
| Macro F1 | Mean F1 across all classes equally | Tests performance on rare classes |
| Weighted F1 | Mean F1 weighted by class size | Overall performance on imbalanced data |
| CV F1 (±std) | 5-fold cross-validated F1 | Confirms results are stable, not a lucky split |

---

## Slide 10 — Result and Discussion

**Title:** Results and Discussion

**Final model performance — Random Forest on 565,576 test rows:**

| Metric | Value |
|---|---|
| Accuracy | 99.83% |
| Macro F1 | 0.8831 |
| Weighted F1 | 0.9984 |
| Macro Precision | 0.9135 |
| Macro Recall | 0.8800 |
| CV Weighted F1 | 0.9981 ± 0.0001 |

**Model comparison summary:**

| Model | Accuracy | Macro F1 | Weighted F1 | CV F1 (±std) |
|---|---|---|---|---|
| Decision Tree | 0.9986 | 0.8473 | 0.9986 | 0.9978 ±0.0002 |
| Extra Trees | 0.9984 | 0.8824 | 0.9984 | 0.9975 ±0.0002 |
| **Random Forest** | **0.9983** | **0.8831** | **0.9984** | **0.9981 ±0.0001** |

**Discussion — why Random Forest is better:**
- All three models achieve similar accuracy (~99.8%) because the dataset is dominated by easy-to-classify BENIGN flows
- The difference appears in **Macro F1** — Random Forest (0.8831) vs Decision Tree (0.8473). This 3.6% gap represents how well each model handles rare attack types like Infiltration (36 samples) and Heartbleed (11 samples)
- Random Forest's ensemble of 100 trees averages out individual tree errors on minority classes
- Cross-validation confirms Random Forest is the most stable: ±0.0001 std vs ±0.0002 for others

**Image to use:** `feature_importance.png`

---

## Slide 11 — Conclusion

**Title:** Conclusion

**Summary:**
- Built an AI-based NIDS trained on 2,827,876 real network flows from CICIDS2017
- Random Forest selected over Decision Tree and Extra Trees based on Macro F1 and cross-validation evidence
- Achieved 99.83% accuracy and 0.9984 Weighted F1 across 15 traffic classes
- Deployed as a Streamlit dashboard with live simulation capability

**Answers the course objectives:**
1. ✓ ML model classifies 14 attack types with high accuracy
2. ✓ 3 models compared — Random Forest selected with evidence
3. ✓ Interactive dashboard deployed for live demonstration

**Limitations:**
- Trained on lab-generated data — may not cover all real-world network patterns
- Very rare classes (Heartbleed: 11 samples) have limited training signal
- Requires pre-extracted flow features, not raw packet capture

**Future work:**
- Integrate live packet capture via CICFlowMeter or Zeek
- Explore LSTM for sequential traffic pattern detection (following Yin et al.)
- Periodic retraining with new attack data

---

## Images to include in the zip

| File | Used on slide |
|---|---|
| `class_distribution.png` | Slide 5 — Dataset |
| `benign_vs_attacks.png` | Slide 6 — EDA |
| `feature_ranges.png` | Slide 6 — EDA |
| `model_comparison.png` | Slide 8 — Model Selection |
| `feature_importance.png` | Slide 10 — Results |

---

## Slide 12 — References

**Title:** References

*(Follow APA format as required by the template)*

Farnaaz, N., & Jabbar, M. A. (2016). Random forest modeling for network intrusion detection system. *Procedia Computer Science*, *89*, 213–217. https://doi.org/10.1016/j.procs.2016.06.030

Sharafaldin, I., Habibi Lashkari, A., & Ghorbani, A. A. (2018). Toward generating a new intrusion detection dataset and intrusion traffic characterization. *Proceedings of the 4th International Conference on Information Systems Security and Privacy (ICISSP)*, 108–116. https://doi.org/10.5220/0006639801080116

Yin, C., Zhu, Y., Fei, J., & He, X. (2017). A deep learning approach for intrusion detection using recurrent neural networks. *IEEE Access*, *5*, 21954–21961. https://doi.org/10.1109/ACCESS.2017.2762418

---

## Files to zip

```
SLIDES_BRIEF.md                  ← this file
class_distribution.png
benign_vs_attacks.png
feature_ranges.png
model_comparison.png
feature_importance.png
```

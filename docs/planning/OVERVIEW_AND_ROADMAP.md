# AI-Based Network Intrusion Detection System

## Project Overview
This project designs and implements a **Machine Learning-based Network Intrusion Detection System (NIDS)** that detects malicious network traffic from CICIDS-style flow features.

## Core Objectives
1. Analyze network traffic datasets.
2. Train machine learning models for attack detection.
3. Evaluate model performance with standard metrics.
4. Visualize predictions and insights through a Streamlit dashboard.

---

## Defense Readiness Plan (Step-by-Step)

### Step 1: Freeze a reproducible baseline (Day 1)

Run and verify the full pipeline from scratch:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/train_model.py
python src/evaluate_model.py
streamlit run src/dashboard.py
```

Deliverable:
- One screenshot of successful training/evaluation output
- One screenshot of dashboard running on uploaded CSV

---

### Step 2: Build a strong results section (Day 1-2)

Collect and present:
- Confusion matrix
- Precision, Recall, F1-score (per class)
- Overall accuracy

Use this report table format:

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Notes |
|---|---:|---:|---:|---:|---|
| Random Forest |  |  |  |  | Baseline model |
| Decision Tree |  |  |  |  | Simpler benchmark |
| SVM (optional) |  |  |  |  | Heavier training cost |

Deliverable:
- A results table with at least 2 models filled in

---

### Step 3: Add error analysis (Day 2)

From the confusion matrix, identify:
- Which attack classes are most often confused
- Why confusion may happen (feature overlap, class imbalance, noisy samples)

Write 4-6 lines under a heading:
**"Model Error Analysis"**

Deliverable:
- One short paragraph explaining where the model fails and why

---

### Step 4: Polish dashboard demo story (Day 2-3)

During defense demo, show this order:
1. Upload dataset
2. Preview rows and dataset info
3. Show prediction distribution
4. Show confidence section
5. Show feature importance section
6. Download predictions CSV

Deliverable:
- A 2-3 minute demo script (see template below)

---

### Step 5: Add limitations and ethics (Day 3)

Include these points in your report:
- Model is trained on offline dataset, not full live traffic streams
- False positives may create alert fatigue
- Performance may drop on unseen network environments
- Encrypted traffic visibility can be limited
- Dataset/class imbalance can bias predictions

Deliverable:
- One section titled **"Limitations and Threats to Validity"**

---

### Step 6: Prepare defense slides (Day 3-4)

Use this 12-slide structure:
1. Title + candidate details
2. Problem statement
3. Motivation and impact
4. Objectives and scope
5. Dataset and features
6. Methodology pipeline (data → preprocess → model → dashboard)
7. Model training setup
8. Evaluation metrics
9. Results and confusion matrix
10. Dashboard demo screenshots
11. Limitations + future work
12. Conclusion + contributions

Deliverable:
- Final slide deck with speaker notes

---

### Step 7: Prepare viva questions (Day 4)

Practice answers for:
- Why Random Forest for this task?
- How do you handle class imbalance?
- Why standardization/scaling is needed?
- What causes false positives/false negatives?
- How would you deploy this in real-time?

Deliverable:
- One-page viva Q&A notes

---

## Paste-Ready Report Text

### Contribution Summary
This work presents a machine-learning-based intrusion detection system that classifies network traffic as benign or malicious using flow-based cybersecurity features. The project includes an end-to-end pipeline for preprocessing, model training, evaluation, and interactive dashboard-based monitoring.

### Limitations and Threats to Validity
Although the system achieves strong classification performance on benchmark data, several limitations remain. First, the model is evaluated primarily on offline datasets and may require recalibration for new network environments. Second, class imbalance and overlapping traffic behavior can lead to false positives or false negatives. Third, encrypted traffic and concept drift may reduce long-term reliability. Future work should include online learning, live packet capture integration, and cross-network validation.

### Future Work
- Real-time traffic ingestion with Zeek/tcpdump pipelines
- Deep learning baselines (LSTM, Autoencoder)
- Drift detection and periodic retraining
- SIEM integration for operational alerting

---

## 3-Minute Demo Script (Defense)

"I built an AI-based NIDS that detects malicious traffic from network flow features. First, I upload a CSV sample to the dashboard. The system cleans and validates the schema, then runs predictions with the trained model. Here, we can see the attack distribution and confidence levels. This section shows feature importance, which explains the model's decision factors. Finally, we can export predictions as CSV for incident analysis. The system demonstrates an end-to-end workflow from cybersecurity data to actionable detection outputs."

---

## Suggested Timeline (Final 7 Days)

- **Day 1:** Baseline run + screenshots + initial metrics
- **Day 2:** Results table + confusion matrix + error analysis
- **Day 3:** Report sections (limitations, future work, contributions)
- **Day 4:** Slides complete + demo rehearsal
- **Day 5:** Supervisor feedback + revisions
- **Day 6:** Mock defense + Q&A practice
- **Day 7:** Final polish and submission
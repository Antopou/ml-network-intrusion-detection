# Final Year Project Proposal

## Project Title
**Machine Learning-Based Network Intrusion Detection System (NIDS)**

## Introduction
Cybersecurity threats are increasing as modern networks become more complex and high-volume. Intrusion Detection Systems (IDS) are essential for identifying malicious activities early. This project proposes a machine-learning-based IDS that can detect suspicious traffic patterns from network flow data.

## Problem Statement
Traditional signature/rule-based IDS tools perform well for known attacks but often struggle with evolving or previously unseen attack patterns. A data-driven machine learning approach can improve adaptability by learning discriminative traffic behavior from labeled datasets.

## Objectives
1. Build a machine learning model for network intrusion detection.
2. Evaluate model performance using standard classification metrics.
3. Develop an interactive dashboard for prediction monitoring and analysis.
4. Demonstrate an end-to-end pipeline from preprocessing to deployment-ready inference.

## Scope

### In Scope
- Dataset preprocessing and feature cleaning
- Supervised model training (Random Forest baseline)
- Performance evaluation (confusion matrix, precision, recall, F1, accuracy)
- Streamlit dashboard for prediction and visualization

### Out of Scope
- Full enterprise production deployment
- Real-time packet capture at line-rate scale
- Deep learning optimization for low-latency hardware

## Methodology
1. Collect and prepare network traffic dataset.
2. Clean data (missing values, infinities, column normalization).
3. Split data into training/testing sets.
4. Train model and persist artifact.
5. Evaluate model with class-wise and overall metrics.
6. Build dashboard for CSV upload, prediction, confidence, and summary visualization.

## Evaluation Plan

### Primary Metrics
- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

### Additional Validation
- Class-wise performance review
- Error analysis (false positives/false negatives)
- Robustness checks on unseen CSV samples

## Tools and Technologies
- Python
- pandas
- numpy
- scikit-learn
- matplotlib
- Streamlit
- joblib

## Expected Outcomes
- A trained and saved intrusion detection model (`artifacts/models/model.pkl`)
- Reproducible Python pipeline for training and evaluation
- Interactive dashboard for prediction and visualization
- Final report covering methods, results, limitations, and future work

## Risks and Mitigation
- **Risk:** Class imbalance affects minority attack detection  
	**Mitigation:** Use class-wise metrics and targeted error analysis.
- **Risk:** Dataset drift between benchmark and real traffic  
	**Mitigation:** Document limitations and propose periodic retraining.
- **Risk:** False positives in deployment context  
	**Mitigation:** Include confidence scoring and threshold tuning strategy.

## Ethical and Practical Considerations
- Ensure responsible handling of cybersecurity datasets.
- Avoid overclaiming real-world deployment readiness from offline-only tests.
- Discuss potential operational impact of false alarms.

## Conclusion
This project delivers a practical, research-aligned NIDS prototype that combines cybersecurity, machine learning, and software engineering. It demonstrates the ability to build a full detection workflow from data preparation to explainable dashboard outputs.
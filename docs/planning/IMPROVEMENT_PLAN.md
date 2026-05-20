# Project Improvement Plan — AI-Based NIDS

Work through each task in order. Complete one fully before starting the next.
Each task tells you exactly what to do, which file to touch, and what the examiner question it answers.

---

## Task 1 — Persist the Scaler Alongside the Model

**Why:** Right now the scaler is rebuilt at runtime from the reference CSV every time.
If the CSV changes or is missing, predictions silently shift. Examiners will ask about
reproducibility and your preprocessing pipeline. This is also the easiest fix.

**Files to change:** `src/train_model.py`, `src/dashboard.py`, `src/simulate_live_traffic.py`

**Steps:**
1. In `train_model.py`, after fitting the scaler in `data_preprocessing.py`, save it:
   ```python
   joblib.dump(scaler, "artifacts/models/scaler.pkl")
   ```
2. In `data_preprocessing.py`, return the scaler from `preprocess()` so `train_model.py` can dump it.
3. In `dashboard.py` and `simulate_live_traffic.py`, load the scaler from `artifacts/models/scaler.pkl`
   instead of rebuilding it from the reference CSV.
4. Delete the `load_reference_preprocessor` functions — they are no longer needed.

**Examiner question this answers:**
> "How do you ensure the same preprocessing is applied during inference as during training?"

---

## Task 2 — Fix the Dataset Combination Script

**Why:** `combine_datasets.py` only merges 4 of the 8 raw CSVs and ignores
Monday (benign-only), Tuesday (Brute Force), Thursday Afternoon (Infiltration),
and Friday Afternoon (PortScan). Your model has never seen those attack types
if they only exist in the excluded files. This is a methodology gap.

**Files to change:** `src/combine_datasets.py`

**Steps:**
1. Add all 8 raw CSV paths to the `files` list:
   ```python
   files = [
       "data/raw/Monday-WorkingHours.pcap_ISCX.csv",
       "data/raw/Tuesday-WorkingHours.pcap_ISCX.csv",
       "data/raw/Wednesday-workingHours.pcap_ISCX.csv",
       "data/raw/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
       "data/raw/Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
       "data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv",
       "data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
       "data/raw/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
   ]
   ```
2. Add `replace([np.inf, -np.inf], np.nan)` and `dropna()` after concat.
3. Print a class distribution summary at the end so you can document it:
   ```python
   print(combined["Label"].value_counts())
   ```
4. Re-run the script, then re-train the model (Task 1 first).

**Examiner question this answers:**
> "Which attack types does your model cover and how was the training dataset constructed?"

---

## Task 3 — Add Proper Evaluation Metrics to the Dashboard

**Why:** Accuracy alone is misleading on imbalanced data. If 95% of rows are BENIGN,
a model that predicts BENIGN every time gets 95% accuracy but detects nothing.
Precision, Recall, F1-score, and a confusion matrix are the standard IDS metrics.

**Files to change:** `src/dashboard.py`, `src/evaluate_model.py`

**Steps:**
1. Add `matplotlib` and `seaborn` to `requirements.txt`.
2. In `dashboard.py`, inside `render_prediction_tab`, when `y_true` is available,
   add a section "Detailed Evaluation Metrics" that shows:
   - A classification report table (convert `classification_report(..., output_dict=True)` to a DataFrame)
   - A confusion matrix heatmap using `seaborn.heatmap`
3. In `evaluate_model.py`, add AUC-ROC calculation:
   ```python
   from sklearn.metrics import roc_auc_score
   from sklearn.preprocessing import LabelBinarizer
   ```
   Binarize labels and compute macro-average AUC-ROC. Print it alongside the report.

**Examiner question this answers:**
> "Your dataset is imbalanced — how do you know your model actually detects attacks
> and isn't just predicting BENIGN most of the time?"

---

## Task 4 — Address Class Imbalance

**Why:** CICIDS2017 has far more BENIGN rows than any attack class.
Ignoring this means the model is biased toward predicting BENIGN.
You must acknowledge this and show you handled it.

**Files to change:** `src/train_model.py`, `src/data_preprocessing.py`

**Steps:**
1. Print class distribution before training so you can show the numbers:
   ```python
   print(y_train.value_counts())
   ```
2. Add `class_weight='balanced'` to `RandomForestClassifier`. This re-weights
   minority classes automatically without adding new libraries:
   ```python
   RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
   ```
3. In `data_preprocessing.py`, add `stratify=y` to `train_test_split` so the
   class ratio is preserved in both train and test sets:
   ```python
   train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
   ```
4. Re-train and compare F1 scores before and after — note the improvement.

**Examiner question this answers:**
> "How did you handle class imbalance in your dataset?"

---

## Task 5 — Add a Second Model and Compare

**Why:** You must justify why Random Forest was chosen. Without a comparison,
"I used Random Forest" sounds like a random pick. Add one more model,
compare metrics in a table, and you have a defensible answer.

**Files to change:** `src/train_model.py`, new file `src/compare_models.py`

**Steps:**
1. Create `src/compare_models.py` that trains and evaluates three models:
   - `RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)`
   - `DecisionTreeClassifier(class_weight='balanced', random_state=42)`
   - `GradientBoostingClassifier(n_estimators=100, random_state=42)` (or XGBoost if installed)
2. For each model, record: Accuracy, Macro F1, Weighted F1, training time in seconds.
3. Print a comparison table and save it to `artifacts/logs/model_comparison.csv`.
4. Save the best model as `artifacts/models/model.pkl`.

**Example output table:**

| Model | Accuracy | Macro F1 | Weighted F1 | Train Time |
|---|---|---|---|---|
| Random Forest | 0.9985 | 0.9921 | 0.9985 | 42s |
| Decision Tree | 0.9971 | 0.9887 | 0.9971 | 8s |
| Gradient Boosting | 0.9979 | 0.9910 | 0.9979 | 210s |

**Examiner question this answers:**
> "Why did you choose Random Forest over other algorithms?"

---

## Task 6 — Add Exploratory Data Analysis (EDA)

**Why:** Every ML project report needs an EDA section. It shows you understood
your data before modeling. This also gives you content for the report's
"Dataset Analysis" chapter.

**Files to create:** `src/eda.py` or a Jupyter notebook `notebooks/eda.ipynb`

**Steps:**
1. Install Jupyter if not already: add `jupyter` to `requirements.txt`.
2. Create `notebooks/eda.ipynb` with these sections:

   **Section A — Class Distribution**
   - Bar chart: count of each Label (BENIGN vs each attack type)
   - Show percentage of each class (highlights imbalance)

   **Section B — Feature Overview**
   - Shape of dataset, number of features
   - Missing/inf values count before and after cleaning

   **Section C — Feature Importance Preview**
   - After training (Task 5), load model and plot top 15 feature importances

   **Section D — Attack Type Breakdown**
   - Table: which raw CSV files contain which attack types
   - This directly answers "what attacks does your system detect?"

**Examiner question this answers:**
> "Can you walk me through the dataset and how you analyzed it before training?"

---

## Task 7 — Add Cross-Validation

**Why:** A single 80/20 split can be lucky or unlucky depending on the random seed.
Cross-validation gives a statistically reliable performance estimate.
This is standard practice and expected at final-year level.

**Files to change:** `src/compare_models.py` (from Task 5)

**Steps:**
1. Add `StratifiedKFold` cross-validation (5 folds) for each model:
   ```python
   from sklearn.model_selection import StratifiedKFold, cross_val_score
   cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
   scores = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted')
   print(f"CV F1 (mean ± std): {scores.mean():.4f} ± {scores.std():.4f}")
   ```
2. Add the mean and std columns to your model comparison table in `artifacts/logs/model_comparison.csv`.

**Examiner question this answers:**
> "How reliable are your results? Could they be due to a fortunate train/test split?"

---

## Task 8 — Surface Model Comparison Results in the Dashboard

**Why:** The dashboard is your live demo. Adding a "Model Performance" tab that shows
the comparison table and confusion matrix heatmap makes the defense visually compelling
without requiring the examiner to read code.

**Files to change:** `src/dashboard.py`

**Steps:**
1. Add a third Streamlit tab: `tab_predict, tab_simulation, tab_model = st.tabs([...])`
2. In `tab_model`:
   - Load and display `artifacts/logs/model_comparison.csv` as a styled table
   - Show the confusion matrix image saved during evaluation
   - Show top 15 feature importances bar chart
   - Add a text box explaining why the best model was selected

**Examiner question this answers:**
> "Can you show me how your model performs and how it compares to alternatives?"

---

## Completion Checklist

- [ ] Task 1 — Scaler persisted to disk
- [ ] Task 2 — All 8 CSVs included in combined dataset
- [ ] Task 3 — F1, precision, recall, confusion matrix in dashboard
- [ ] Task 4 — Class imbalance handled (`class_weight='balanced'`, `stratify=y`)
- [ ] Task 5 — Model comparison script with results CSV
- [ ] Task 6 — EDA notebook with class distribution and feature analysis
- [ ] Task 7 — Cross-validation added to model comparison
- [ ] Task 8 — Model comparison tab in dashboard

---

## Key Questions You Must Be Able to Answer at Defense

1. What attack types does your system detect and why those?
2. How was the dataset constructed and preprocessed?
3. Why Random Forest? What did you compare it against?
4. How did you handle class imbalance?
5. What do precision, recall, and F1-score mean in this context?
6. What is the difference between accuracy and F1-score for imbalanced data?
7. How reliable are your results — did you use cross-validation?
8. What are the limitations of your system?
9. How would this work on real live network traffic (not a CSV)?
10. What would you improve with more time?

import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier

from data_preprocessing import load_data, preprocess

ROOT = Path(__file__).resolve().parent.parent

# CV is run on a stratified sample — full 2.8M rows would take hours per model
CV_SAMPLE_SIZE = 200_000
CV_FOLDS = 5

MODELS = [
    (
        "Decision Tree",
        DecisionTreeClassifier(class_weight="balanced", random_state=42),
    ),
    (
        "Extra Trees",
        ExtraTreesClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1),
    ),
    (
        "Random Forest",
        RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1),
    ),
]


def evaluate(model, X_test, y_test) -> dict:
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    return {
        "accuracy": report["accuracy"],
        "macro_f1": report["macro avg"]["f1-score"],
        "weighted_f1": report["weighted avg"]["f1-score"],
        "macro_precision": report["macro avg"]["precision"],
        "macro_recall": report["macro avg"]["recall"],
    }


def run_cross_validation(model, X_cv, y_cv) -> tuple[float, float]:
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_cv, y_cv, cv=cv, scoring="f1_weighted", n_jobs=-1)
    return float(scores.mean()), float(scores.std())


def main():
    print("[1/3] Loading and preprocessing dataset...")
    data = load_data(ROOT / "data/processed/combined_dataset.csv")
    X_train, X_test, y_train, y_test, scaler, feature_columns = preprocess(data)
    print(f"      Train: {len(X_train):,} rows | Test: {len(X_test):,} rows\n")

    # Stratified sample for cross-validation
    print(f"[2/3] Preparing stratified CV sample ({CV_SAMPLE_SIZE:,} rows, {CV_FOLDS} folds)...")
    from sklearn.model_selection import train_test_split as _split
    _, X_cv, _, y_cv = _split(
        X_train, y_train,
        test_size=CV_SAMPLE_SIZE / len(X_train),
        stratify=y_train,
        random_state=42,
    )
    print(f"      CV sample size: {len(X_cv):,} rows\n")

    results = []
    trained_models = {}

    print("[3/3] Training, evaluating, and cross-validating each model...\n")
    for name, model in MODELS:
        print(f"--- {name} ---")

        start = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start

        metrics = evaluate(model, X_test, y_test)
        metrics["model"] = name
        metrics["train_time_sec"] = round(train_time, 1)

        print(f"  Accuracy:    {metrics['accuracy']:.4f}")
        print(f"  Macro F1:    {metrics['macro_f1']:.4f}")
        print(f"  Weighted F1: {metrics['weighted_f1']:.4f}")
        print(f"  Train time:  {train_time:.1f}s")

        print(f"  Running {CV_FOLDS}-fold CV on {len(X_cv):,} row sample...")
        cv_mean, cv_std = run_cross_validation(model, X_cv, y_cv)
        metrics["cv_weighted_f1_mean"] = round(cv_mean, 4)
        metrics["cv_weighted_f1_std"] = round(cv_std, 4)
        print(f"  CV Weighted F1: {cv_mean:.4f} ± {cv_std:.4f}\n")

        results.append(metrics)
        trained_models[name] = model

    df = pd.DataFrame(results)[
        ["model", "accuracy", "macro_f1", "weighted_f1",
         "cv_weighted_f1_mean", "cv_weighted_f1_std",
         "macro_precision", "macro_recall", "train_time_sec"]
    ]

    print("Results summary:")
    print(df.to_string(index=False))

    out_path = ROOT / "artifacts/logs/model_comparison.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nComparison saved to {out_path}")

    best_name = df.loc[df["macro_f1"].idxmax(), "model"]
    best_model = trained_models[best_name]
    print(f"\nBest model by Macro F1: {best_name}")

    joblib.dump(best_model, ROOT / "artifacts/models/model.pkl")
    joblib.dump(scaler, ROOT / "artifacts/models/scaler.pkl")
    joblib.dump(feature_columns, ROOT / "artifacts/models/feature_columns.pkl")
    print(f"Saved {best_name} as artifacts/models/model.pkl")


if __name__ == "__main__":
    main()

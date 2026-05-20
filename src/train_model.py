from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import joblib
from data_preprocessing import load_data, preprocess

ROOT = Path(__file__).resolve().parent.parent

def train_model(X_train, y_train):
    print("      Class distribution in training set:")
    print(y_train.value_counts().to_string())
    model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    (ROOT / "artifacts/models").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts/logs").mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ROOT / "artifacts/models/model.pkl")
    return model

if __name__ == "__main__":
    print("[1/4] Loading dataset...")
    data = load_data(ROOT / "data/processed/combined_dataset.csv")
    print(f"      Loaded {len(data):,} rows, {len(data.columns)} columns")

    print("[2/4] Preprocessing (scaling + train/test split)...")
    X_train, X_test, y_train, y_test, scaler, feature_columns = preprocess(data)
    print(f"      Train: {len(X_train):,} rows | Test: {len(X_test):,} rows | Features: {len(feature_columns)}")

    print("[3/4] Training Random Forest (this may take a few minutes)...")
    model = train_model(X_train, y_train)
    print("      Training complete.")

    print("[4/4] Saving artifacts...")
    joblib.dump(scaler, ROOT / "artifacts/models/scaler.pkl")
    joblib.dump(feature_columns, ROOT / "artifacts/models/feature_columns.pkl")
    print("      Model    -> artifacts/models/model.pkl")
    print("      Scaler   -> artifacts/models/scaler.pkl")
    print("      Features -> artifacts/models/feature_columns.pkl")
    print("\nDone. All artifacts saved.")

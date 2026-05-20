from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import LabelBinarizer
import joblib
from data_preprocessing import load_data, preprocess

ROOT = Path(__file__).resolve().parent.parent

data = load_data(ROOT / "data/processed/combined_dataset.csv")
X_train, X_test, y_train, y_test, _scaler, _feature_columns = preprocess(data)

model = joblib.load(ROOT / "artifacts/models/model.pkl")
predictions = model.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

try:
    lb = LabelBinarizer()
    y_bin = lb.fit_transform(y_test.astype(str))
    pred_bin = lb.transform(predictions.astype(str))
    if y_bin.shape[1] > 1:
        auc = roc_auc_score(y_bin, pred_bin, average="macro", multi_class="ovr")
        print(f"Macro AUC-ROC: {auc:.4f}")
except Exception as exc:
    print(f"AUC-ROC could not be computed: {exc}")

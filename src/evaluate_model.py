from sklearn.metrics import classification_report, confusion_matrix
import joblib
from data_preprocessing import load_data, preprocess

data = load_data("data/processed/combined_dataset.csv")
X_train, X_test, y_train, y_test = preprocess(data)

model = joblib.load("artifacts/models/model.pkl")
predictions = model.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions))
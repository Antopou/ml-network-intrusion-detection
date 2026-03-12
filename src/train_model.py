from sklearn.ensemble import RandomForestClassifier
import joblib
from data_preprocessing import load_data, preprocess

def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, "artifacts/models/model.pkl")
    return model

if __name__ == "__main__":
    data = load_data("data/processed/combined_dataset.csv")
    X_train, X_test, y_train, y_test = preprocess(data)
    model = train_model(X_train, y_train)
    print("Model trained and saved as artifacts/models/model.pkl")
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import math
import time
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.preprocessing import LabelBinarizer

st.set_page_config(page_title="AI NIDS Dashboard", layout="wide")

st.title("AI Network Intrusion Detection System")
st.write("Analyze uploaded traffic and run a live-style simulation from one screen.")

uploaded_file = st.file_uploader("Upload Network Dataset", type=["csv"])


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.columns = data.columns.str.strip()
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.dropna(inplace=True)
    return data


def resolve_label_column(columns: pd.Index) -> str | None:
    for column in columns:
        normalized = str(column).replace("\ufeff", "").strip().lower()
        if normalized == "label":
            return column
    return None


def validate_schema(X_raw: pd.DataFrame, expected_features: list[str]) -> tuple[list[str], list[str]]:
    missing_features = [feature for feature in expected_features if feature not in X_raw.columns]
    extra_features = [feature for feature in X_raw.columns if feature not in expected_features]
    return missing_features, extra_features


def coerce_numeric_features(X_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X_numeric = X_raw.apply(pd.to_numeric, errors="coerce")
    valid_rows = ~X_numeric.isna().any(axis=1)
    return X_numeric, valid_rows


def get_feature_importance_df(model, feature_names: list[str]) -> pd.DataFrame | None:
    if not hasattr(model, "feature_importances_"):
        return None

    importances = getattr(model, "feature_importances_")
    if len(importances) != len(feature_names):
        return None

    return pd.DataFrame(
        {"Feature": feature_names, "Importance": importances}
    ).sort_values(by="Importance", ascending=False)


def list_local_csv_files() -> list[str]:
    roots = [ROOT / "data/raw", ROOT / "data/raw/MachineLearningCVE"]
    csv_files: list[str] = []
    for root in roots:
        if root.exists():
            csv_files.extend(str(path) for path in sorted(root.glob("*.csv")))
    return csv_files


def read_uploaded_csv(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(uploaded_file.getvalue()))


@st.cache_resource
def load_model():
    return joblib.load(ROOT / "artifacts/models/model.pkl")

@st.cache_resource
def load_scaler():
    scaler_path = ROOT / "artifacts/models/scaler.pkl"
    features_path = ROOT / "artifacts/models/feature_columns.pkl"
    if not scaler_path.exists() or not features_path.exists():
        return None, None, (
            "Scaler or feature columns not found. "
            "Run train_model.py first to generate artifacts/models/scaler.pkl."
        )
    return joblib.load(scaler_path), joblib.load(features_path), None

def prepare_predictions(
    raw_data: pd.DataFrame,
    model,
    scaler,
    expected_features: list[str] | None,
) -> dict:
    messages: dict[str, list[str] | str] = {
        "warnings": [],
        "errors": [],
        "mode_text": "",
    }

    data = clean_data(raw_data)
    if data.empty:
        messages["errors"].append("The dataset is empty after cleaning.")
        return {
            "ready": False,
            "messages": messages,
            "data": data,
        }

    label_column = resolve_label_column(data.columns)
    messages["mode_text"] = (
        "Labeled CSV (evaluation + prediction)"
        if label_column is not None
        else "Unlabeled CSV (prediction only)"
    )

    X_raw = data.drop(columns=[label_column]) if label_column is not None else data.copy()
    y_true = data[label_column] if label_column is not None else None

    if expected_features is not None:
        missing_features, extra_features = validate_schema(X_raw, expected_features)

        if missing_features:
            messages["errors"].append(
                "Schema mismatch: missing required columns. "
                f"Examples: {missing_features[:8]}"
            )

        if extra_features:
            messages["warnings"].append(
                f"Ignoring {len(extra_features)} extra columns not used during training."
            )

        if not messages["errors"]:
            X_raw = X_raw.reindex(columns=expected_features)
    else:
        expected_count = getattr(model, "n_features_in_", None)
        if expected_count is not None and X_raw.shape[1] != expected_count:
            messages["errors"].append(
                f"Feature count mismatch: model expects {expected_count} features, "
                f"but input provides {X_raw.shape[1]}."
            )

    if messages["errors"]:
        return {
            "ready": False,
            "messages": messages,
            "data": data,
        }

    X_numeric, valid_rows = coerce_numeric_features(X_raw)
    dropped_rows = int((~valid_rows).sum())
    if dropped_rows > 0:
        messages["warnings"].append(
            f"Dropped {dropped_rows} rows with non-numeric or invalid feature values."
        )

    X_numeric = X_numeric.loc[valid_rows]
    if y_true is not None:
        y_true = y_true.loc[valid_rows]

    if X_numeric.empty:
        messages["errors"].append("No valid rows remain after numeric validation.")
        return {
            "ready": False,
            "messages": messages,
            "data": data,
        }

    if scaler is not None and expected_features is not None:
        X_for_model = scaler.transform(X_numeric[expected_features])
        feature_names = expected_features
    else:
        X_for_model = X_numeric.to_numpy()
        feature_names = X_numeric.columns.tolist()

    predictions = model.predict(X_for_model)
    result_data = data.loc[X_numeric.index].copy()
    result_data["Prediction"] = predictions

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_for_model)
        result_data["Confidence"] = probabilities.max(axis=1)

    return {
        "ready": True,
        "messages": messages,
        "data": data,
        "result_data": result_data,
        "y_true": y_true,
        "predictions": predictions,
        "feature_names": feature_names,
    }


def render_messages(messages: dict):
    if messages.get("mode_text"):
        st.info(f"Detection Mode: {messages['mode_text']}")
    for warning in messages.get("warnings", []):
        st.warning(warning)
    for error in messages.get("errors", []):
        st.error(error)


def render_prediction_tab(result: dict, model):
    data = result["data"]
    result_data = result["result_data"]
    y_true = result["y_true"]
    predictions = result["predictions"]

    st.subheader("Dataset Preview")
    st.dataframe(data.head())

    st.subheader("Dataset Info")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(data))
    col2.metric("Columns", len(data.columns))
    col3.metric("Missing Values Removed", "Yes")

    st.subheader("Prediction Results")
    prediction_counts = (
        result_data["Prediction"]
        .value_counts()
        .rename_axis("Attack Type")
        .reset_index(name="Count")
    )
    st.dataframe(prediction_counts)

    st.subheader("Attack Distribution")
    st.bar_chart(result_data["Prediction"].value_counts())

    if "Confidence" in result_data.columns:
        st.subheader("Prediction Confidence")
        c1, c2 = st.columns(2)
        c1.metric("Average Confidence", f"{result_data['Confidence'].mean():.2%}")
        c2.metric("Lowest Confidence", f"{result_data['Confidence'].min():.2%}")

        confidence_sample = result_data[["Prediction", "Confidence"]].head(20).copy()
        confidence_sample["Confidence"] = confidence_sample["Confidence"].map(
            lambda value: f"{value:.2%}"
        )
        st.dataframe(confidence_sample)

    if y_true is not None:
        st.subheader("Actual vs Predicted Sample")
        comparison = pd.DataFrame(
            {
                "Actual Label": y_true.astype(str),
                "Prediction": pd.Series(predictions, index=y_true.index).astype(str),
            }
        )
        st.dataframe(comparison.head(20))

        st.subheader("Evaluation Metrics")
        y_true_str = y_true.astype(str)
        predictions_str = pd.Series(predictions, index=y_true.index).astype(str)

        accuracy = (y_true_str == predictions_str).mean()
        report_dict = classification_report(y_true_str, predictions_str, output_dict=True, zero_division=0)
        report_df = pd.DataFrame(report_dict).T
        report_df = report_df.drop(index=[c for c in ["accuracy", "macro avg", "weighted avg"] if c in report_df.index], errors="ignore")
        report_df = report_df[["precision", "recall", "f1-score", "support"]].round(4)

        macro_f1 = report_dict.get("macro avg", {}).get("f1-score", None)
        weighted_f1 = report_dict.get("weighted avg", {}).get("f1-score", None)

        c1, c2, c3 = st.columns(3)
        c1.metric("Accuracy", f"{accuracy:.4f}")
        if macro_f1 is not None:
            c2.metric("Macro F1", f"{macro_f1:.4f}")
        if weighted_f1 is not None:
            c3.metric("Weighted F1", f"{weighted_f1:.4f}")

        try:
            lb = LabelBinarizer()
            y_bin = lb.fit_transform(y_true_str)
            pred_bin = lb.transform(predictions_str)
            if y_bin.shape[1] > 1:
                auc = roc_auc_score(y_bin, pred_bin, average="macro", multi_class="ovr")
                st.metric("Macro AUC-ROC", f"{auc:.4f}")
        except Exception:
            pass

        st.markdown("**Per-Class Metrics (Precision / Recall / F1)**")
        st.dataframe(report_df, use_container_width=True)

        st.markdown("**Confusion Matrix**")
        labels = sorted(y_true_str.unique())
        cm = confusion_matrix(y_true_str, predictions_str, labels=labels)
        fig, ax = plt.subplots(figsize=(max(6, len(labels)), max(5, len(labels) - 1)))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            ax=ax,
        )
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.subheader("Evaluation")
        st.write("No label column detected, so accuracy metrics are skipped.")

    st.subheader("Prediction Summary")
    total_attacks = (result_data["Prediction"] != "BENIGN").sum()
    benign_count = (result_data["Prediction"] == "BENIGN").sum()

    c1, c2 = st.columns(2)
    c1.metric("Predicted BENIGN", int(benign_count))
    c2.metric("Predicted Attacks", int(total_attacks))

    st.download_button(
        label="Download Predictions CSV",
        data=result_data.to_csv(index=False).encode("utf-8"),
        file_name="predictions_output.csv",
        mime="text/csv",
    )

    st.subheader("Top 15 Most Important Features")
    feature_importance_df = get_feature_importance_df(model, result["feature_names"])
    if feature_importance_df is not None:
        top_features = feature_importance_df.head(15)
        st.dataframe(top_features)
        st.bar_chart(top_features.set_index("Feature")["Importance"])
    else:
        st.info("This model does not support aligned feature-importance visualization.")


def run_live_simulation(result_data: pd.DataFrame, batch_size: int, max_batches: int, sleep_time: float, alert_threshold: float):
    total_rows = len(result_data)
    total_batches = math.ceil(total_rows / batch_size)
    batches_to_run = min(total_batches, max_batches)

    if batches_to_run <= 0:
        st.warning("No batches to simulate. Increase max batches or reduce batch size.")
        return

    status_placeholder = st.empty()
    progress_placeholder = st.progress(0)
    log_placeholder = st.empty()

    logs = []

    for batch_index in range(batches_to_run):
        start = batch_index * batch_size
        end = min(start + batch_size, total_rows)
        batch = result_data.iloc[start:end]

        benign_count = int((batch["Prediction"] == "BENIGN").sum())
        attack_count = int(len(batch) - benign_count)
        attack_rate = attack_count / len(batch)

        attack_only = batch[batch["Prediction"] != "BENIGN"]
        top_attack = (
            attack_only["Prediction"].value_counts().idxmax()
            if not attack_only.empty
            else "None"
        )

        avg_confidence = float(batch["Confidence"].mean()) if "Confidence" in batch.columns else np.nan
        high_conf_alerts = 0
        if "Confidence" in batch.columns:
            high_conf_alerts = int(
                ((batch["Prediction"] != "BENIGN") & (batch["Confidence"] >= alert_threshold)).sum()
            )

        logs.append(
            {
                "Batch": batch_index + 1,
                "Rows": len(batch),
                "Status": "ALERT" if attack_count > 0 else "OK",
                "Predicted Attacks": attack_count,
                "Attack Rate": f"{attack_rate:.2%}",
                "Top Attack": top_attack,
                "Avg Confidence": f"{avg_confidence:.2%}" if not np.isnan(avg_confidence) else "N/A",
                f"High-Confidence Alerts (>= {alert_threshold:.2f})": high_conf_alerts,
            }
        )

        status_placeholder.markdown(
            f"**Batch {batch_index + 1}/{batches_to_run}** | "
            f"Rows {start + 1}-{end} | "
            f"Status: {'ALERT' if attack_count > 0 else 'OK'} | "
            f"Top Attack: {top_attack}"
        )

        log_placeholder.dataframe(pd.DataFrame(logs), use_container_width=True)
        progress_placeholder.progress((batch_index + 1) / batches_to_run)

        if sleep_time > 0 and batch_index < batches_to_run - 1:
            time.sleep(sleep_time)

    st.success("Live simulation complete.")

    total_attack_predictions = int((result_data["Prediction"] != "BENIGN").sum())
    c1, c2 = st.columns(2)
    c1.metric("Total Predicted Attacks", total_attack_predictions)
    c2.metric("Rows Simulated", int(min(total_rows, batches_to_run * batch_size)))

    log_df = pd.DataFrame(logs)
    st.download_button(
        label="Download Simulation Batch Log",
        data=log_df.to_csv(index=False).encode("utf-8"),
        file_name="simulation_batch_log.csv",
        mime="text/csv",
    )


model = load_model()
scaler, expected_features, preprocessor_warning = load_scaler()

tab_predict, tab_simulation = st.tabs(["Prediction Dashboard", "Live Simulation"])

with tab_predict:
    st.caption("Use this tab for standard prediction analysis on uploaded CSV files.")
    if uploaded_file:
        try:
            raw_data = read_uploaded_csv(uploaded_file)
            result = prepare_predictions(raw_data, model, scaler, expected_features)

            if preprocessor_warning:
                st.warning(preprocessor_warning)

            render_messages(result["messages"])
            if result["ready"]:
                render_prediction_tab(result, model)
        except Exception as exc:
            st.error(f"Error processing file: {exc}")
    else:
        st.info("Please upload a CSV dataset file to begin.")

with tab_simulation:
    st.caption(
        "Run a live-style simulation in batches so non-expert listeners can see detection behavior over time."
    )

    source_mode = st.radio(
        "Simulation data source",
        options=["Uploaded file", "Local sample file"],
        horizontal=True,
        key="sim_source_mode",
    )

    selected_local_path = None
    if source_mode == "Local sample file":
        local_csv_files = list_local_csv_files()
        if local_csv_files:
            selected_local_path = st.selectbox(
                "Choose local CSV",
                options=local_csv_files,
                index=0,
                key="sim_local_path",
            )
        else:
            st.warning("No local CSV files found under data/raw/ or data/raw/MachineLearningCVE/.")

    c1, c2, c3 = st.columns(3)
    batch_size = c1.slider("Batch size", min_value=100, max_value=5000, value=500, step=100)
    max_batches = c2.slider("Max batches", min_value=1, max_value=50, value=8, step=1)
    sleep_time = c3.slider("Delay between batches (sec)", min_value=0.0, max_value=2.0, value=0.7, step=0.1)

    c4, c5 = st.columns(2)
    alert_threshold = c4.slider("High-confidence alert threshold", 0.50, 0.99, 0.80, 0.01)
    shuffle_rows = c5.checkbox("Shuffle rows before simulation", value=True)

    run_simulation_clicked = st.button("Start Live Simulation", type="primary", key="start_live_simulation")

    if run_simulation_clicked:
        try:
            if source_mode == "Uploaded file":
                if uploaded_file is None:
                    st.error("Upload a CSV first or switch to Local sample file mode.")
                    st.stop()
                raw_data = read_uploaded_csv(uploaded_file)
            else:
                if not selected_local_path:
                    st.error("Select a local CSV file for simulation.")
                    st.stop()
                raw_data = pd.read_csv(selected_local_path)

            if shuffle_rows:
                raw_data = raw_data.sample(frac=1.0, random_state=42)

            result = prepare_predictions(raw_data, model, scaler, expected_features)

            if preprocessor_warning:
                st.warning(preprocessor_warning)

            render_messages(result["messages"])
            if not result["ready"]:
                st.stop()

            st.subheader("Simulation Stream")
            run_live_simulation(
                result_data=result["result_data"],
                batch_size=batch_size,
                max_batches=max_batches,
                sleep_time=sleep_time,
                alert_threshold=alert_threshold,
            )

            st.subheader("Final Distribution (All Processed Rows)")
            st.bar_chart(result["result_data"]["Prediction"].value_counts())

        except Exception as exc:
            st.error(f"Error running simulation: {exc}")
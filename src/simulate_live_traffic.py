import argparse
import math
import time
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


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


def load_reference_preprocessor(reference_path: Path):
    if not reference_path.exists():
        return None, None, (
            f"Reference dataset '{reference_path}' not found. "
            "Simulation will run without training-time scaling."
        )

    try:
        reference_data = pd.read_csv(reference_path)
        reference_data = clean_data(reference_data)
        label_column = resolve_label_column(reference_data.columns)

        if label_column is None:
            return None, None, (
                "Reference dataset does not contain a Label column. "
                "Simulation will run without training-time scaling."
            )

        feature_columns = [column for column in reference_data.columns if column != label_column]
        scaler = StandardScaler()
        scaler.fit(reference_data[feature_columns])
        return scaler, feature_columns, None
    except Exception as exc:
        return None, None, (
            "Could not build reference preprocessor. "
            f"Simulation will run without scaling. Details: {exc}"
        )


def validate_schema(X_raw: pd.DataFrame, expected_features: list[str]):
    missing_features = [feature for feature in expected_features if feature not in X_raw.columns]
    extra_features = [feature for feature in X_raw.columns if feature not in expected_features]
    return missing_features, extra_features


def format_percent(value: float | None) -> str:
    if value is None or np.isnan(value):
        return "N/A"
    return f"{value * 100:.2f}%"


def run_simulation(args):
    model = joblib.load(args.model)
    scaler, expected_features, preprocessor_warning = load_reference_preprocessor(Path(args.reference_csv))

    if preprocessor_warning:
        print(f"[WARN] {preprocessor_warning}")

    data = pd.read_csv(args.csv)
    data = clean_data(data)

    if data.empty:
        raise ValueError("Uploaded dataset is empty after cleaning.")

    label_column = resolve_label_column(data.columns)
    X_raw = data.drop(columns=[label_column]) if label_column is not None else data.copy()
    y_true = data[label_column] if label_column is not None else None

    if expected_features is not None:
        missing_features, extra_features = validate_schema(X_raw, expected_features)

        if missing_features:
            preview = ", ".join(missing_features[:10])
            raise ValueError(
                "Schema mismatch: missing required columns in simulation data. "
                f"Examples: {preview}"
            )

        if extra_features:
            print(
                f"[WARN] Ignoring {len(extra_features)} extra columns not used in training."
            )

        X_raw = X_raw.reindex(columns=expected_features)
    else:
        expected_count = getattr(model, "n_features_in_", None)
        if expected_count is not None and X_raw.shape[1] != expected_count:
            raise ValueError(
                f"Feature count mismatch: model expects {expected_count} features, "
                f"but simulation data provides {X_raw.shape[1]}."
            )

    X_numeric = X_raw.apply(pd.to_numeric, errors="coerce")
    valid_rows = ~X_numeric.isna().any(axis=1)

    dropped_rows = int((~valid_rows).sum())
    if dropped_rows > 0:
        print(f"[WARN] Dropped {dropped_rows} rows with invalid numeric feature values.")

    X_numeric = X_numeric.loc[valid_rows]
    if y_true is not None:
        y_true = y_true.loc[valid_rows]

    if X_numeric.empty:
        raise ValueError("No valid rows remain after numeric validation.")

    if args.shuffle:
        X_numeric = X_numeric.sample(frac=1.0, random_state=args.random_state)
        if y_true is not None:
            y_true = y_true.loc[X_numeric.index]

    if scaler is not None and expected_features is not None:
        X_for_model = scaler.transform(X_numeric[expected_features])
    else:
        X_for_model = X_numeric.to_numpy()

    predictions = model.predict(X_for_model)

    confidence = None
    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(X_for_model).max(axis=1)

    result_data = data.loc[X_numeric.index].copy()
    result_data["Prediction"] = predictions
    if confidence is not None:
        result_data["Confidence"] = confidence

    total_rows = len(result_data)
    total_batches = math.ceil(total_rows / args.batch_size)
    batch_limit = min(total_batches, args.max_batches) if args.max_batches else total_batches

    print("\n=== AI NIDS Live Simulation ===")
    print(f"Model: {args.model}")
    print(f"Source CSV: {args.csv}")
    print(f"Rows used: {total_rows}")
    print(f"Batch size: {args.batch_size}")
    print(f"Batches to simulate: {batch_limit}/{total_batches}")
    print("===============================\n")

    summaries = []

    for batch_index in range(batch_limit):
        start = batch_index * args.batch_size
        end = min(start + args.batch_size, total_rows)
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

        avg_confidence = float(batch["Confidence"].mean()) if "Confidence" in batch.columns else None

        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "ALERT" if attack_count > 0 else "OK"

        print(
            f"[{timestamp}] Batch {batch_index + 1}/{batch_limit} | "
            f"Rows {start + 1}-{end} | Status: {status} | "
            f"Attacks: {attack_count}/{len(batch)} ({format_percent(attack_rate)}) | "
            f"Top attack: {top_attack} | Avg confidence: {format_percent(avg_confidence)}"
        )

        high_conf_alerts = 0
        if "Confidence" in batch.columns:
            high_conf_alerts = int(
                ((batch["Prediction"] != "BENIGN") & (batch["Confidence"] >= args.alert_threshold)).sum()
            )

        if high_conf_alerts > 0:
            print(
                f"   -> High-confidence alerts (>= {args.alert_threshold:.2f}): {high_conf_alerts}"
            )

        summaries.append(
            {
                "batch": batch_index + 1,
                "rows": len(batch),
                "attack_count": attack_count,
                "attack_rate": attack_rate,
                "top_attack": top_attack,
                "avg_confidence": avg_confidence,
                "high_conf_alerts": high_conf_alerts,
            }
        )

        if args.sleep > 0 and batch_index < batch_limit - 1:
            time.sleep(args.sleep)

    print("\n=== Simulation Summary ===")
    total_attack_predictions = int((result_data["Prediction"] != "BENIGN").sum())
    print(f"Total predicted attacks: {total_attack_predictions}/{total_rows}")

    if y_true is not None:
        prediction_series = pd.Series(predictions, index=X_numeric.index)
        accuracy = float((y_true.astype(str) == prediction_series.astype(str)).mean())
        print(f"Accuracy against labels: {format_percent(accuracy)}")

    if args.log_file:
        pd.DataFrame(summaries).to_csv(args.log_file, index=False)
        print(f"Batch log saved to: {args.log_file}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Simulate near real-time NIDS predictions from CSV traffic data."
    )
    parser.add_argument(
        "--csv",
        default="data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv",
        help="Path to the traffic CSV to simulate.",
    )
    parser.add_argument(
        "--model",
        default="artifacts/models/model.pkl",
        help="Path to trained model file.",
    )
    parser.add_argument(
        "--reference-csv",
        default="data/processed/combined_dataset.csv",
        help="Reference dataset used to rebuild preprocessing (feature order + scaling).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Rows per simulated time window.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds to wait between batches.",
    )
    parser.add_argument(
        "--max-batches",
        type=int,
        default=10,
        help="Maximum number of batches to run (0 or negative = all batches).",
    )
    parser.add_argument(
        "--alert-threshold",
        type=float,
        default=0.80,
        help="Confidence threshold for high-confidence attack alerts.",
    )
    parser.add_argument(
        "--log-file",
        default="artifacts/logs/simulation_batch_log.csv",
        help="CSV file to save per-batch summary.",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle rows before simulation for mixed traffic windows.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed used when --shuffle is enabled.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.max_batches <= 0:
        args.max_batches = None

    run_simulation(args)


if __name__ == "__main__":
    main()

from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
)


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"

DATA_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "CIC-IDS2017"
)

OUTPUT_DIR = MODEL_DIR / "evaluation"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# LOAD MODEL
# ==========================================

print("\nLoading CyberSentinel AI model...\n")

model = joblib.load(
    MODEL_DIR / "random_forest_multiclass.joblib"
)

scaler = joblib.load(
    MODEL_DIR / "multiclass_scaler.joblib"
)

label_encoder = joblib.load(
    MODEL_DIR / "label_encoder.joblib"
)

with open(
    MODEL_DIR / "multiclass_feature_columns.json",
    "r"
) as f:
    feature_columns = json.load(f)


# ==========================================
# EVALUATE EACH FILE
# ==========================================

results = []


csv_files = sorted(
    DATA_DIR.glob("*.csv")
)


if not csv_files:

    raise FileNotFoundError(
        "No CIC-IDS2017 CSV files found."
    )


for file in csv_files:

    print("\n" + "=" * 70)

    print(
        f"Evaluating: {file.name}"
    )

    print("=" * 70)

    try:

        df = pd.read_csv(
            file,
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            file,
            encoding="cp1252"
        )


    df.columns = (
        df.columns
        .str.strip()
    )


    # --------------------------------------
    # CLEAN
    # --------------------------------------

    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    df = df.dropna(
        subset=["Label"]
    )

    df = df.dropna(
        subset=feature_columns
    )


    if df.empty:

        print(
            "No valid rows found. Skipping."
        )

        continue


    X = df[
        feature_columns
    ]

    y = label_encoder.transform(
        df["Label"]
    )


    # --------------------------------------
    # PREDICTION
    # --------------------------------------

    X_scaled = scaler.transform(
        X
    )

    y_pred = model.predict(
        X_scaled
    )


    # --------------------------------------
    # METRICS
    # --------------------------------------

    accuracy = accuracy_score(
        y,
        y_pred
    )

    balanced_accuracy = (
        balanced_accuracy_score(
            y,
            y_pred
        )
    )

    macro_f1 = f1_score(
        y,
        y_pred,
        average="macro"
    )

    weighted_f1 = f1_score(
        y,
        y_pred,
        average="weighted"
    )


    print(
        f"Rows:               {len(df):,}"
    )

    print(
        f"Accuracy:           {accuracy:.4f}"
    )

    print(
        f"Balanced Accuracy:  {balanced_accuracy:.4f}"
    )

    print(
        f"Macro F1:           {macro_f1:.4f}"
    )

    print(
        f"Weighted F1:        {weighted_f1:.4f}"
    )


    results.append(
        {
            "dataset": file.name,

            "rows": len(df),

            "accuracy": round(
                float(accuracy),
                4
            ),

            "balanced_accuracy": round(
                float(balanced_accuracy),
                4
            ),

            "macro_f1": round(
                float(macro_f1),
                4
            ),

            "weighted_f1": round(
                float(weighted_f1),
                4
            ),
        }
    )


# ==========================================
# SAVE RESULTS
# ==========================================

results_df = pd.DataFrame(
    results
)


output_file = (
    OUTPUT_DIR
    / "scenario_evaluation.csv"
)


results_df.to_csv(
    output_file,
    index=False
)


json_file = (
    OUTPUT_DIR
    / "scenario_evaluation.json"
)


with open(
    json_file,
    "w"
) as f:

    json.dump(
        results,
        f,
        indent=4
    )


# ==========================================
# SUMMARY
# ==========================================

print("\n")

print("=" * 70)

print(
    "CYBERSENTINEL AI SCENARIO EVALUATION"
)

print("=" * 70)

print("\n")

print(
    results_df.to_string(
        index=False
    )
)

print("\n")

print(
    f"CSV saved to:\n{output_file}"
)

print(
    f"\nJSON saved to:\n{json_file}"
)

print("\nScenario evaluation complete! ✅")
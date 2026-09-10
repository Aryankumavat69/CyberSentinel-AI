from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
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


# ==========================================
# LOAD MODEL
# ==========================================

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


print("\nLoading CIC-IDS2017 data...\n")


# ==========================================
# LOAD DATASET
# ==========================================

frames = []

for file in DATA_DIR.glob("*.csv"):

    print(f"Loading: {file.name}")

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

    frames.append(df)


if not frames:

    raise FileNotFoundError(
        "No CSV files found in "
        "data/raw/CIC-IDS2017"
    )


data = pd.concat(
    frames,
    ignore_index=True
)


# ==========================================
# CLEAN DATA
# ==========================================

data = data.replace(
    [float("inf"), float("-inf")],
    pd.NA
)

data = data.dropna(
    subset=["Label"]
)

data = data.dropna(
    subset=feature_columns
)


X = data[
    feature_columns
]

y = label_encoder.transform(
    data["Label"]
)


print("\nDataset shape:")
print(X.shape)


# ==========================================
# SCALE FEATURES
# ==========================================

X_scaled = scaler.transform(X)


# ==========================================
# PREDICTIONS
# ==========================================

print("\nRunning predictions...\n")


y_pred = model.predict(
    X_scaled
)


# ==========================================
# METRICS
# ==========================================

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


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n")
print("=" * 60)
print("CYBERSENTINEL AI MODEL EVALUATION")
print("=" * 60)

print(
    f"\nAccuracy:           {accuracy:.4f}"
)

print(
    f"Balanced Accuracy:  {balanced_accuracy:.4f}"
)

print(
    f"Macro F1 Score:     {macro_f1:.4f}"
)

print(
    f"Weighted F1 Score:  {weighted_f1:.4f}"
)


# ==========================================
# CLASSIFICATION REPORT
# ==========================================

print("\n")
print("=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        y,
        y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ==========================================
# CONFUSION MATRIX
# ==========================================

print("\n")
print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

cm = confusion_matrix(
    y,
    y_pred
)

print(cm)


# ==========================================
# SAVE RESULTS
# ==========================================

results = {
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

    "classes":
        label_encoder.classes_.tolist()
}


with open(
    MODEL_DIR / "evaluation_results.json",
    "w"
) as f:

    json.dump(
        results,
        f,
        indent=4
    )


print(
    "\nEvaluation saved to:"
)

print(
    "models/evaluation_results.json"
)

print(
    "\nEvaluation complete! ✅"
)
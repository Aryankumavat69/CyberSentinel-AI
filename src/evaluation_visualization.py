from pathlib import Path
import json

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = MODEL_DIR / "evaluation"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# LOAD SAVED MODEL
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


# ==========================================
# LOAD DATA
# ==========================================

DATA_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "CIC-IDS2017"
)

frames = []

print("\nLoading dataset...\n")

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

    df.columns = df.columns.str.strip()

    frames.append(df)


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


# ==========================================
# PREDICTIONS
# ==========================================

print("\nGenerating predictions...\n")

X_scaled = scaler.transform(X)

y_pred = model.predict(
    X_scaled
)


class_names = label_encoder.classes_


# ==========================================
# 1. CONFUSION MATRIX
# ==========================================

cm = confusion_matrix(
    y,
    y_pred
)

fig, ax = plt.subplots(
    figsize=(14, 12)
)

ax.imshow(cm)

ax.set_title(
    "CyberSentinel AI - Confusion Matrix"
)

ax.set_xlabel(
    "Predicted Class"
)

ax.set_ylabel(
    "Actual Class"
)

ax.set_xticks(
    range(len(class_names))
)

ax.set_yticks(
    range(len(class_names))
)

ax.set_xticklabels(
    class_names,
    rotation=90
)

ax.set_yticklabels(
    class_names
)

for i in range(len(class_names)):

    for j in range(len(class_names)):

        ax.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center",
            fontsize=7
        )

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "confusion_matrix.png",
    dpi=200
)

plt.close()

print(
    "Saved: confusion_matrix.png"
)


# ==========================================
# 2. F1 SCORE BY CLASS
# ==========================================

report = classification_report(
    y,
    y_pred,
    target_names=class_names,
    output_dict=True,
    zero_division=0
)

report_df = pd.DataFrame(
    report
).transpose()

class_report = report_df.loc[
    class_names
]


plt.figure(
    figsize=(14, 7)
)

plt.bar(
    class_report.index,
    class_report["f1-score"]
)

plt.title(
    "CyberSentinel AI - F1 Score by Attack Class"
)

plt.xlabel(
    "Attack Class"
)

plt.ylabel(
    "F1 Score"
)

plt.xticks(
    rotation=75,
    ha="right"
)

plt.ylim(
    0,
    1.05
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "f1_score_by_class.png",
    dpi=200
)

plt.close()

print(
    "Saved: f1_score_by_class.png"
)


# ==========================================
# 3. PRECISION / RECALL / F1
# ==========================================

metrics = class_report[
    [
        "precision",
        "recall",
        "f1-score"
    ]
]

ax = metrics.plot(
    kind="bar",
    figsize=(15, 7)
)

ax.set_title(
    "CyberSentinel AI - Precision, Recall and F1"
)

ax.set_xlabel(
    "Attack Class"
)

ax.set_ylabel(
    "Score"
)

ax.set_ylim(
    0,
    1.05
)

plt.xticks(
    rotation=75,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "classification_metrics.png",
    dpi=200
)

plt.close()

print(
    "Saved: classification_metrics.png"
)


# ==========================================
# 4. OVERALL MODEL METRICS
# ==========================================

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score
)

accuracy = accuracy_score(
    y,
    y_pred
)

balanced_accuracy = balanced_accuracy_score(
    y,
    y_pred
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


metric_names = [
    "Accuracy",
    "Balanced Accuracy",
    "Macro F1",
    "Weighted F1"
]

metric_values = [
    accuracy,
    balanced_accuracy,
    macro_f1,
    weighted_f1
]


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    metric_names,
    metric_values
)

plt.title(
    "CyberSentinel AI - Overall Model Performance"
)

plt.ylabel(
    "Score"
)

plt.ylim(
    0,
    1.05
)

for i, value in enumerate(
    metric_values
):

    plt.text(
        i,
        value + 0.02,
        f"{value:.4f}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "overall_performance.png",
    dpi=200
)

plt.close()

print(
    "Saved: overall_performance.png"
)


# ==========================================
# SAVE EVALUATION RESULTS
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
        class_names.tolist()
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


# ==========================================
# COMPLETE
# ==========================================

print("\n")
print("=" * 55)
print("EVALUATION VISUALIZATION COMPLETE")
print("=" * 55)

print(
    f"\nCharts saved in:\n{OUTPUT_DIR}"
)

print("\nFiles created:")

print("1. confusion_matrix.png")
print("2. f1_score_by_class.png")
print("3. classification_metrics.png")
print("4. overall_performance.png")
print("5. evaluation_results.json")

print("\nDone! ✅")
from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw" / "CIC-IDS2017"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================


csv_files = list(DATA_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {DATA_DIR}"
    )

print(f"\nFound {len(csv_files)} CSV files.")

frames = []

for file in csv_files:

    print(f"Loading: {file.name}")

    try:
        df = pd.read_csv(
            file,
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        print(
            f"UTF-8 failed for {file.name}, "
            "using Windows-1252..."
        )

        df = pd.read_csv(
            file,
            encoding="cp1252"
        )

    # Clean column names
    df.columns = df.columns.str.strip()

    # IMPORTANT: append EVERY successfully loaded file
    frames.append(df)

    print(
        f"  Loaded {len(df):,} rows"
    )


# Make sure something was actually loaded
if not frames:
    raise ValueError(
        "No datasets were successfully loaded."
    )


# Combine all CSV files
data = pd.concat(
    frames,
    ignore_index=True
)

print("\n===================================")
print("DATASET LOADING COMPLETE")
print("===================================")

print(
    f"Total rows: {len(data):,}"
)

print(
    f"Total columns: {len(data.columns)}"
)

print(
    f"Files combined: {len(frames)}"
)


# ============================================================
# 2. CLEAN LABEL COLUMN
# ============================================================

label_column = "Label"

if label_column not in data.columns:
    raise ValueError(
        f"'{label_column}' column not found."
    )

data[label_column] = (
    data[label_column]
    .astype(str)
    .str.strip()
)


# ============================================================
# 3. REMOVE INVALID VALUES
# ============================================================

data = data.replace(
    [float("inf"), float("-inf")],
    pd.NA
)

data = data.dropna()

print("\nDataset after cleaning:")
print(data.shape)


# ============================================================
# 4. REMOVE NON-NUMERIC COLUMNS
# ============================================================

columns_to_drop = [
    "Flow ID",
    "Source IP",
    "Destination IP",
    "Timestamp",
]

existing_drop_columns = [
    column
    for column in columns_to_drop
    if column in data.columns
]

X = data.drop(
    columns=[label_column] + existing_drop_columns
)

y = data[label_column]


# ============================================================
# 5. KEEP ONLY NUMERIC FEATURES
# ============================================================

X = X.select_dtypes(
    include=["number"]
)

print("\nNumber of features:")
print(X.shape[1])


# ============================================================
# 6. ENCODE LABELS
# ============================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("\nAttack classes:")
for index, class_name in enumerate(
    label_encoder.classes_
):
    count = (y == class_name).sum()

    print(
        f"{index}: {class_name} -> {count}"
    )


# ============================================================
# 7. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded,
)

print("\nTraining shape:")
print(X_train.shape)

print("Testing shape:")
print(X_test.shape)


# ============================================================
# 8. SCALE FEATURES
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)


# ============================================================
# 9. TRAIN RANDOM FOREST
# ============================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced",
)

model.fit(
    X_train_scaled,
    y_train
)

print("Training complete.")


# ============================================================
# 10. PREDICTIONS
# ============================================================

y_pred = model.predict(
    X_test_scaled
)


# ============================================================
# 11. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n===================================")
print("MULTICLASS MODEL RESULTS")
print("===================================")

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
    )
)


print("\nConfusion Matrix:\n")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 12. SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_DIR / "random_forest_multiclass.joblib"
)

joblib.dump(
    scaler,
    MODEL_DIR / "multiclass_scaler.joblib"
)

joblib.dump(
    label_encoder,
    MODEL_DIR / "label_encoder.joblib"
)


# ============================================================
# 13. SAVE FEATURE SCHEMA
# ============================================================

feature_columns = X.columns.tolist()

with open(
    MODEL_DIR / "multiclass_feature_columns.json",
    "w"
) as f:

    json.dump(
        feature_columns,
        f,
        indent=2
    )


# ============================================================
# 14. SAVE CLASS NAMES
# ============================================================

with open(
    MODEL_DIR / "class_names.json",
    "w"
) as f:

    json.dump(
        label_encoder.classes_.tolist(),
        f,
        indent=2
    )


print("\n===================================")
print("MODEL FILES SAVED")
print("===================================")

print(
    MODEL_DIR / "random_forest_multiclass.joblib"
)

print(
    MODEL_DIR / "multiclass_scaler.joblib"
)

print(
    MODEL_DIR / "label_encoder.joblib"
)

print(
    MODEL_DIR / "multiclass_feature_columns.json"
)

print(
    MODEL_DIR / "class_names.json"
)
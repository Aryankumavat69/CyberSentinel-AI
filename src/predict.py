from pathlib import Path
import json

import joblib
import pandas as pd
import shap


# ==============================
# PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


# ==============================
# LOAD MULTICLASS MODEL
# ==============================

model = joblib.load(
    MODEL_DIR / "random_forest_multiclass.joblib"
)

scaler = joblib.load(
    MODEL_DIR / "multiclass_scaler.joblib"
)

label_encoder = joblib.load(
    MODEL_DIR / "label_encoder.joblib"
)


# ==============================
# LOAD FEATURE SCHEMA
# ==============================

with open(
    MODEL_DIR / "multiclass_feature_columns.json",
    "r"
) as f:
    feature_columns = json.load(f)


# ==============================
# SHAP EXPLAINER
# ==============================

explainer = shap.TreeExplainer(model)


# ==============================
# PREDICTION FUNCTION
# ==============================

def predict_threat(input_data):

    input_df = pd.DataFrame(input_data)

    # Check for missing features
    missing_features = [
        feature
        for feature in feature_columns
        if feature not in input_df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    # Keep features in the exact training order
    input_features = input_df[
        feature_columns
    ]

    # Scale input
    input_scaled = scaler.transform(
        input_features
    )

    # Prediction
    prediction = model.predict(
        input_scaled
    )[0]

    # Class probabilities
    probabilities = model.predict_proba(
        input_scaled
    )[0]

    # Convert encoded class back to name
    label = label_encoder.inverse_transform(
        [prediction]
    )[0]

    # ==============================
    # RISK SCORE
    # ==============================

    class_names = list(
        label_encoder.classes_
    )

    benign_index = class_names.index(
        "BENIGN"
    )

    malicious_probability = (
        1 - probabilities[benign_index]
    )

    risk_score = malicious_probability * 100


    # ==============================
    # SEVERITY
    # ==============================

    if risk_score < 25:
        severity = "LOW"

    elif risk_score < 50:
        severity = "MEDIUM"

    elif risk_score < 75:
        severity = "HIGH"

    else:
        severity = "CRITICAL"


    # ==============================
    # CLASS PROBABILITIES
    # ==============================

    class_probabilities = {}

    for class_name, probability in zip(
        class_names,
        probabilities
    ):
        class_probabilities[class_name] = round(
            float(probability * 100),
            2
        )


    # ==============================
    # SHAP EXPLANATION
    # ==============================

    shap_values = explainer.shap_values(
        input_scaled
    )

    if isinstance(shap_values, list):

        shap_for_prediction = (
            shap_values[prediction][0]
        )

    else:

        shap_array = shap_values

        if shap_array.ndim == 3:

            shap_for_prediction = (
                shap_array[
                    0,
                    :,
                    prediction
                ]
            )

        else:

            shap_for_prediction = (
                shap_array[0]
            )


    # ==============================
    # FEATURE CONTRIBUTIONS
    # ==============================

    feature_contributions = []

    for feature, value in zip(
        feature_columns,
        shap_for_prediction
    ):

        feature_contributions.append(
            {
                "feature": feature,
                "impact": round(
                    float(value),
                    6
                )
            }
        )


    # Sort by strongest impact
    feature_contributions.sort(
        key=lambda x: abs(
            x["impact"]
        ),
        reverse=True
    )


    # Top 8 features
    top_features = (
        feature_contributions[:8]
    )


    # ==============================
    # FINAL RESULT
    # ==============================

    return {

        "prediction": label,

        "risk_score": round(
            risk_score,
            2
        ),

        "severity": severity,

        "benign_probability": round(
            float(
                probabilities[
                    benign_index
                ] * 100
            ),
            2
        ),

        "class_probabilities":
            class_probabilities,

        "top_features":
            top_features
    }
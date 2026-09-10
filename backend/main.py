from pathlib import Path
from typing import Any
import json

import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.predict import predict_threat, feature_columns


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "CIC-IDS2017"
)

MODEL_DIR = BASE_DIR / "models"

EVALUATION_DIR = MODEL_DIR / "evaluation"


app = FastAPI(
    title="CyberSentinel AI",
    description="AI-powered network threat detection API",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cyber-sentinel-ai-mgje-amber.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    data: list[dict[str, Any]]


SCENARIOS = {
    "benign": "Monday-WorkingHours.pcap_ISCX.csv",
    "ddos": "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "portscan": "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "webattack": "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "infiltration": "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "dos": "Wednesday-workingHours.pcap_ISCX.csv",
    "bot": "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "ssh_ftp": "Tuesday-WorkingHours.pcap_ISCX.csv",
}


@app.get("/")
def home():

    return {
        "message": "🛡️ CyberSentinel AI API is running!",
        "status": "online",
        "model": "Multiclass Random Forest",
        "version": "4.0.0",
        "scenarios": list(
            SCENARIOS.keys()
        )
    }


@app.get("/sample")
def get_sample():

    return get_scenario_sample("benign")


@app.get("/sample/{scenario}")
def get_scenario_sample(
    scenario: str
):

    scenario = scenario.lower()

    if scenario not in SCENARIOS:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Unknown scenario",
                "available_scenarios":
                    list(SCENARIOS.keys())
            }
        )

    file_path = (
        DATA_DIR
        / SCENARIOS[scenario]
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Dataset file not found"
        )

    try:

        df = pd.read_csv(
            file_path,
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            file_path,
            encoding="cp1252"
        )

    df.columns = (
        df.columns
        .str.strip()
    )

    sample_df = df[
        feature_columns
    ].dropna()

    if sample_df.empty:

        raise HTTPException(
            status_code=404,
            detail="No valid sample found"
        )

    sample = sample_df.iloc[[0]]

    return {
        "success": True,
        "scenario": scenario,
        "file": SCENARIOS[scenario],
        "feature_count": len(
            feature_columns
        ),
        "data": sample.to_dict(
            orient="records"
        )[0]
    }


@app.post("/predict")
def predict(
    request: PredictionRequest
):

    try:

        result = predict_threat(
            request.data
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# ANALYST FEEDBACK
# ==========================================

class FeedbackRequest(BaseModel):
    prediction: str
    severity: str
    risk_score: float
    feedback: str
    comment: str = ""


@app.post("/feedback")
def submit_feedback(
    request: FeedbackRequest
):

    feedback_dir = (
        BASE_DIR
        / "data"
        / "processed"
    )

    feedback_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    feedback_file = (
        feedback_dir
        / "analyst_feedback.csv"
    )

    new_feedback = pd.DataFrame([
        {
            "prediction": request.prediction,
            "severity": request.severity,
            "risk_score": request.risk_score,
            "feedback": request.feedback,
            "comment": request.comment
        }
    ])

    if feedback_file.exists():

        new_feedback.to_csv(
            feedback_file,
            mode="a",
            header=False,
            index=False
        )

    else:

        new_feedback.to_csv(
            feedback_file,
            index=False
        )

    return {
        "success": True,
        "message":
            "Analyst feedback recorded successfully."
    }


@app.get("/feedback")
def get_feedback():

    feedback_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "analyst_feedback.csv"
    )

    if not feedback_file.exists():

        return {
            "success": True,
            "total_feedback": 0,
            "feedback": []
        }

    df = pd.read_csv(
        feedback_file
    )

    return {
        "success": True,
        "total_feedback": len(df),
        "feedback":
            df.to_dict(
                orient="records"
            )
    }
# ==========================================
# SCENARIO PERFORMANCE
# ==========================================

@app.get("/scenario-evaluation")
def get_scenario_evaluation():

    file_path = (
        EVALUATION_DIR
        / "scenario_evaluation.json"
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Scenario evaluation results not found"
        )

    with open(
        file_path,
        "r"
    ) as f:

        results = json.load(f)

    return {
        "success": True,
        "results": results
    }
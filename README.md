# 🛡️ CyberSentinel-AI

### AI-Powered Network Threat Detection & Explainable Cybersecurity Dashboard

CyberSentinel-AI is an AI-powered cybersecurity platform designed to detect and classify suspicious network activity using Machine Learning.

The system analyzes network-flow data, identifies potential threats, calculates a risk score, explains predictions using SHAP, and provides an interactive dashboard for security analysis and analyst feedback.

---

## 🚀 Key Features

* 🤖 Multiclass Machine Learning threat detection
* 🔍 Detection of multiple network attack categories
* 📊 Risk scoring from 0–100
* 🚦 Threat severity classification
* 🧠 SHAP-based Explainable AI
* 📈 Class probability visualization
* 🖥️ Interactive React dashboard
* ⚡ FastAPI prediction backend
* 📝 Analyst feedback system
* 📋 Detection history and statistics
* 📊 Model evaluation and scenario evaluation
* 🔌 REST API architecture

---

## 🧠 Threat Detection

CyberSentinel-AI is trained using the **CIC-IDS2017** network intrusion dataset.

The multiclass model recognizes categories including:

* BENIGN
* DDoS
* DoS
* PortScan
* Bot
* Infiltration
* FTP-Patator
* SSH-Patator
* Heartbleed
* Web Attack
* and other attack categories available in the dataset.

---

## 🏗️ System Architecture

```text
Network Flow Data
        ↓
Feature Extraction
        ↓
Data Cleaning
        ↓
Feature Scaling
        ↓
Machine Learning Model
        ↓
Threat Classification
        ↓
Risk Score
        ↓
SHAP Explainability
        ↓
FastAPI Backend
        ↓
React Dashboard
        ↓
Analyst Feedback
```

---

## 🛠️ Technology Stack

### Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* Random Forest
* SHAP

### Backend

* FastAPI
* Uvicorn
* REST API

### Frontend

* React
* Vite
* Tailwind CSS
* JavaScript

### Dataset

* CIC-IDS2017

### Development

* VS Code
* Git
* GitHub

---

## 📊 Machine Learning Pipeline

```text
CIC-IDS2017
     ↓
Data Loading
     ↓
Data Cleaning
     ↓
Feature Selection
     ↓
Train/Test Split
     ↓
Standard Scaling
     ↓
Random Forest Training
     ↓
Multiclass Prediction
     ↓
Model Evaluation
     ↓
SHAP Explainability
```

---

## 🧠 Explainable AI

CyberSentinel-AI does not only provide a prediction.

It also identifies the network features that contributed most strongly to the prediction using **SHAP (SHapley Additive exPlanations)**.

This helps make the model's output more interpretable for security analysis.

---

## 📈 Model Evaluation

The project includes:

* Accuracy
* Balanced Accuracy
* Macro F1 Score
* Weighted F1 Score
* Classification Report
* Confusion Matrix
* Per-class F1 scores
* Scenario-based evaluation

Evaluation visualizations are generated automatically and stored in:

```text
models/evaluation/
```

---

## 🖥️ Dashboard

The web dashboard provides:

* Threat prediction
* Risk score
* Severity level
* Benign probability
* Multiclass probabilities
* SHAP feature contributions
* Detection history
* Analyst feedback
* System status

---

## 🔌 API Endpoints

| Endpoint               | Method | Purpose                      |
| ---------------------- | ------ | ---------------------------- |
| `/`                    | GET    | API status                   |
| `/sample`              | GET    | Get sample network data      |
| `/sample/{scenario}`   | GET    | Get scenario-specific sample |
| `/predict`             | POST   | Predict network threat       |
| `/evaluation`          | GET    | Model evaluation results     |
| `/scenario-evaluation` | GET    | Scenario evaluation          |
| `/feedback`            | GET    | Retrieve analyst feedback    |
| `/feedback`            | POST   | Submit analyst feedback      |

---

## 📁 Project Structure

```text
CyberSentinel-AI/
│
├── backend/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
│
├── src/
│   ├── train_multiclass.py
│   ├── predict.py
│   ├── evaluate_model.py
│   ├── evaluation_visualization.py
│   └── scenario_evaluation.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   └── evaluation/
│
├── notebooks/
│
├── tests/
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Aryankumavat69/CyberSentinel-AI.git
cd CyberSentinel-AI
```

Create and activate the Python environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install Python dependencies:

```powershell
pip install numpy pandas matplotlib seaborn scikit-learn xgboost jupyter shap fastapi uvicorn requests joblib
```

Install frontend dependencies:

```powershell
cd frontend
npm install
```

---

## ▶️ Running the Project

### Start Backend

From the project root:

```powershell
.venv\Scripts\activate
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start Frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm run dev
```

Dashboard:

```text
http://localhost:5173
```

---

## 🔐 Security & Educational Purpose

CyberSentinel-AI is designed for **defensive cybersecurity education, network monitoring, and machine-learning experimentation**.

It does not provide functionality for unauthorized access, credential theft, malware deployment, or offensive exploitation.

---

## 📌 Future Improvements

* Real-time network-flow ingestion
* Streaming threat detection
* Improved rare-class detection
* Temporal/group-based evaluation
* Model comparison
* Alert notifications
* Authentication and role-based access
* Cloud deployment
* Security event logging
* Automated model retraining using validated analyst feedback

---

## 👨‍💻 Author

**Aryan Kumavat**

AI & Data Science Student

Focused on:

`Artificial Intelligence • Data Science • Machine Learning • Cybersecurity • Cloud`

---

⭐ If you find this project useful, consider giving the repository a star!

import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const SCENARIOS = [
  { value: "benign", label: "Benign Traffic" },
  { value: "ddos", label: "DDoS" },
  { value: "portscan", label: "Port Scan" },
  { value: "webattack", label: "Web Attack" },
  { value: "infiltration", label: "Infiltration" },
  { value: "dos", label: "DoS" },
  { value: "bot", label: "Bot" },
  { value: "ssh_ftp", label: "SSH / FTP" },
];

function App() {
  const [scenario, setScenario] = useState("benign");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [history, setHistory] = useState([]);
  const [feedbackCount, setFeedbackCount] = useState(0);

  useEffect(() => {
    loadFeedback();
  }, []);

  const loadFeedback = async () => {
    try {
      const response = await fetch(
        `${API_URL}/feedback`
      );

      if (!response.ok) return;

      const data = await response.json();

      setFeedbackCount(
        data.total_feedback || 0
      );
    } catch (error) {
      console.error(
        "Feedback loading error:",
        error
      );
    }
  };

  const analyzeTraffic = async () => {
    setLoading(true);
    setResult(null);
    setFeedbackStatus("");

    try {
      const sampleResponse = await fetch(
        `${API_URL}/sample/${scenario}`
      );

      if (!sampleResponse.ok) {
        throw new Error(
          "Unable to load traffic sample."
        );
      }

      const sample =
        await sampleResponse.json();

      const predictionResponse =
        await fetch(
          `${API_URL}/predict`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              data: [sample.data],
            }),
          }
        );

      if (!predictionResponse.ok) {
        throw new Error(
          "Prediction request failed."
        );
      }

      const predictionData =
        await predictionResponse.json();

      const analysis =
        predictionData.result;

      setResult(analysis);

      const historyItem = {
        id: Date.now(),
        scenario,
        prediction:
          analysis.prediction,
        severity:
          analysis.severity,
        risk_score:
          analysis.risk_score,
      };

      setHistory(
        (previous) =>
          [
            historyItem,
            ...previous,
          ].slice(0, 12)
      );
    } catch (error) {
      console.error(error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (
    feedback
  ) => {
    if (!result) return;

    setFeedbackStatus(
      "Submitting..."
    );

    try {
      const response =
        await fetch(
          `${API_URL}/feedback`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              prediction:
                result.prediction,
              severity:
                result.severity,
              risk_score:
                result.risk_score,
              feedback,
              comment:
                `Scenario: ${scenario}`,
            }),
          }
        );

      if (!response.ok) {
        throw new Error(
          "Failed to submit feedback."
        );
      }

      setFeedbackStatus(
        `✓ ${feedback} recorded`
      );

      setFeedbackCount(
        (count) => count + 1
      );
    } catch (error) {
      console.error(error);

      setFeedbackStatus(
        "Failed to submit feedback"
      );
    }
  };

  const getSeverityClass = (
    severity
  ) => {
    switch (severity) {
      case "CRITICAL":
        return "text-red-400 bg-red-500/10 border-red-500/30";

      case "HIGH":
        return "text-orange-400 bg-orange-500/10 border-orange-500/30";

      case "MEDIUM":
        return "text-yellow-400 bg-yellow-500/10 border-yellow-500/30";

      default:
        return "text-green-400 bg-green-500/10 border-green-500/30";
    }
  };

  const getPredictionClass = (
    prediction
  ) => {
    return prediction === "BENIGN"
      ? "text-green-400"
      : "text-red-400";
  };

  const threatsDetected =
    history.filter(
      (item) =>
        item.prediction !==
        "BENIGN"
    ).length;

  const benignTraffic =
    history.filter(
      (item) =>
        item.prediction ===
        "BENIGN"
    ).length;

  const highRiskEvents =
    history.filter(
      (item) =>
        item.severity === "HIGH" ||
        item.severity ===
          "CRITICAL"
    ).length;

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* HEADER */}
      <header className="border-b border-slate-800 bg-slate-950/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">

          <div>
            <h1 className="text-2xl font-bold">
              🛡️ CyberSentinel AI
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Intelligent Network Threat Detection Platform
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-4 py-2 text-sm text-green-400">
            <span className="h-2 w-2 rounded-full bg-green-400"></span>
            System Online
          </div>

        </div>
      </header>


      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">

        {/* CONTROL */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-xl font-semibold">
            Network Traffic Analysis
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Select a traffic scenario and run the AI threat detector.
          </p>

          <div className="mt-6 flex flex-col gap-4 md:flex-row">

            <select
              value={scenario}
              onChange={(event) =>
                setScenario(
                  event.target.value
                )
              }
              className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none focus:border-cyan-500"
            >
              {SCENARIOS.map(
                (item) => (
                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>
                )
              )}
            </select>

            <button
              onClick={
                analyzeTraffic
              }
              disabled={loading}
              className="rounded-xl bg-cyan-600 px-6 py-3 font-semibold hover:bg-cyan-500 disabled:opacity-50"
            >
              {loading
                ? "Analyzing..."
                : "🔍 Analyze Traffic"}
            </button>

          </div>

        </section>


        {/* RESULT */}
        {result && (
          <section className="grid gap-6 lg:grid-cols-3">

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <p className="text-sm text-slate-400">
                Threat Classification
              </p>

              <h2
                className={`mt-3 text-3xl font-bold ${getPredictionClass(
                  result.prediction
                )}`}
              >
                {result.prediction}
              </h2>

              <div
                className={`mt-5 inline-block rounded-full border px-4 py-2 text-sm font-semibold ${getSeverityClass(
                  result.severity
                )}`}
              >
                {result.severity}
              </div>

            </div>


            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <p className="text-sm text-slate-400">
                Risk Score
              </p>

              <div className="mt-3 flex items-end gap-2">

                <span className="text-4xl font-bold">
                  {result.risk_score}
                </span>

                <span className="mb-1 text-slate-400">
                  / 100
                </span>

              </div>

              <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">

                <div
                  className="h-full rounded-full bg-cyan-500"
                  style={{
                    width: `${Math.min(
                      result.risk_score,
                      100
                    )}%`,
                  }}
                />

              </div>

            </div>


            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <p className="text-sm text-slate-400">
                Benign Probability
              </p>

              <p className="mt-3 text-4xl font-bold text-green-400">
                {result.benign_probability}%
              </p>

              <p className="mt-3 text-sm text-slate-500">
                Multiclass Random Forest
              </p>

            </div>

          </section>
        )}


        {/* CLASS PROBABILITIES */}
        {result?.class_probabilities && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

            <h2 className="text-xl font-semibold">
              Class Probabilities
            </h2>

            <div className="mt-6 space-y-4">

              {Object.entries(
                result.class_probabilities
              ).map(
                ([name, probability]) => (

                  <div key={name}>

                    <div className="mb-1 flex justify-between text-sm">

                      <span className="text-slate-300">
                        {name}
                      </span>

                      <span className="text-slate-400">
                        {probability}%
                      </span>

                    </div>

                    <div className="h-2 rounded-full bg-slate-800">

                      <div
                        className="h-2 rounded-full bg-cyan-500"
                        style={{
                          width: `${probability}%`,
                        }}
                      />

                    </div>

                  </div>
                )
              )}

            </div>

          </section>
        )}


        {/* SHAP */}
        {result?.top_features && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

            <h2 className="text-xl font-semibold">
              Explainable AI — SHAP
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Features contributing most strongly to this prediction.
            </p>

            <div className="mt-6 grid gap-3 md:grid-cols-2">

              {result.top_features.map(
                (feature, index) => (

                  <div
                    key={feature.feature}
                    className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950 p-4"
                  >

                    <div className="flex items-center gap-3">

                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-800 text-xs">
                        {index + 1}
                      </span>

                      <span className="text-sm text-slate-300">
                        {feature.feature}
                      </span>

                    </div>

                    <span
                      className={
                        feature.impact >= 0
                          ? "text-red-400"
                          : "text-green-400"
                      }
                    >
                      {feature.impact > 0
                        ? "+"
                        : ""}
                      {feature.impact}
                    </span>

                  </div>
                )
              )}

            </div>

          </section>
        )}


        {/* FEEDBACK */}
        {result && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

            <h2 className="text-xl font-semibold">
              👨‍💻 Analyst Feedback
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Review and label the AI prediction.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">

              <button
                onClick={() =>
                  submitFeedback(
                    "Confirmed Threat"
                  )
                }
                className="rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-3 text-red-400 hover:bg-red-500/20"
              >
                🚨 Confirmed Threat
              </button>

              <button
                onClick={() =>
                  submitFeedback(
                    "False Positive"
                  )
                }
                className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 px-5 py-3 text-yellow-400 hover:bg-yellow-500/20"
              >
                ⚠️ False Positive
              </button>

              <button
                onClick={() =>
                  submitFeedback(
                    "Needs Review"
                  )
                }
                className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-5 py-3 text-cyan-400 hover:bg-cyan-500/20"
              >
                🔍 Needs Review
              </button>

            </div>

            {feedbackStatus && (
              <p className="mt-4 text-sm text-green-400">
                {feedbackStatus}
              </p>
            )}

          </section>
        )}


        {/* STATISTICS */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Total Analyses
            </p>

            <p className="mt-2 text-3xl font-bold">
              {history.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Threats Detected
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {threatsDetected}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Benign Traffic
            </p>

            <p className="mt-2 text-3xl font-bold text-green-400">
              {benignTraffic}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              High Risk Events
            </p>

            <p className="mt-2 text-3xl font-bold text-orange-400">
              {highRiskEvents}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Analyst Feedback
            </p>

            <p className="mt-2 text-3xl font-bold text-cyan-400">
              {feedbackCount}
            </p>
          </div>

        </section>


        {/* HISTORY */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-xl font-semibold">
            Detection History
          </h2>

          {history.length === 0 ? (

            <div className="mt-6 rounded-xl border border-dashed border-slate-800 p-8 text-center text-slate-500">
              No analyses performed yet.
            </div>

          ) : (

            <div className="mt-6 overflow-x-auto">

              <table className="w-full text-left text-sm">

                <thead className="border-b border-slate-800 text-slate-500">

                  <tr>
                    <th className="px-4 py-3">
                      Scenario
                    </th>

                    <th className="px-4 py-3">
                      Prediction
                    </th>

                    <th className="px-4 py-3">
                      Severity
                    </th>

                    <th className="px-4 py-3">
                      Risk
                    </th>
                  </tr>

                </thead>

                <tbody>

                  {history.map(
                    (item) => (

                      <tr
                        key={item.id}
                        className="border-b border-slate-800/70"
                      >

                        <td className="px-4 py-3 text-slate-300">
                          {item.scenario}
                        </td>

                        <td
                          className={`px-4 py-3 font-medium ${getPredictionClass(
                            item.prediction
                          )}`}
                        >
                          {item.prediction}
                        </td>

                        <td className="px-4 py-3">
                          {item.severity}
                        </td>

                        <td className="px-4 py-3">
                          {item.risk_score}
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </section>


        {/* SYSTEM STATUS */}
        <section className="grid gap-4 md:grid-cols-3">

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">

            <p className="text-sm text-slate-400">
              AI Engine
            </p>

            <p className="mt-2 font-semibold">
              Multiclass Random Forest
            </p>

            <p className="mt-1 text-xs text-green-400">
              ● Operational
            </p>

          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">

            <p className="text-sm text-slate-400">
              Explainability
            </p>

            <p className="mt-2 font-semibold">
              SHAP TreeExplainer
            </p>

            <p className="mt-1 text-xs text-green-400">
              ● Operational
            </p>

          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">

            <p className="text-sm text-slate-400">
              Feedback Pipeline
            </p>

            <p className="mt-2 font-semibold">
              Persistent Analyst Feedback
            </p>

            <p className="mt-1 text-xs text-green-400">
              ● Operational
            </p>

          </div>

        </section>

      </main>


      <footer className="border-t border-slate-800 py-6 text-center text-sm text-slate-500">
        CyberSentinel AI • AI-Powered Network Threat Detection
      </footer>

    </div>
  );
}

export default App;
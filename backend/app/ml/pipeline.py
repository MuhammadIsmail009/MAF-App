from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.ml.features import processes_to_dataframe


class SimpleAnomalyModel:
    """
    Lightweight wrapper that uses a RandomForestClassifier trained on synthetic
    data plus a heuristic anomaly score.
    """

    def __init__(self) -> None:
        # Train a tiny RF on synthetic samples so predict_proba works.
        X = np.array(
            [
                [0, 0, 0, 0.1, 0],  # benign
                [3, 20, 1, 0.95, 5],  # malicious
                [1, 5, 0, 0.3, 0],  # benign
                [4, 30, 1, 0.9, 10],  # malicious
            ]
        )
        y = np.array([0, 1, 0, 1])  # 1 = malicious
        self.model = RandomForestClassifier(n_estimators=20, random_state=42)
        self.model.fit(X, y)

    def _vectorize_row(self, row) -> np.ndarray:
        return np.array(
            [
                float(row["threads"]),
                float(row["dll_count"]),
                float(row["suspicious_flag"]),
                float(row["entropy"]),
                float(row["net_conn_count"]),
            ]
        )

    def predict_processes(self, processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = processes_to_dataframe(processes)
        predictions: List[Dict[str, Any]] = []
        if df.empty:
            return predictions

        vectors = np.stack([self._vectorize_row(r) for _, r in df.iterrows()], axis=0)
        probs = self.model.predict_proba(vectors)[:, 1]  # probability malicious

        for (idx, row), prob in zip(df.iterrows(), probs):
            # Heuristic anomaly score combining entropy, suspicious flag, and RF prob
            entropy = float(row["entropy"])
            susp = float(row["suspicious_flag"])
            net = float(row["net_conn_count"])
            anomaly_score = min(
                1.0,
                0.4 * prob + 0.3 * entropy + 0.2 * susp + 0.1 * (1.0 if net > 0 else 0.0),
            )
            label = "malicious" if anomaly_score > 0.7 or prob > 0.6 else "benign"

            predictions.append(
                {
                    "pid": int(row["pid"]),
                    "ppid": int(row["ppid"]),
                    "name": str(row["name"]),
                    "anomaly_score": float(anomaly_score),
                    "confidence": float(prob),
                    "label": label,
                    "features": row.to_dict(),
                }
            )

        return predictions


model = SimpleAnomalyModel()


def run_ml_pipeline(volatility_output: Dict[str, Any]) -> Dict[str, Any]:
    processes = volatility_output.get("pslist") or []
    proc_predictions = model.predict_processes(processes)

    max_anomaly = max((p["anomaly_score"] for p in proc_predictions), default=0.0)
    any_malicious = any(p["label"] == "malicious" for p in proc_predictions)

    return {
        "processes": proc_predictions,
        "max_anomaly_score": max_anomaly,
        "any_malicious": any_malicious,
    }




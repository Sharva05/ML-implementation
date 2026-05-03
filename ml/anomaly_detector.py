import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from common.config import ML_CONFIG


class AnomalyDetector:
    """
    Detect anomalies using Isolation Forest + Z-score hybrid scoring.
    """

    def __init__(self):
        self.model = IsolationForest(
            contamination=ML_CONFIG["contamination"],
            random_state=42
        )

    def fit(self, X):
        """Train Isolation Forest"""
        self.model.fit(X)

    def compute_zscore(self, X):
        """Compute z-score for each feature"""
        return (X - X.mean()) / X.std()

    def predict(self, df):
        """
        Input: DataFrame with features
        Output: anomaly_df with required schema
        """

        X = df.drop(columns=["log_id"])

        # Isolation score
        isolation_scores = self.model.decision_function(X)

        # Z-score
        zscores = self.compute_zscore(X)
        zscore_values = np.abs(zscores).mean(axis=1)

        # Hybrid score
        w1 = ML_CONFIG["weight_isolation"]
        w2 = ML_CONFIG["weight_zscore"]

        combined_score = w1 * isolation_scores + w2 * zscore_values

        # Anomaly flag
        is_anomaly = self.model.predict(X) == -1

        anomaly_df = pd.DataFrame({
            "log_id": df["log_id"],
            "isolation_score": isolation_scores,
            "zscore": zscore_values,
            "combined_score": combined_score,
            "is_anomaly": is_anomaly
        })

        return anomaly_df
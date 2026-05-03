import os
import joblib
from datetime import datetime
import pandas as pd

from ml.anomaly_detector import AnomalyDetector
from common.config import ML_CONFIG


class Trainer:
    """
    Handles training, saving, and (optionally) loading of ML models.

    Design Notes:
    - Uses sliding window training (Phase 2 extension)
    - Saves versioned models for reproducibility
    - Keeps model lifecycle separate from detection logic
    """

    def __init__(self):
        self.detector = AnomalyDetector()

    def train(self, df: pd.DataFrame):
        """
        Train model using input DataFrame.

        Current:
        - Uses full dataset

        Future (Phase 2):
        - Apply sliding window on last N sessions
        """

        # Remove non-feature columns
        X = df.drop(columns=["log_id"], errors="ignore")

        # Train model
        self.detector.fit(X)

    def save_model(self) -> str:
        """
        Save trained model to disk with versioning.
        """

        # Ensure directory exists
        model_dir = "ml/model_store"
        os.makedirs(model_dir, exist_ok=True)

        # Generate timestamp version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # File path
        path = os.path.join(
            model_dir,
            f"isolation_forest_v{timestamp}.pkl"
        )

        # Save model
        joblib.dump(self.detector.model, path)

        return path

    def load_model(self, path: str):
        """
        Load a saved model from disk.
        """

        self.detector.model = joblib.load(path)
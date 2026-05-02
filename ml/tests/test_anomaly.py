import pandas as pd
from ml.anomaly_detector import AnomalyDetector


def test_anomaly_output_schema():
    df = pd.DataFrame({
        "log_id": [1, 2, 3],
        "feature1": [10, 20, 30],
        "feature2": [1, 2, 100]
    })

    detector = AnomalyDetector()
    detector.fit(df.drop(columns=["log_id"]))

    result = detector.predict(df)

    expected_cols = [
        "log_id",
        "isolation_score",
        "zscore",
        "combined_score",
        "is_anomaly"
    ]

    assert all(col in result.columns for col in expected_cols)
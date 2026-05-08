import pandas as pd

from statistical_features import (
    log_frequency_score,
    burstiness_score,
    zscore_base
)

from temporal_features import (
    add_temporal_features
)

from severity_features import (
    add_severity_weight
)

from counter_proximity import (
    add_counter_proximity
)

from common.config import (
    SESSIONIZED_LOGS_PATH,
    FEATURES_OUTPUT_PATH,
    FEATURE_COLUMNS
)


def build_features(input_path):

    df = pd.read_parquet(input_path)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = log_frequency_score(df)

    df = burstiness_score(df)

    df = zscore_base(df)

    df = add_temporal_features(df)

    df = add_severity_weight(df)

    df = add_counter_proximity(df)

    features_df = df[FEATURE_COLUMNS]

    return features_df


if __name__ == "__main__":

    features = build_features(
        SESSIONIZED_LOGS_PATH
    )

    print(features.head())

    features.to_parquet(
        FEATURES_OUTPUT_PATH,
        index=False
    )

    print("features saved")
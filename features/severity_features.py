from common.config import (
    SEVERITY_WEIGHTS,
    DEFAULT_SEVERITY_WEIGHT
)


def add_severity_weight(df):

    df["severity_weight"] = (
        df["log_level"]
        .map(SEVERITY_WEIGHTS)
        .fillna(DEFAULT_SEVERITY_WEIGHT)
    )

    return df
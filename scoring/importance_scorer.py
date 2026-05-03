"""
Importance Scorer

Combines ML, graph, and rule-based signals
"""

import pandas as pd
from common.config import ML_WEIGHT, GRAPH_WEIGHT, RULE_WEIGHT


def compute_importance_score(anomaly_df, graph_scores_df, features_df):
    """
    Expected Inputs:
        anomaly_df: columns -> [log_id, anomaly_score]
        graph_scores_df: columns -> [log_id, graph_score]
        features_df: columns -> [log_id, rule_score]

    Output:
        scored_logs_df: DataFrame with final_score
    """

    # TODO: merge all dataframes on log_id
    # TODO: compute final_score using weights

    pass
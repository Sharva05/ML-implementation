"""
Label Mapper

Maps score → label
"""

from common.config import LABEL_THRESHOLDS


def map_score_to_label(score: float) -> str:
    for label, (low, high) in LABEL_THRESHOLDS.items():
        if low <= score < high:
            return label
    return "critical"
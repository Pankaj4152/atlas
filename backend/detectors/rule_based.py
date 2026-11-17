"""
Rule-Based Anomaly Detector.
Traditional baseline detector using predefined operational thresholds.
"""

from typing import List, Dict
import pandas as pd


class RuleBasedDetector:
    """
    Flags windows as anomalies based on deterministic thresholds:
    1. Presence of any CRITICAL level logs.
    2. Error count exceeding error_threshold.
    3. Error ratio exceeding error_ratio_threshold.
    """

    def __init__(
        self,
        error_threshold: int = 5,
        error_ratio_threshold: float = 0.30,
        critical_threshold: int = 1
    ):
        self.error_threshold = error_threshold
        self.error_ratio_threshold = error_ratio_threshold
        self.critical_threshold = critical_threshold

    def detect(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Input: feature_df produced by feature_extraction.
        Output: Copy of DataFrame with added columns:
        - 'rule_anomaly': bool (True if anomalous)
        - 'rule_reason': explanation string
        """
        if feature_df.empty:
            return feature_df

        df = feature_df.copy()
        is_anomaly: List[bool] = []
        reasons: List[str] = []

        for _, row in df.iterrows():
            triggers = []
            if row.get("critical_count", 0) >= self.critical_threshold:
                triggers.append(f"Critical errors observed ({int(row['critical_count'])})")
            if row.get("error_count", 0) >= self.error_threshold:
                triggers.append(f"High error count ({int(row['error_count'])})")
            if row.get("error_ratio", 0) >= self.error_ratio_threshold and row.get("total_logs", 0) >= 3:
                triggers.append(f"High error ratio ({row['error_ratio']:.1%})")

            if triggers:
                is_anomaly.append(True)
                reasons.append("; ".join(triggers))
            else:
                is_anomaly.append(False)
                reasons.append("")

        df["rule_anomaly"] = is_anomaly
        df["rule_reason"] = reasons
        return df

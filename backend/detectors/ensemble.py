"""
Ensemble Anomaly Detector.
Combines Rule-based, Z-Score, and Isolation Forest detections.
Assigns severity levels (LOW, MEDIUM, HIGH, CRITICAL).
"""

from typing import List, Dict, Any
import pandas as pd
from backend.detectors.rule_based import RuleBasedDetector
from backend.detectors.zscore import ZScoreDetector
from backend.detectors.isolation_forest import IsolationForestDetector


class EnsembleDetector:
    """
    Ensemble detection pipeline:
    - Runs RuleBasedDetector, ZScoreDetector, and IsolationForestDetector.
    - Votes across models and computes an ensemble agreement score.
    - Anomaly Decision Policy:
        - Strict Anomaly (is_anomaly=True): When at least 2 models agree (majority/consensus),
          OR when critical errors are explicitly observed.
        - Single detector flags without consensus are treated as MEDIUM/LOW warning signals.
    """

    def __init__(
        self,
        rule_detector: RuleBasedDetector = None,
        zscore_detector: ZScoreDetector = None,
        iforest_detector: IsolationForestDetector = None,
    ):
        self.rule_detector = rule_detector or RuleBasedDetector()
        self.zscore_detector = zscore_detector or ZScoreDetector()
        self.iforest_detector = iforest_detector or IsolationForestDetector()

    def detect(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs all detectors and merges outputs into a unified verdict.
        Adds columns:
        - is_anomaly (bool)
        - severity (CRITICAL, HIGH, MEDIUM, LOW, NORMAL)
        - detector_votes (int: 0 to 3)
        - anomaly_summary (str)
        """
        if feature_df.empty:
            return feature_df

        df = feature_df.copy()
        df = self.rule_detector.detect(df)
        df = self.zscore_detector.detect(df)
        df = self.iforest_detector.detect(df)

        is_anomalies: List[bool] = []
        severities: List[str] = []
        vote_counts: List[int] = []
        summaries: List[str] = []

        for _, row in df.iterrows():
            r_vote = bool(row.get("rule_anomaly", False))
            z_vote = bool(row.get("zscore_anomaly", False))
            i_vote = bool(row.get("iforest_anomaly", False))
            votes = sum([r_vote, z_vote, i_vote])

            # Determine severity & verified consensus anomaly
            crit_count = row.get("critical_count", 0)
            err_count = row.get("error_count", 0)

            if crit_count > 0:
                severity = "CRITICAL"
                is_anom = True
            elif votes >= 2:
                severity = "HIGH" if err_count >= 8 else "MEDIUM"
                is_anom = True
            elif votes == 1:
                severity = "LOW"
                is_anom = False  # Noise suppression: single detector flag without corroboration
            elif err_count > 0:
                severity = "LOW"
                is_anom = False
            else:
                severity = "NORMAL"
                is_anom = False

            # Compile consolidated summary
            active_reasons = []
            if row.get("rule_reason"):
                active_reasons.append(f"[Rule] {row['rule_reason']}")
            if row.get("zscore_reason"):
                active_reasons.append(f"[Z-Score] {row['zscore_reason']}")
            if row.get("iforest_reason"):
                active_reasons.append(f"[IsolationForest] {row['iforest_reason']}")

            is_anomalies.append(is_anom)
            severities.append(severity)
            vote_counts.append(votes)
            summaries.append(" | ".join(active_reasons) if active_reasons else "Normal operations")

        df["is_anomaly"] = is_anomalies
        df["severity"] = severities
        df["detector_votes"] = vote_counts
        df["anomaly_summary"] = summaries

        return df

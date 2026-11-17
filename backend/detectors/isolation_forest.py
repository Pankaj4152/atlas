"""
Isolation Forest Machine Learning Anomaly Detector.
Unsupervised multidimensional anomaly detection on engineered features.
"""

from typing import Optional, List
import pandas as pd
from sklearn.ensemble import IsolationForest
from backend.pipeline.feature_extraction import get_feature_matrix


class IsolationForestDetector:
    """
    Isolation Forest identifies anomalies by isolating outliers in feature space.
    - Fits an unsupervised forest on extracted numerical features.
    - Handles multivariate patterns (e.g. moderate error count combined with high rare events and sudden volume spike).
    """

    def __init__(
        self,
        contamination: float = 0.10,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None

    def detect(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Input: feature_df produced by feature_extraction.
        Output: Copy of DataFrame with added columns:
        - 'iforest_anomaly': bool (True if anomalous)
        - 'iforest_score': float (continuous anomaly score, lower/negative indicates anomaly)
        - 'iforest_reason': str
        """
        if feature_df.empty:
            return feature_df

        df = feature_df.copy()
        X = get_feature_matrix(df)

        n_samples = len(X)
        if n_samples < 2:
            df["iforest_anomaly"] = False
            df["iforest_score"] = 0.0
            df["iforest_reason"] = "Insufficient samples to train Isolation Forest (< 2 windows)"
            return df

        # Dynamic contamination adjustment if dataset has very few windows
        eff_contamination = min(self.contamination, max(1.0 / n_samples, 0.01))

        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=eff_contamination,
            random_state=self.random_state
        )
        self.model.fit(X)

        # IsolationForest: 1 for normal, -1 for anomaly
        preds = self.model.predict(X)
        scores = self.model.decision_function(X)

        df["iforest_anomaly"] = preds == -1
        df["iforest_score"] = scores.round(4)

        reasons: List[str] = []
        for i, is_anom in enumerate(df["iforest_anomaly"]):
            if is_anom:
                reasons.append(f"Multivariate feature anomaly (score={scores[i]:.3f})")
            else:
                reasons.append("")

        df["iforest_reason"] = reasons
        return df

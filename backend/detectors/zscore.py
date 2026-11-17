"""
Z-Score Statistical Anomaly Detector.
Detects statistical deviations in error frequency and log volume.
Formula: Z = (x - mean) / std
"""

from typing import List
import numpy as np
import pandas as pd


class ZScoreDetector:
    """
    Statistical baseline detector:
    Calculates Z-scores across key metric columns.
    A window is flagged if the absolute Z-score of any target metric exceeds z_threshold.
    """

    def __init__(
        self,
        z_threshold: float = 2.5,
        target_columns: List[str] = None
    ):
        self.z_threshold = z_threshold
        self.target_columns = target_columns or ["error_count", "critical_count", "total_logs"]

    def detect(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Input: feature_df produced by feature_extraction.
        Output: Copy of DataFrame with added columns:
        - 'zscore_anomaly': bool
        - 'max_zscore': float
        - 'zscore_reason': str
        """
        if feature_df.empty:
            return feature_df

        df = feature_df.copy()
        n_samples = len(df)

        # If too few samples to compute standard deviation reliably, return neutral
        if n_samples < 3:
            df["zscore_anomaly"] = False
            df["max_zscore"] = 0.0
            df["zscore_reason"] = "Insufficient data points for statistical analysis (< 3 windows)"
            return df

        anomalies: List[bool] = []
        max_scores: List[float] = []
        reasons: List[str] = []

        # Compute z-scores for each target column
        z_matrices = {}
        for col in self.target_columns:
            if col in df.columns:
                values = df[col].values.astype(float)
                mean = np.mean(values)
                std = np.std(values)
                # Avoid division by zero when standard deviation is zero
                if std > 1e-6:
                    z_matrices[col] = (values - mean) / std
                else:
                    z_matrices[col] = np.zeros_like(values)

        for i in range(n_samples):
            max_z = 0.0
            trigger_reasons = []

            for col, z_vals in z_matrices.items():
                z = float(z_vals[i])
                if abs(z) > abs(max_z):
                    max_z = z
                if z >= self.z_threshold:
                    val = df[col].iloc[i]
                    trigger_reasons.append(f"{col} spike (Z={z:.2f}, val={val})")

            is_anom = len(trigger_reasons) > 0
            anomalies.append(is_anom)
            max_scores.append(round(max_z, 2))
            reasons.append("; ".join(trigger_reasons) if trigger_reasons else "")

        df["zscore_anomaly"] = anomalies
        df["max_zscore"] = max_scores
        df["zscore_reason"] = reasons
        return df

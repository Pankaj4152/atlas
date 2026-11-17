"""
Time-window feature extraction.
Aggregates parsed, templated logs into time windows (e.g. 1 minute)
and generates numerical feature vectors for anomaly detection.
"""

from typing import Optional
import numpy as np
import pandas as pd


def extract_window_features(
    df: pd.DataFrame,
    window_size: str = "1min"
) -> pd.DataFrame:
    """
    Groups preprocessed logs into fixed time windows and calculates numerical features:
    - total_logs: Count of log events in the window
    - error_count: ERROR severity count
    - warning_count: WARNING severity count
    - critical_count: CRITICAL severity count
    - error_ratio: (errors + criticals) / total_logs
    - unique_events: Number of distinct Drain3 event templates
    - rare_events: Number of rare template occurrences
    - volume_change: Ratio of current total_logs to previous window (spike velocity)

    Returns:
    DataFrame indexed by window timestamp with numerical feature columns.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Ensure required columns exist
    for col in ["level", "event_id", "is_rare_event"]:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' missing from preprocessed DataFrame.")

    # Prepare boolean indicators for aggregation
    df["is_error"] = (df["level"] == "ERROR").astype(int)
    df["is_warning"] = (df["level"] == "WARNING").astype(int)
    df["is_critical"] = (df["level"] == "CRITICAL").astype(int)
    df["rare_int"] = df["is_rare_event"].astype(int)

    # Set timestamp as index for resample
    df = df.set_index("timestamp").sort_index()

    # Aggregate by time window
    resampler = df.resample(window_size)
    
    agg_df = pd.DataFrame({
        "total_logs": resampler["message"].count(),
        "error_count": resampler["is_error"].sum(),
        "warning_count": resampler["is_warning"].sum(),
        "critical_count": resampler["is_critical"].sum(),
        "unique_events": resampler["event_id"].nunique(),
        "rare_events": resampler["rare_int"].sum(),
    })

    # Filter out empty windows that have zero logs (only keep active periods)
    agg_df = agg_df[agg_df["total_logs"] > 0].copy()

    if agg_df.empty:
        return agg_df

    # Derived features
    # 1. Error ratio: (error + critical) / total
    agg_df["error_ratio"] = (agg_df["error_count"] + agg_df["critical_count"]) / agg_df["total_logs"]

    # 2. Volume change: ratio compared to previous window (1.0 = steady, > 2.0 = spike)
    prev_volume = agg_df["total_logs"].shift(1).fillna(agg_df["total_logs"].iloc[0])
    # Avoid division by zero
    prev_volume = prev_volume.replace(0, 1)
    agg_df["volume_change"] = (agg_df["total_logs"] / prev_volume).round(2)

    # Round floats
    agg_df["error_ratio"] = agg_df["error_ratio"].round(4)

    # Reset index to have 'window_start' as a clean column
    agg_df = agg_df.reset_index().rename(columns={"timestamp": "window_start"})

    return agg_df


def get_feature_matrix(feature_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract only the numerical feature columns intended for ML models.
    """
    feature_cols = [
        "total_logs",
        "error_count",
        "warning_count",
        "critical_count",
        "error_ratio",
        "unique_events",
        "rare_events",
        "volume_change",
    ]
    return feature_df[feature_cols].copy()

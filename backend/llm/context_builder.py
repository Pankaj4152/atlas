"""
Context builder for LLM analysis.
Extracts anomalous time windows, filters relevant raw logs, and builds
structured payloads for LLM root-cause analysis.
"""

from typing import List
import pandas as pd
from backend.llm.schemas import AnomalyContext


def build_anomaly_contexts(
    df_raw: pd.DataFrame,
    detected_df: pd.DataFrame,
    max_sample_logs: int = 15
) -> List[AnomalyContext]:
    """
    Takes the parsed raw logs and the ensemble detector results.
    For each anomalous window, compiles an AnomalyContext object.
    """
    contexts: List[AnomalyContext] = []

    if detected_df.empty or "is_anomaly" not in detected_df.columns:
        return contexts

    anomaly_windows = detected_df[detected_df["is_anomaly"]].copy()

    for idx, row in anomaly_windows.iterrows():
        win_start = pd.to_datetime(row["window_start"])
        # Standard window is 1 minute
        win_end = win_start + pd.Timedelta(minutes=1)

        # Slice relevant raw logs within this window
        mask = (df_raw["timestamp"] >= win_start) & (df_raw["timestamp"] < win_end)
        window_logs = df_raw[mask].copy()

        # Prioritize ERROR and CRITICAL logs for LLM context
        severe_logs = window_logs[window_logs["level"].isin(["CRITICAL", "ERROR", "WARNING"])]
        if not severe_logs.empty:
            sample_logs = severe_logs["raw"].head(max_sample_logs).tolist()
        else:
            sample_logs = window_logs["raw"].head(max_sample_logs).tolist()

        # Extract top templates if available
        top_templates = []
        if "template" in window_logs.columns:
            top_templates = window_logs["template"].value_counts().head(5).index.tolist()

        incident_id = f"INC-{len(contexts) + 1:03d}"
        time_str = f"{win_start.strftime('%Y-%m-%d %H:%M:%S')} to {win_end.strftime('%H:%M:%S')}"

        context = AnomalyContext(
            incident_id=incident_id,
            time_window=time_str,
            severity_hint=str(row.get("severity", "HIGH")).lower(),
            total_logs=int(row.get("total_logs", len(window_logs))),
            error_count=int(row.get("error_count", 0)),
            critical_count=int(row.get("critical_count", 0)),
            warning_count=int(row.get("warning_count", 0)),
            detector_summary=str(row.get("anomaly_summary", "")),
            top_templates=top_templates,
            sample_raw_logs=sample_logs,
        )
        contexts.append(context)

    return contexts

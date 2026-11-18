"""
End-to-End Log Analysis Pipeline.
Orchestrates:
1. Parsing raw log file -> DataFrame
2. Template mining with Drain3
3. Time-window feature extraction
4. Ensemble anomaly detection (Rule + Z-score + Isolation Forest)
5. LLM-based root-cause diagnosis for flagged incidents
6. Exporting complete, structured analysis report (JSON & Python dict)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import pandas as pd

from backend.pipeline.parser import parse_log_file
from backend.pipeline.preprocessing import LogTemplateExtractor
from backend.pipeline.feature_extraction import extract_window_features
from backend.detectors.ensemble import EnsembleDetector
from backend.llm.context_builder import build_anomaly_contexts
from backend.llm.client import LLMAnalyzer


class LogAnalysisPipeline:
    """Complete log analysis orchestrator."""

    def __init__(
        self,
        window_size: str = "1min",
        rare_threshold: float = 0.05,
        llm_provider: Optional[str] = None,
        llm_api_key: Optional[str] = None,
    ):
        self.window_size = window_size
        self.extractor = LogTemplateExtractor(rare_threshold=rare_threshold)
        self.detector = EnsembleDetector()
        self.llm_analyzer = LLMAnalyzer(provider=llm_provider, api_key=llm_api_key)

    def analyze_file(
        self,
        file_path: Union[str, Path],
        output_json_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Run end-to-end analysis on an uploaded log file.
        Returns complete analysis report dictionary and optionally saves to JSON.
        """
        path = Path(file_path)
        start_time = datetime.now()

        # Step 1: Parse logs
        df_raw = parse_log_file(path)
        total_logs = len(df_raw)

        if total_logs == 0:
            return {
                "file_info": {
                    "file_name": path.name,
                    "file_size_kb": round(path.stat().st_size / 1024, 2) if path.exists() else 0,
                    "analyzed_at": datetime.now().isoformat(),
                    "duration_seconds": 0.0,
                },
                "summary": {
                    "total_logs": 0,
                    "total_windows": 0,
                    "flagged_windows": 0,
                    "critical_incidents": 0,
                    "total_incidents": 0,
                    "severity_distribution": {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0},
                },
                "incidents": [],
                "timeline": [],
                "top_templates": [],
            }

        # Step 2: Extract templates and flag rare events
        df_templated = self.extractor.fit_transform(df_raw)
        template_catalog = self.extractor.get_template_catalog()

        # Step 3: Extract time-window features
        feature_df = extract_window_features(df_templated, window_size=self.window_size)

        # Step 4: Run ensemble anomaly detection
        detected_df = self.detector.detect(feature_df)

        # Step 5: Compile anomalous contexts and query LLM
        anomaly_contexts = build_anomaly_contexts(df_templated, detected_df)
        incidents = []

        for ctx in anomaly_contexts:
            llm_result = self.llm_analyzer.analyze(ctx)
            incidents.append({
                "incident_id": ctx.incident_id,
                "time_window": ctx.time_window,
                "title": llm_result.title,
                "severity": llm_result.severity,
                "confidence": llm_result.confidence,
                "probable_root_cause": llm_result.probable_root_cause,
                "explanation": llm_result.explanation,
                "recommended_actions": llm_result.recommended_actions,
                "metrics": {
                    "total_logs": ctx.total_logs,
                    "error_count": ctx.error_count,
                    "critical_count": ctx.critical_count,
                    "warning_count": ctx.warning_count,
                },
                "detector_triggers": ctx.detector_summary,
                "sample_logs": ctx.sample_raw_logs,
            })

        # Calculate high-level summary statistics safely
        level_counts = df_raw["level"].value_counts().to_dict()
        flagged_windows_count = int(detected_df["is_anomaly"].sum()) if (not detected_df.empty and "is_anomaly" in detected_df.columns) else 0
        critical_incidents_count = sum(1 for inc in incidents if inc["severity"] == "critical")

        timeline = []
        if not detected_df.empty:
            for _, row in detected_df.iterrows():
                timeline.append({
                    "window": str(row.get("window_start", "")),
                    "total_logs": int(row.get("total_logs", 0)),
                    "errors": int(row.get("error_count", 0)),
                    "criticals": int(row.get("critical_count", 0)),
                    "warnings": int(row.get("warning_count", 0)),
                    "is_anomaly": bool(row.get("is_anomaly", False)),
                    "severity": str(row.get("severity", "NORMAL")),
                })

        duration_sec = round((datetime.now() - start_time).total_seconds(), 2)

        report = {
            "file_info": {
                "file_name": path.name,
                "file_size_kb": round(path.stat().st_size / 1024, 2),
                "analyzed_at": datetime.now().isoformat(),
                "duration_seconds": duration_sec,
            },
            "summary": {
                "total_logs": total_logs,
                "total_windows": len(detected_df),
                "flagged_windows": flagged_windows_count,
                "critical_incidents": critical_incidents_count,
                "total_incidents": len(incidents),
                "severity_distribution": {
                    "CRITICAL": int(level_counts.get("CRITICAL", 0)),
                    "ERROR": int(level_counts.get("ERROR", 0)),
                    "WARNING": int(level_counts.get("WARNING", 0)),
                    "INFO": int(level_counts.get("INFO", 0)),
                    "DEBUG": int(level_counts.get("DEBUG", 0)),
                },
            },
            "incidents": incidents,
            "timeline": timeline,
            "top_templates": template_catalog.head(10).to_dict(orient="records"),
        }

        if output_json_path:
            out_p = Path(output_json_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        return report

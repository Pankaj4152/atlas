import pytest
from pathlib import Path
from backend.pipeline.analyzer import LogAnalysisPipeline


def test_full_pipeline_analysis():
    sample_file = Path("sample_logs/sample_server.log")
    pipeline = LogAnalysisPipeline()
    report = pipeline.analyze_file(sample_file)

    assert "file_info" in report
    assert "summary" in report
    assert "incidents" in report
    assert "timeline" in report
    assert "top_templates" in report

    assert report["summary"]["total_logs"] == 35
    assert report["summary"]["flagged_windows"] >= 1
    assert len(report["incidents"]) >= 1

    incident = report["incidents"][0]
    assert incident["severity"] == "critical"
    assert len(incident["recommended_actions"]) >= 3
    assert len(incident["sample_logs"]) > 0

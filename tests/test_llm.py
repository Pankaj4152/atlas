import pytest
from pathlib import Path
from backend.pipeline.parser import parse_log_file
from backend.pipeline.preprocessing import LogTemplateExtractor
from backend.pipeline.feature_extraction import extract_window_features
from backend.detectors.ensemble import EnsembleDetector
from backend.llm.context_builder import build_anomaly_contexts
from backend.llm.client import LLMAnalyzer
from backend.llm.schemas import AnomalyContext, LLMAnalysisResult


def test_build_anomaly_contexts():
    sample_file = Path("sample_logs/sample_server.log")
    df = parse_log_file(sample_file)
    extractor = LogTemplateExtractor()
    df_processed = extractor.fit_transform(df)
    features = extract_window_features(df_processed, window_size="1min")
    detector = EnsembleDetector()
    detected = detector.detect(features)

    contexts = build_anomaly_contexts(df_processed, detected)

    assert len(contexts) >= 1
    ctx = contexts[0]
    assert isinstance(ctx, AnomalyContext)
    assert ctx.error_count > 0 or ctx.critical_count > 0
    assert len(ctx.sample_raw_logs) > 0


def test_llm_analyzer_fallback():
    ctx = AnomalyContext(
        incident_id="INC-001",
        time_window="2026-11-18 10:03:00 to 10:04:00",
        severity_hint="critical",
        total_logs=13,
        error_count=7,
        critical_count=3,
        warning_count=1,
        detector_summary="Spike in errors and critical logs",
        top_templates=["Connection timeout to database server <*> after <*>"],
        sample_raw_logs=[
            "2026-11-18 10:03:02 ERROR [db] Connection pool exhausted: active=20, max=20, pending=15",
            "2026-11-18 10:03:03 ERROR [api] Connection timeout to database server 10.0.0.5:5432 after 5000ms",
            "2026-11-18 10:03:10 CRITICAL [system] Service worker thread #3 crashed: unhandled DBConnectionError",
        ],
    )

    analyzer = LLMAnalyzer(provider="fallback")
    result = analyzer.analyze(ctx)

    assert isinstance(result, LLMAnalysisResult)
    assert result.severity == "critical"
    assert "Database Connection Pool" in result.title or "Database" in result.title
    assert len(result.recommended_actions) >= 3
    assert result.confidence in ["high", "medium", "low"]

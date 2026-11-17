import pytest
import pandas as pd
from pathlib import Path
from backend.pipeline.parser import parse_log_file
from backend.pipeline.preprocessing import LogTemplateExtractor
from backend.pipeline.feature_extraction import extract_window_features
from backend.detectors.rule_based import RuleBasedDetector
from backend.detectors.zscore import ZScoreDetector
from backend.detectors.isolation_forest import IsolationForestDetector
from backend.detectors.ensemble import EnsembleDetector


@pytest.fixture
def sample_feature_df():
    sample_file = Path("sample_logs/sample_server.log")
    df = parse_log_file(sample_file)
    extractor = LogTemplateExtractor()
    df_processed = extractor.fit_transform(df)
    return extract_window_features(df_processed, window_size="1min")


def test_rule_based_detector(sample_feature_df):
    detector = RuleBasedDetector()
    res = detector.detect(sample_feature_df)
    assert "rule_anomaly" in res.columns
    assert "rule_reason" in res.columns
    
    # 10:03 window has critical errors and should be flagged
    crit_window = res[res["critical_count"] > 0]
    assert crit_window["rule_anomaly"].all()


def test_zscore_detector(sample_feature_df):
    detector = ZScoreDetector(z_threshold=1.5)
    res = detector.detect(sample_feature_df)
    assert "zscore_anomaly" in res.columns
    assert "max_zscore" in res.columns

    # Verify spike is detected
    flagged = res[res["zscore_anomaly"]]
    assert len(flagged) >= 1


def test_isolation_forest_detector(sample_feature_df):
    detector = IsolationForestDetector(contamination=0.2, random_state=42)
    res = detector.detect(sample_feature_df)
    assert "iforest_anomaly" in res.columns
    assert "iforest_score" in res.columns
    # Outlier window should have a lower decision score
    assert res["iforest_score"].min() < 0.0


def test_ensemble_detector(sample_feature_df):
    ensemble = EnsembleDetector()
    res = ensemble.detect(sample_feature_df)
    assert "is_anomaly" in res.columns
    assert "severity" in res.columns
    assert "detector_votes" in res.columns

    # 10:03 window must be classified as CRITICAL
    crit_rows = res[res["critical_count"] > 0]
    assert (crit_rows["severity"] == "CRITICAL").all()
    assert (crit_rows["is_anomaly"] == True).all()

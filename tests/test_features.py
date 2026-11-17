import pytest
import pandas as pd
from pathlib import Path
from backend.pipeline.parser import parse_log_file
from backend.pipeline.preprocessing import LogTemplateExtractor
from backend.pipeline.feature_extraction import extract_window_features, get_feature_matrix


def test_template_extraction():
    sample_file = Path("sample_logs/sample_server.log")
    df = parse_log_file(sample_file)

    extractor = LogTemplateExtractor(rare_threshold=0.1)
    df_processed = extractor.fit_transform(df)

    assert "template" in df_processed.columns
    assert "event_id" in df_processed.columns
    assert "is_rare_event" in df_processed.columns

    # Verify that similar logs collapse to the same template
    # E.g., User 1029 and User 1030
    user_logs = df_processed[df_processed["message"].str.contains("User.*authenticated")]
    assert len(user_logs["event_id"].unique()) == 1

    catalog = extractor.get_template_catalog()
    assert len(catalog) > 0
    assert "event_id" in catalog.columns
    assert "template" in catalog.columns


def test_window_feature_extraction():
    sample_file = Path("sample_logs/sample_server.log")
    df = parse_log_file(sample_file)
    extractor = LogTemplateExtractor(rare_threshold=0.1)
    df_processed = extractor.fit_transform(df)

    feat_df = extract_window_features(df_processed, window_size="1min")

    assert not feat_df.empty
    assert "window_start" in feat_df.columns
    assert "total_logs" in feat_df.columns
    assert "error_count" in feat_df.columns
    assert "critical_count" in feat_df.columns
    assert "error_ratio" in feat_df.columns
    assert "volume_change" in feat_df.columns

    # 10:03 window in our sample log should show high errors and criticals
    anomaly_window = feat_df[feat_df["error_count"] > 0]
    assert len(anomaly_window) >= 1
    
    # Feature matrix check
    matrix = get_feature_matrix(feat_df)
    assert matrix.shape[1] == 8
    assert not matrix.isnull().any().any()

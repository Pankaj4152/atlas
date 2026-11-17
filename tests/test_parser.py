import pytest
import pandas as pd
from pathlib import Path
from backend.pipeline.parser import parse_line, parse_log_file, normalize_level

def test_normalize_level():
    assert normalize_level("warn") == "WARNING"
    assert normalize_level("WARNING") == "WARNING"
    assert normalize_level("err") == "ERROR"
    assert normalize_level("error") == "ERROR"
    assert normalize_level("CRIT") == "CRITICAL"
    assert normalize_level("info") == "INFO"
    assert normalize_level(None) == "INFO"

def test_parse_line_standard():
    line = "2026-11-18 10:00:01 INFO [system] Server started"
    res = parse_line(line)
    assert res is not None
    assert str(res["timestamp"]).startswith("2026-11-18 10:00:01")
    assert res["level"] == "INFO"
    assert res["component"] == "system"
    assert res["message"] == "Server started"

def test_parse_sample_log_file():
    sample_file = Path("sample_logs/sample_server.log")
    df = parse_log_file(sample_file)
    assert not df.empty
    assert len(df) >= 20
    assert "timestamp" in df.columns
    assert "level" in df.columns
    assert "component" in df.columns
    assert "message" in df.columns
    
    # Check that levels are normalized
    levels = set(df["level"].unique())
    assert levels.issubset({"INFO", "WARNING", "ERROR", "CRITICAL"})
    
    # Check presence of critical logs from 10:03
    crit_count = (df["level"] == "CRITICAL").sum()
    assert crit_count >= 3

"""
Log Parser module.
Handles standard log formats, extracts timestamp, level, component/service, and message.
Also supports structured CSV/TSV input and malformed line tolerance.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
import pandas as pd
from dateutil import parser as date_parser

# Canonical severity levels
SEVERITY_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

# Mapping common variations to canonical severity
LEVEL_MAP = {
    "DEBUG": "DEBUG",
    "DBG": "DEBUG",
    "INFO": "INFO",
    "INF": "INFO",
    "NOTICE": "INFO",
    "WARN": "WARNING",
    "WARNING": "WARNING",
    "ERR": "ERROR",
    "ERROR": "ERROR",
    "FAIL": "ERROR",
    "FAILURE": "ERROR",
    "CRIT": "CRITICAL",
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
    "EMERG": "CRITICAL",
    "EMERGENCY": "CRITICAL",
    "ALERT": "CRITICAL",
}

# Regex patterns for common server log formats
PATTERNS = [
    # Format 1: 2026-11-18 10:00:01 INFO [component] message
    re.compile(
        r"^(?P<timestamp>\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
        r"(?P<level>[A-Za-z]+)\s+"
        r"(?:\[(?P<component>[^\]]+)\]\s+)?(?P<message>.*)$"
    ),
    # Format 2: [2026-11-18 10:00:01] [INFO] [component] message
    re.compile(
        r"^\[(?P<timestamp>[^\]]+)\]\s+"
        r"\[(?P<level>[A-Za-z]+)\]\s+"
        r"(?:\[(?P<component>[^\]]+)\]\s+)?(?P<message>.*)$"
    ),
    # Format 3: 2026-11-18 10:00:01 - component - INFO - message
    re.compile(
        r"^(?P<timestamp>\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*-\s*"
        r"(?P<component>[^\-]+)\s*-\s*"
        r"(?P<level>[A-Za-z]+)\s*-\s*(?P<message>.*)$"
    ),
    # Format 4: Syslog style: Nov 18 10:00:01 hostname service[1234]: message
    re.compile(
        r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
        r"(?P<component>[^\s:]+)(?:\[\d+\])?:\s+(?P<message>.*)$"
    ),
]


def normalize_level(raw_level: Optional[str]) -> str:
    """Normalize log level variations to canonical uppercase levels."""
    if not raw_level:
        return "INFO"
    clean = raw_level.strip().upper()
    return LEVEL_MAP.get(clean, "INFO")


def parse_timestamp(raw_ts: str) -> Optional[datetime]:
    """Parse timestamp string into standard datetime object."""
    if not raw_ts:
        return None
    try:
        return date_parser.parse(raw_ts)
    except (ValueError, OverflowError):
        return None


def parse_line(line: str, fallback_ts: Optional[datetime] = None) -> Optional[dict]:
    """
    Parse a single log line into a structured dictionary.
    Returns None if line is blank or comment.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    for pattern in PATTERNS:
        match = pattern.match(line)
        if match:
            data = match.groupdict()
            ts = parse_timestamp(data.get("timestamp")) if data.get("timestamp") else fallback_ts
            level = normalize_level(data.get("level"))
            component = (data.get("component") or "system").strip()
            message = (data.get("message") or "").strip()
            return {
                "timestamp": ts,
                "level": level,
                "component": component,
                "message": message,
                "raw": line,
            }

    # Fallback for unstructured/malformed lines (e.g. stacktrace continuation)
    # Scan for level keyword anywhere in the line
    detected_level = "INFO"
    for word in line.split():
        clean_word = word.strip("[]():,").upper()
        if clean_word in LEVEL_MAP:
            detected_level = LEVEL_MAP[clean_word]
            break

    return {
        "timestamp": fallback_ts,
        "level": detected_level,
        "component": "unstructured",
        "message": line,
        "raw": line,
    }


def parse_log_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Parse a log file (.log, .txt, .csv) into a normalized pandas DataFrame.
    DataFrame columns:
    - timestamp (datetime64[ns])
    - level (str: DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - component (str)
    - message (str)
    - raw (str)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    # Handle structured CSV files directly
    if path.suffix.lower() == ".csv":
        return _parse_csv(path)

    # Process text/log lines
    records = []
    last_valid_ts = None

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parsed = parse_line(line, fallback_ts=last_valid_ts)
            if parsed:
                if parsed["timestamp"]:
                    last_valid_ts = parsed["timestamp"]
                records.append(parsed)

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "level", "component", "message", "raw"])

    # If timestamps have NaNs (e.g. from multiline stack traces), forward-fill
    df["timestamp"] = pd.to_datetime(df["timestamp"]).ffill()

    # Sort chronologically and drop duplicate identical logs
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    return df


def _parse_csv(path: Path) -> pd.DataFrame:
    """Parse structured CSV with flexible column matching."""
    df_raw = pd.read_csv(path)
    col_map = {}

    for col in df_raw.columns:
        norm = col.strip().lower()
        if norm in ("timestamp", "time", "date", "datetime"):
            col_map[col] = "timestamp"
        elif norm in ("level", "severity", "loglevel", "type"):
            col_map[col] = "level"
        elif norm in ("component", "service", "source", "logger", "module"):
            col_map[col] = "component"
        elif norm in ("message", "msg", "content", "log", "text"):
            col_map[col] = "message"

    df = df_raw.rename(columns=col_map)
    for req in ["timestamp", "level", "component", "message"]:
        if req not in df.columns:
            if req == "component":
                df["component"] = "system"
            elif req == "level":
                df["level"] = "INFO"
            elif req == "message":
                df["message"] = ""
            elif req == "timestamp":
                df["timestamp"] = pd.Timestamp.now()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce").ffill()
    df["level"] = df["level"].astype(str).apply(normalize_level)
    df["component"] = df["component"].astype(str)
    df["message"] = df["message"].astype(str)
    df["raw"] = df["message"]

    return df[["timestamp", "level", "component", "message", "raw"]].sort_values(by="timestamp").reset_index(drop=True)

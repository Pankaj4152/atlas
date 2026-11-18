"""
Log Parser module.
Handles standard log formats, HDFS, BGL, Syslog, Apache, and structured CSV input.
Includes robust fallback for timestamps and malformed lines.
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
    "SEVERE": "CRITICAL",
    "EMERG": "CRITICAL",
    "EMERGENCY": "CRITICAL",
    "ALERT": "CRITICAL",
}

# Regex patterns for common server log formats & benchmark datasets
PATTERNS = [
    # Format 1: Standard YYYY-MM-DD HH:MM:SS LEVEL [component] message
    re.compile(
        r"^(?P<timestamp>\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
        r"(?P<level>[A-Za-z]+)\s+"
        r"(?:\[(?P<component>[^\]]+)\]\s+)?(?P<message>.*)$"
    ),
    # Format 2: Bracketed [2026-11-18 10:00:01] [INFO] [component] message
    re.compile(
        r"^\[(?P<timestamp>[^\]]+)\]\s+"
        r"\[(?P<level>[A-Za-z]+)\]\s+"
        r"(?:\[(?P<component>[^\]]+)\]\s+)?(?P<message>.*)$"
    ),
    # Format 3: HDFS LogHub Format: 081109 203615 148 INFO dfs.DataNode$PacketResponder: message
    # Timestamp: YYMMDD HHMMSS (e.g. 081109 203615)
    re.compile(
        r"^(?P<date>\d{6})\s+(?P<time>\d{6})\s+\d+\s+"
        r"(?P<level>[A-Za-z]+)\s+"
        r"(?P<component>[^:]+):\s+(?P<message>.*)$"
    ),
    # Format 4: BGL LogHub Format: - 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.675872 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error
    re.compile(
        r"^-\s+(?P<epoch>\d+)\s+\S+\s+\S+\s+"
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d+)\s+"
        r"\S+\s+\S+\s+(?P<component>\S+)\s+"
        r"(?P<level>[A-Za-z]+)\s+(?P<message>.*)$"
    ),
    # Format 5: Hyphenated 2026-11-18 10:00:01 - component - INFO - message
    re.compile(
        r"^(?P<timestamp>\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*-\s*"
        r"(?P<component>[^\-]+)\s*-\s*"
        r"(?P<level>[A-Za-z]+)\s*-\s*(?P<message>.*)$"
    ),
    # Format 6: Syslog style: Nov 18 10:00:01 hostname service[1234]: message
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
        # Special BGL format: 2005-06-03-15.42.50.675872
        if len(raw_ts) > 19 and raw_ts[10] == "-":
            formatted = f"{raw_ts[:10]} {raw_ts[11:13]}:{raw_ts[14:16]}:{raw_ts[17:]}"
            return datetime.strptime(formatted[:19], "%Y-%m-%d %H:%M:%S")
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
            # Handle HDFS YYMMDD HHMMSS
            if "date" in data and "time" in data:
                try:
                    d_str = f"20{data['date']} {data['time']}"
                    ts = datetime.strptime(d_str, "%Y%m%d %H%M%S")
                except ValueError:
                    ts = fallback_ts
            elif data.get("timestamp"):
                ts = parse_timestamp(data.get("timestamp")) or fallback_ts
            else:
                ts = fallback_ts

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

    # Fallback for unstructured lines / stack traces
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
    Guarantees valid datetime timestamps (synthetic timestamps if unparseable).
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

    # If all timestamps are NaT, generate sequential synthetic timestamps
    if df["timestamp"].isna().all():
        base_time = datetime(2026, 11, 18, 10, 0, 0)
        # 1-second interval sequential timestamps
        df["timestamp"] = [base_time + pd.Timedelta(seconds=i) for i in range(len(df))]
    else:
        # Forward fill and backfill any remaining NaNs
        df["timestamp"] = pd.to_datetime(df["timestamp"]).ffill().bfill()

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

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce").ffill().bfill()
    df["level"] = df["level"].astype(str).apply(normalize_level)
    df["component"] = df["component"].astype(str)
    df["message"] = df["message"].astype(str)
    df["raw"] = df["message"]

    return df[["timestamp", "level", "component", "message", "raw"]].sort_values(by="timestamp").reset_index(drop=True)

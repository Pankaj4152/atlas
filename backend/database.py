"""
SQLite database layer for persisting uploads, analyses, and report metadata.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

DB_PATH = Path("data/atlas_analyzer.db")


def get_db_connection() -> sqlite3.Connection:
    """Return a configured sqlite3 connection with dict-like row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for uploaded files
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            file_size_kb REAL NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    # Table for completed analysis reports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            upload_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            total_logs INTEGER NOT NULL,
            total_windows INTEGER NOT NULL,
            flagged_windows INTEGER NOT NULL,
            critical_incidents INTEGER NOT NULL,
            total_incidents INTEGER NOT NULL,
            report_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (upload_id) REFERENCES uploads (id)
        )
    """)

    conn.commit()
    conn.close()


def save_upload(file_id: str, original_filename: str, stored_path: str, file_size_kb: float) -> Dict[str, Any]:
    """Save record of an uploaded log file."""
    now_iso = datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO uploads (id, original_filename, stored_path, file_size_kb, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (file_id, original_filename, stored_path, file_size_kb, now_iso),
    )
    conn.commit()
    conn.close()
    return {
        "file_id": file_id,
        "filename": original_filename,
        "stored_path": stored_path,
        "file_size_kb": file_size_kb,
        "uploaded_at": now_iso,
    }


def get_upload(file_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve upload record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploads WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def save_report(report_id: str, upload_id: str, filename: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save full analysis report."""
    now_iso = datetime.now().isoformat()
    summary = report_data.get("summary", {})
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reports (
            id, upload_id, filename, total_logs, total_windows, 
            flagged_windows, critical_incidents, total_incidents, 
            report_data, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report_id,
            upload_id,
            filename,
            summary.get("total_logs", 0),
            summary.get("total_windows", 0),
            summary.get("flagged_windows", 0),
            summary.get("critical_incidents", 0),
            summary.get("total_incidents", 0),
            json.dumps(report_data),
            now_iso,
        ),
    )
    conn.commit()
    conn.close()
    return {"report_id": report_id, "created_at": now_iso}


def list_reports() -> List[Dict[str, Any]]:
    """List summary records of all past reports."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, upload_id, filename, total_logs, total_windows, 
               flagged_windows, critical_incidents, total_incidents, created_at
        FROM reports
        ORDER BY created_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Fetch complete report data by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["report_data"] = json.loads(data["report_data"])
        return data
    return None

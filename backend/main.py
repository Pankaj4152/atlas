"""
FastAPI Main Application.
REST API for Atlas Server Log Analyzer.
Endpoints:
- POST /api/upload
- POST /api/analyze/{file_id}
- GET /api/reports
- GET /api/reports/{id}
- GET /api/reports/{id}/pdf
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from backend.database import (
    init_db,
    save_upload,
    get_upload,
    save_report,
    list_reports,
    get_report,
)
from backend.pipeline.analyzer import LogAnalysisPipeline
from backend.report_generator import generate_pdf_report

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize SQLite database
init_db()

app = FastAPI(
    title="Atlas Server Log Analyzer API",
    description="Backend API for AI-powered server anomaly detection and root-cause analysis.",
    version="1.0.0",
)

# Enable CORS for React frontend (Vite defaults to 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "service": "Atlas Server Log Analyzer",
        "status": "online",
        "version": "1.0.0",
    }


@app.post("/api/upload")
async def upload_log_file(file: UploadFile = File(...)):
    """Upload a .log, .txt, or .csv server log file."""
    allowed_extensions = {".log", ".txt", ".csv"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Please upload .log, .txt, or .csv",
        )

    file_id = str(uuid.uuid4())[:8]
    saved_filename = f"{file_id}_{file.filename}"
    file_path = UPLOAD_DIR / saved_filename

    # Save to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_kb = round(file_path.stat().st_size / 1024, 2)
    record = save_upload(
        file_id=file_id,
        original_filename=file.filename,
        stored_path=str(file_path),
        file_size_kb=file_size_kb,
    )

    return {
        "status": "success",
        "message": "File uploaded successfully.",
        "file": record,
    }


@app.post("/api/analyze/{file_id}")
async def analyze_uploaded_file(file_id: str, window_size: Optional[str] = "1min"):
    """Run full anomaly detection and LLM diagnostic pipeline on uploaded file."""
    upload_record = get_upload(file_id)
    if not upload_record:
        raise HTTPException(status_code=404, detail="Uploaded file ID not found.")

    file_path = Path(upload_record["stored_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Underlying log file missing from disk.")

    pipeline = LogAnalysisPipeline(window_size=window_size)
    report_data = pipeline.analyze_file(file_path)

    # Save completed report in database
    report_id = f"REP-{uuid.uuid4().hex[:8]}"
    save_report(
        report_id=report_id,
        upload_id=file_id,
        filename=upload_record["original_filename"],
        report_data=report_data,
    )

    return {
        "status": "success",
        "report_id": report_id,
        "report": report_data,
    }


@app.get("/api/reports")
async def get_all_reports():
    """Retrieve list of previous analysis reports."""
    reports = list_reports()
    return {"reports": reports}


@app.get("/api/reports/{report_id}")
async def get_report_by_id(report_id: str):
    """Retrieve full analysis report data for dashboard rendering."""
    record = get_report(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Report ID not found.")
    return record


@app.get("/api/reports/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """Generate and stream downloadable executive PDF report."""
    record = get_report(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Report ID not found.")

    report_data = record["report_data"]
    pdf_buffer = generate_pdf_report(report_data)

    fname = f"anomaly_report_{report_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )

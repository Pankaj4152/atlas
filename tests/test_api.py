import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_upload_and_analyze_flow():
    sample_file_path = Path("sample_logs/sample_server.log")

    # 1. Test Upload
    with open(sample_file_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("sample_server.log", f, "text/plain")}
        )
    assert response.status_code == 200
    upload_data = response.json()
    assert upload_data["status"] == "success"
    file_id = upload_data["file"]["file_id"]

    # 2. Test Analyze
    resp_analyze = client.post(f"/api/analyze/{file_id}")
    assert resp_analyze.status_code == 200
    res = resp_analyze.json()
    assert res["status"] == "success"
    assert "report_id" in res
    report_id = res["report_id"]

    # 3. Test Get Reports list
    resp_list = client.get("/api/reports")
    assert resp_list.status_code == 200
    assert any(r["id"] == report_id for r in resp_list.json()["reports"])

    # 4. Test Get Report Details
    resp_detail = client.get(f"/api/reports/{report_id}")
    assert resp_detail.status_code == 200
    report_obj = resp_detail.json()
    assert report_obj["id"] == report_id
    assert len(report_obj["report_data"]["incidents"]) >= 1

    # 5. Test Download PDF
    resp_pdf = client.get(f"/api/reports/{report_id}/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert len(resp_pdf.content) > 1000  # PDF generated with valid binary data

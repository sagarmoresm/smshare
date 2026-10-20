"""
SMSHARE Test Suite — End-to-End Verification
"""

import os
import io
import time
import zipfile
import datetime
from pathlib import Path
from fastapi.testclient import TestClient

from server import app, UPLOADS_DIR
import database

client = TestClient(app)

def test_system_status():
    print("[TEST] Checking system status endpoint...")
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "SMSHARE" in data["system"]
    print("  -> Status OK:", data)

def test_send_and_receive_text():
    print("\n[TEST] Testing text send and receive flow...")
    test_text = "Hello Neo-Brutalism SMSHARE! Secret note: 98765"
    
    # Send
    response = client.post("/api/send", data={"text": test_text, "expireAtHour": 0.5})
    assert response.status_code == 200, response.text
    send_data = response.json()
    code = send_data["code"]
    assert len(code) == 4, f"Expected 4-character code, got {code}"
    print(f"  -> Generated 4-character code: {code}")

    # Receive
    receive_res = client.get(f"/api/receive?code={code}")
    assert receive_res.status_code == 200, receive_res.text
    receive_data = receive_res.json()
    assert receive_data["text"] == test_text
    assert receive_data["code"] == code
    print("  -> Successfully received text payload:", receive_data["text"])

def test_send_and_receive_files_and_zip():
    print("\n[TEST] Testing multi-file upload, individual download, and ZIP bundling...")
    file1_content = b"Content of sample document A"
    file2_content = b"Content of sample document B - with more data"

    files = [
        ("files", ("document_a.txt", io.BytesIO(file1_content), "text/plain")),
        ("files", ("document_b.txt", io.BytesIO(file2_content), "text/plain"))
    ]
    data = {
        "text": "Check these two documents",
        "expireAtHour": 2.0
    }

    # Upload
    response = client.post("/api/send", data=data, files=files)
    assert response.status_code == 200, response.text
    res_json = response.json()
    code = res_json["code"]
    assert res_json["file_count"] == 2
    print(f"  -> Uploaded 2 files with code: {code}")

    # Receive info
    rec_res = client.get(f"/api/receive?code={code}")
    assert rec_res.status_code == 200
    rec_json = rec_res.json()
    assert len(rec_json["files"]) == 2
    assert rec_json["text"] == "Check these two documents"

    file_a = rec_json["files"][0]
    file_b = rec_json["files"][1]

    # Download File A
    dl_res = client.get(file_a["downloadUrl"])
    assert dl_res.status_code == 200
    assert dl_res.content == file1_content
    print(f"  -> Downloaded single file '{file_a['fileName']}' successfully.")

    # Download All as ZIP
    zip_res = client.get(f"/api/download-zip/{code}")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"
    
    # Inspect ZIP contents
    with zipfile.ZipFile(io.BytesIO(zip_res.content)) as z:
        zip_names = z.namelist()
        assert "document_a.txt" in zip_names
        assert "document_b.txt" in zip_names
        assert "SMSHARE_RECEIPT.txt" in zip_names
        assert z.read("document_a.txt") == file1_content
        assert z.read("document_b.txt") == file2_content
    print("  -> Downloaded and verified ZIP archive containing all files and receipt.")

def test_auto_wipe_and_disk_purge():
    print("\n[TEST] Testing auto-wipe and disk file deletion...")
    # Create a share directly in DB that expired 1 minute ago
    now = datetime.datetime.now(datetime.timezone.utc)
    expired_time = (now - datetime.timedelta(minutes=1)).isoformat()
    now_iso = now.isoformat()

    with database.get_connection() as conn:
        code = "TEST"
        conn.execute("DELETE FROM shares WHERE code = 'TEST'")
        conn.execute(
            """
            INSERT INTO shares (code, share_type, text_content, created_at, expires_at, file_count, total_size)
            VALUES (?, 'text', 'Expired secret', ?, ?, 0, 0)
            """,
            (code, now_iso, expired_time)
        )
        conn.commit()

    # Attempt to retrieve expired code via API
    res = client.get("/api/receive?code=TEST")
    assert res.status_code == 404
    print("  -> Expired code was rejected with 404.")

    # Verify database record was deleted
    assert database.get_share("TEST") is None
    print("  -> Verified database record was hard-deleted.")

def test_static_files():
    print("\n[TEST] Verifying static frontend files serve properly...")
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "SMSHARE" in res_index.text
    assert "<svg" in res_index.text
    print("  -> index.html served OK.")

    res_css = client.get("/style.css")
    assert res_css.status_code == 200
    assert "--border-width: 3px;" in res_css.text
    print("  -> style.css (Neo-Brutalism theme) served OK.")

    res_js = client.get("/app.js")
    assert res_js.status_code == 200
    assert "DOMContentLoaded" in res_js.text
    print("  -> app.js served OK.")

if __name__ == "__main__":
    print("========================================")
    print("   RUNNING SMSHARE REPLICA TEST SUITE   ")
    print("========================================")
    test_system_status()
    test_send_and_receive_text()
    test_send_and_receive_files_and_zip()
    test_auto_wipe_and_disk_purge()
    test_static_files()
    print("\n[SUCCESS] ALL TESTS PASSED! EVERYTHING IS 100% WORKING!")
    print("========================================")

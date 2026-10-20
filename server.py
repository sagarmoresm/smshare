import os
import sys
import shutil
import uuid
import io
import zipfile
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import database

BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

# Limits: Max 10 files, 500 MB per file
MAX_FILES = 10
MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

async def purge_expired_shares():
    """Background task to delete expired shares and hard-remove files from disk."""
    while True:
        try:
            expired_codes = database.get_expired_codes()
            for code in expired_codes:
                # Remove from database
                database.delete_share(code)
                # Remove files from disk
                code_folder = UPLOADS_DIR / code
                if code_folder.exists():
                    shutil.rmtree(code_folder, ignore_errors=True)
                print(f"[Purge Worker] Successfully purged expired share: {code}")
        except Exception as e:
            print(f"[Purge Worker Error]: {e}")
        await asyncio.sleep(20)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database.init_db()
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    purge_task = asyncio.create_task(purge_expired_shares())
    yield
    # Shutdown
    purge_task.cancel()

app = FastAPI(
    title="SMSHARE API",
    description="Privacy-first, self-destructing temporary file & text sharing with Neo-Brutalist design",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/send")
async def send_payload(
    text: Optional[str] = Form(None),
    expireAtHour: float = Form(0.5), # Default 30 min
    files: List[UploadFile] = File(default=[])
):
    clean_text = text.strip() if text else ""
    valid_files = [f for f in files if f.filename and f.filename.strip()]

    if not clean_text and not valid_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide text message or at least one file to share."
        )

    if len(valid_files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum allowed is {MAX_FILES} files per share."
        )

    # Allowed expiry options: 0.5 (30m), 2, 12, 24 hours
    if expireAtHour <= 0 or expireAtHour > 72:
        expireAtHour = 0.5

    # Determine type
    if clean_text and valid_files:
        share_type = "mixed"
    elif valid_files:
        share_type = "files"
    else:
        share_type = "text"

    # Pre-generate share code
    with database.get_connection() as conn:
        code = database.generate_unique_code(conn)

    code_folder = UPLOADS_DIR / code
    saved_file_records = []

    if valid_files:
        code_folder.mkdir(parents=True, exist_ok=True)
        for uf in valid_files:
            file_id = uuid.uuid4().hex[:12]
            # Sanitize original filename
            safe_original_name = Path(uf.filename).name or f"file_{file_id}"
            ext = Path(safe_original_name).suffix
            stored_name = f"{file_id}_{safe_original_name}"
            stored_path = code_folder / stored_name

            # Stream save file and track size
            size_counter = 0
            with open(stored_path, "wb") as dest:
                while chunk := await uf.read(1024 * 1024):  # 1MB chunks
                    size_counter += len(chunk)
                    if size_counter > MAX_FILE_SIZE_BYTES:
                        # Clean up and abort
                        dest.close()
                        shutil.rmtree(code_folder, ignore_errors=True)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File '{safe_original_name}' exceeds 500 MB limit."
                        )
                    dest.write(chunk)

            saved_file_records.append({
                "id": file_id,
                "file_name": safe_original_name,
                "file_size": size_counter,
                "file_mime": uf.content_type or "application/octet-stream",
                "stored_filename": stored_name
            })

    # Save to SQLite database
    share = database.create_share(
        code=code,
        share_type=share_type,
        text_content=clean_text if clean_text else None,
        expire_hours=expireAtHour,
        files=saved_file_records
    )

    # Calculate seconds
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = datetime.datetime.fromisoformat(share["expires_at"])
    seconds_remaining = max(0, int((expires_at - now).total_seconds()))

    return {
        "success": True,
        "code": share["code"],
        "share_type": share["share_type"],
        "expires_at": share["expires_at"],
        "seconds_remaining": seconds_remaining,
        "file_count": share["file_count"],
        "total_size": share["total_size"]
    }

@app.get("/api/receive")
async def receive_payload(code: str = Query(..., min_length=1, max_length=10)):
    clean_code = code.strip().upper()
    share = database.get_share(clean_code)
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested code is invalid or has expired and been destroyed."
        )

    # Format file list with download URLs
    formatted_files = []
    for f in share.get("files", []):
        formatted_files.append({
            "id": f["id"],
            "fileName": f["file_name"],
            "fileSize": f["file_size"],
            "fileMime": f["file_mime"],
            "downloadUrl": f"/api/download/{clean_code}/{f['id']}"
        })

    return {
        "success": True,
        "code": share["code"],
        "type": share["share_type"],
        "text": share["text_content"],
        "files": formatted_files,
        "fileCount": share["file_count"],
        "totalSize": share["total_size"],
        "createdAt": share["created_at"],
        "expiresAt": share["expires_at"],
        "secondsRemaining": share["seconds_remaining"]
    }

@app.get("/api/download/{code}/{file_id}")
async def download_file(code: str, file_id: str):
    clean_code = code.strip().upper()
    share = database.get_share(clean_code)
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content has expired or does not exist."
        )

    file_entry = next((f for f in share.get("files", []) if f["id"] == file_id), None)
    if not file_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in this transfer."
        )

    file_path = UPLOADS_DIR / clean_code / file_entry["stored_filename"]
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File binary no longer available."
        )

    return FileResponse(
        path=file_path,
        filename=file_entry["file_name"],
        media_type=file_entry["file_mime"],
        content_disposition_type="attachment"
    )

@app.get("/api/download-zip/{code}")
async def download_all_zip(code: str):
    clean_code = code.strip().upper()
    share = database.get_share(clean_code)
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content has expired or does not exist."
        )

    files = share.get("files", [])
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files attached to this share."
        )

    # Build ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for f in files:
            file_path = UPLOADS_DIR / clean_code / f["stored_filename"]
            if file_path.exists():
                zip_file.write(file_path, arcname=f["file_name"])

        # Add transfer receipt note
        readme_text = (
            f"SMSHARE SECURE TRANSFER\n"
            f"Code: {clean_code}\n"
            f"Created: {share['created_at']}\n"
            f"Expires: {share['expires_at']}\n\n"
            f"All content on SMSHARE self-destructs after expiry.\n"
            f"Zero logging · No accounts · Built for privacy-first sharing.\n"
        )
        zip_file.writestr("SMSHARE_RECEIPT.txt", readme_text)

    zip_buffer.seek(0)
    zip_filename = f"smshare_{clean_code}_files.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )

@app.get("/api/status")
async def system_status():
    with database.get_connection() as conn:
        active_count = conn.execute("SELECT COUNT(*) FROM shares").fetchone()[0]
    return {
        "status": "online",
        "system": "SMSHARE Neo-Brutalism Platform",
        "active_shares": active_count,
        "limits": {
            "max_files": MAX_FILES,
            "max_file_size_mb": 500
        }
    }

@app.get("/favicon.ico")
@app.get("/favicon.svg")
async def get_favicon():
    fav_path = STATIC_DIR / "favicon.svg"
    if fav_path.exists():
        return FileResponse(fav_path, media_type="image/svg+xml")
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

# Direct route for /c/{code} to serve the index.html with code preloaded
@app.get("/c/{code}")
async def direct_code_share(code: str):
    return FileResponse(STATIC_DIR / "index.html")

# Mount static frontend
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

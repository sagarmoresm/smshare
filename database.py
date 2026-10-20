import sqlite3
import random
import string
import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

DB_PATH = Path(__file__).parent / "smshare.db"

# Exclude ambiguous characters like 0, O, 1, I for frictionless user communication
CHAR_SET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shares (
                code TEXT PRIMARY KEY,
                share_type TEXT NOT NULL,
                text_content TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                file_count INTEGER DEFAULT 0,
                total_size INTEGER DEFAULT 0
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_mime TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                FOREIGN KEY(code) REFERENCES shares(code) ON DELETE CASCADE
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_shares_expires ON shares(expires_at);")
        conn.commit()

# Ensure tables are initialized on import
init_db()


def generate_unique_code(conn: sqlite3.Connection) -> str:
    for _ in range(50):
        code = "".join(random.choices(CHAR_SET, k=4))
        cursor = conn.execute("SELECT 1 FROM shares WHERE code = ?", (code,))
        if not cursor.fetchone():
            return code
    # Fallback to 5 chars if dense
    return "".join(random.choices(CHAR_SET, k=5))

def create_share(
    code: str,
    share_type: str,
    text_content: Optional[str],
    expire_hours: float,
    files: List[Dict[str, Any]]
) -> Dict[str, Any]:
    code = code.strip().upper()
    with get_connection() as conn:
        now = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now + datetime.timedelta(hours=expire_hours)
        
        now_iso = now.isoformat()
        expires_iso = expires_at.isoformat()
        
        total_size = sum(f.get("file_size", 0) for f in files)
        file_count = len(files)
        
        conn.execute(
            """
            INSERT INTO shares (code, share_type, text_content, created_at, expires_at, file_count, total_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (code, share_type, text_content, now_iso, expires_iso, file_count, total_size)
        )
        
        for f in files:
            conn.execute(
                """
                INSERT INTO files (id, code, file_name, file_size, file_mime, stored_filename)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (f["id"], code, f["file_name"], f["file_size"], f["file_mime"], f["stored_filename"])
            )
        
        conn.commit()
        return {
            "code": code,
            "share_type": share_type,
            "created_at": now_iso,
            "expires_at": expires_iso,
            "file_count": file_count,
            "total_size": total_size
        }

def get_share(code: str) -> Optional[Dict[str, Any]]:
    code = code.strip().upper()
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM shares WHERE code = ?", (code,))
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check if already expired
        now = datetime.datetime.now(datetime.timezone.utc)
        expires_at = datetime.datetime.fromisoformat(row["expires_at"])
        if now >= expires_at:
            # Auto-purge on access
            delete_share(code)
            return None
        
        files_cursor = conn.execute("SELECT * FROM files WHERE code = ?", (code,))
        files = [dict(f) for f in files_cursor.fetchall()]
        
        share_data = dict(row)
        share_data["files"] = files
        share_data["seconds_remaining"] = max(0, int((expires_at - now).total_seconds()))
        return share_data

def get_expired_codes() -> List[str]:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute("SELECT code FROM shares WHERE expires_at <= ?", (now,))
        return [row["code"] for row in cursor.fetchall()]

def delete_share(code: str) -> List[str]:
    code = code.strip().upper()
    with get_connection() as conn:
        # Get all stored filenames before deleting
        cursor = conn.execute("SELECT stored_filename FROM files WHERE code = ?", (code,))
        stored_files = [row["stored_filename"] for row in cursor.fetchall()]
        
        conn.execute("DELETE FROM files WHERE code = ?", (code,))
        conn.execute("DELETE FROM shares WHERE code = ?", (code,))
        conn.commit()
        return stored_files

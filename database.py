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
                total_size INTEGER DEFAULT 0,
                is_private INTEGER DEFAULT 0,
                password TEXT
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
        
        # Safely migrate existing tables if columns missing
        try:
            conn.execute("ALTER TABLE shares ADD COLUMN is_private INTEGER DEFAULT 0;")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE shares ADD COLUMN password TEXT;")
        except Exception:
            pass

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
    files: List[Dict[str, Any]],
    is_private: bool = False,
    password: Optional[str] = None
) -> Dict[str, Any]:
    code = code.strip().upper()
    with get_connection() as conn:
        now = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now + datetime.timedelta(hours=expire_hours)
        
        now_iso = now.isoformat()
        expires_iso = expires_at.isoformat()
        
        total_size = sum(f.get("file_size", 0) for f in files)
        file_count = len(files)
        clean_pass = password.strip() if password else None
        
        conn.execute(
            """
            INSERT INTO shares (code, share_type, text_content, created_at, expires_at, file_count, total_size, is_private, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (code, share_type, text_content, now_iso, expires_iso, file_count, total_size, 1 if is_private else 0, clean_pass)
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
            "total_size": total_size,
            "is_private": is_private,
            "has_password": bool(clean_pass)
        }

def get_share(code: str, password: Optional[str] = None, is_admin: bool = False) -> Optional[Dict[str, Any]]:
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
        
        seconds_remaining = max(0, int((expires_at - now).total_seconds()))
        is_priv = bool(row["is_private"])
        stored_pass = row["password"] or ""

        # If private and not admin, check password
        if is_priv and not is_admin:
            if not password or password.strip() != stored_pass.strip():
                return {
                    "code": code,
                    "requires_password": True,
                    "is_private": True,
                    "seconds_remaining": seconds_remaining
                }
        
        files_cursor = conn.execute("SELECT * FROM files WHERE code = ?", (code,))
        files = [dict(f) for f in files_cursor.fetchall()]
        
        share_data = dict(row)
        share_data["files"] = files
        share_data["seconds_remaining"] = seconds_remaining
        share_data["is_private"] = is_priv
        share_data["requires_password"] = False
        return share_data

def get_all_shares_for_admin() -> List[Dict[str, Any]]:
    """Returns all non-expired shares with full files and password details for the admin dashboard."""
    now = datetime.datetime.now(datetime.timezone.utc)
    now_iso = now.isoformat()
    
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM shares WHERE expires_at > ? ORDER BY created_at DESC", (now_iso,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            share = dict(row)
            expires_at = datetime.datetime.fromisoformat(share["expires_at"])
            share["seconds_remaining"] = max(0, int((expires_at - now).total_seconds()))
            share["is_private"] = bool(share["is_private"])
            
            f_cursor = conn.execute("SELECT * FROM files WHERE code = ?", (share["code"],))
            share["files"] = [dict(f) for f in f_cursor.fetchall()]
            results.append(share)
            
        return results

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

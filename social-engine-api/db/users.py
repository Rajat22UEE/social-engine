"""
db/users.py - User database operations

Handles session-based user creation and retrieval.
"""
from datetime import datetime
from db.connection import get_conn


def get_or_create_user(session_id: str) -> dict:
    """
    Find user by session_id or create a new one.
    Updates last_active timestamp on every access.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, session_id, name, email, created_at FROM users WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return {"id": row[0], "session_id": row[1], "name": row[2], "email": row[3], "created_at": row[4]}
    else:
        c.execute("INSERT INTO users (session_id) VALUES (?)", (session_id,))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return {"id": user_id, "session_id": session_id, "name": "", "email": "", "created_at": datetime.now().isoformat()}
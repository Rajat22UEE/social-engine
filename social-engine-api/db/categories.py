"""
db/categories.py - Content category database operations

Fetches available content categories for the generation flow.
"""
from db.connection import get_conn


def get_categories() -> list:
    """
    Fetch all content categories used for AI prompt customization.
    Returns list of dicts with id, name, key, description, prompt_hint, icon.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, key, description, prompt_hint, icon FROM content_categories")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "key": r[2], "description": r[3],
             "prompt_hint": r[4], "icon": r[5]} for r in rows]
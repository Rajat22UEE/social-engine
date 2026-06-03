"""
db/templates.py - Template database operations

Minimal: only get_template used by the generate endpoint.
"""
from db.connection import get_conn


def get_template(id: int) -> dict:
    """
    Fetch a single template by ID including its element definitions.
    Returns None if not found.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, aspect_ratio, width, height, is_default, created_at FROM templates WHERE id = ?", (id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    template = {"id": row[0], "name": row[1], "aspect_ratio": row[2], "width": row[3],
                "height": row[4], "is_default": bool(row[5]), "created_at": row[6]}
    c.execute("""SELECT id, element_key, x, y, font_size, font_family, color_hex,
                  max_chars, max_lines, alignment, background_color_hex
                  FROM template_elements WHERE template_id = ? ORDER BY y ASC""", (id,))
    elements = []
    for e in c.fetchall():
        elements.append({
            "id": e[0], "element_key": e[1], "x": e[2], "y": e[3],
            "font_size": e[4], "font_family": e[5], "color_hex": e[6],
            "max_chars": e[7], "max_lines": e[8], "alignment": e[9],
            "background_color_hex": e[10]
        })
    template["elements"] = elements
    conn.close()
    return template
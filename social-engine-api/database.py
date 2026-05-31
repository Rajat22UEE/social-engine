import sqlite3
import json
import os
from datetime import datetime

DB_PATH = 'database.db'


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # ── Tables ────────────────────────────────────────────────────────────────

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        aspect_ratio TEXT NOT NULL DEFAULT '4:5',
        width INTEGER NOT NULL DEFAULT 1080,
        height INTEGER NOT NULL DEFAULT 1350,
        is_default BOOLEAN DEFAULT 0,
        user_session_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_session_id) REFERENCES users(session_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS template_elements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER NOT NULL,
        element_key TEXT NOT NULL,
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        font_size INTEGER DEFAULT 48,
        font_family TEXT DEFAULT 'Poppins',
        color_hex TEXT DEFAULT '#1A2A4A',
        max_chars INTEGER,
        max_lines INTEGER DEFAULT 2,
        alignment TEXT DEFAULT 'center',
        background_color_hex TEXT,
        FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        template_id INTEGER,
        aspect_ratio TEXT DEFAULT '4:5',
        topic TEXT,
        headline TEXT,
        hook TEXT,
        caption TEXT,
        cta TEXT,
        hashtags TEXT,
        image_path TEXT,
        category TEXT,
        brand_name TEXT,
        is_draft BOOLEAN DEFAULT 0,
        view_count INTEGER DEFAULT 0,
        download_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id),
        FOREIGN KEY (template_id) REFERENCES templates(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        event_type TEXT NOT NULL,
        event_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS content_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        key TEXT UNIQUE NOT NULL,
        description TEXT,
        prompt_hint TEXT,
        icon TEXT DEFAULT '📋'
    )''')

    # ── Seed Default Templates ────────────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM templates WHERE is_default = 1")
    if c.fetchone()[0] == 0:
        # Feed template (4:5, 1080x1350)
        c.execute("INSERT INTO templates (name, aspect_ratio, width, height, is_default) VALUES (?, ?, ?, ?, 1)",
                  ('Instagram Feed', '4:5', 1080, 1350))
        feed_id = c.lastrowid

        # Story template (9:16, 1080x1920)
        c.execute("INSERT INTO templates (name, aspect_ratio, width, height, is_default) VALUES (?, ?, ?, ?, 1)",
                  ('Instagram Story', '9:16', 1080, 1920))
        story_id = c.lastrowid

        # Feed elements
        elements_feed = [
            ('headline', 60, 300, 80, '#1A2A4A', 50, 3),
            ('hook', 60, 480, 48, '#29BE71', 80, 2),
            ('body', 60, 620, 36, '#333333', 200, 4),
            ('cta', 60, 1100, 40, '#FFFFFF', 40, 1),
        ]
        for key, x, y, size, color, chars, lines in elements_feed:
            c.execute("""INSERT INTO template_elements 
                (template_id, element_key, x, y, font_size, color_hex, max_chars, max_lines, alignment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'center')""",
                      (feed_id, key, x, y, size, color, chars, lines))

        # Story elements (centered, larger text)
        elements_story = [
            ('headline', 80, 400, 90, '#1A2A4A', 40, 2),
            ('hook', 80, 600, 56, '#29BE71', 60, 2),
            ('body', 80, 780, 42, '#333333', 150, 4),
            ('cta', 80, 1600, 45, '#FFFFFF', 35, 1),
        ]
        for key, x, y, size, color, chars, lines in elements_story:
            c.execute("""INSERT INTO template_elements 
                (template_id, element_key, x, y, font_size, color_hex, max_chars, max_lines, alignment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'center')""",
                      (story_id, key, x, y, size, color, chars, lines))

    # ── Seed Content Categories ───────────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM content_categories")
    if c.fetchone()[0] == 0:
        categories = [
            ('Educational', 'educational', 'Share knowledge and industry insights', 'Focus on educating the audience about a specific topic or trend', '📚'),
            ('Promotional', 'promotional', 'Highlight services, products, or offers', 'Emphasize the value proposition and call-to-action', '🚀'),
            ('Case Study', 'case_study', 'Showcase success stories and results', 'Present before/after or problem/solution narrative', '📊'),
            ('Engagement', 'engagement', 'Spark conversations and build community', 'Use questions, polls, or interactive elements', '💬'),
            ('Branding', 'branding', 'Company intro, team spotlight, culture', 'Focus on brand values, mission, and team stories', '🏢'),
            ('Testimonial', 'testimonial', 'Share customer reviews and social proof', 'Highlight authentic customer quotes and experiences', '⭐'),
            ('Event', 'event', 'Promote webinars, launches, and events', 'Create urgency and highlight event details', '📅'),
            ('Quote', 'quote', 'Inspirational or thought leadership quotes', 'Use impactful statements with visual emphasis', '💡'),
        ]
        for name, key, desc, hint, icon in categories:
            c.execute("INSERT INTO content_categories (name, key, description, prompt_hint, icon) VALUES (?, ?, ?, ?, ?)",
                      (name, key, desc, hint, icon))

    conn.commit()
    conn.close()


# ── User Helpers ──────────────────────────────────────────────────────────────

def get_or_create_user(session_id: str) -> dict:
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


# ── Template Helpers ──────────────────────────────────────────────────────────

def get_templates(session_id: str = None) -> list:
    conn = get_conn()
    c = conn.cursor()
    if session_id:
        c.execute("""SELECT id, name, aspect_ratio, width, height, is_default, created_at 
                      FROM templates WHERE is_default = 1 OR user_session_id = ? 
                      ORDER BY is_default DESC, created_at DESC""", (session_id,))
    else:
        c.execute("""SELECT id, name, aspect_ratio, width, height, is_default, created_at 
                      FROM templates WHERE is_default = 1 ORDER BY created_at DESC""")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "aspect_ratio": r[2], "width": r[3], "height": r[4],
             "is_default": bool(r[5]), "created_at": r[6]} for r in rows]


def get_template(id: int) -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, aspect_ratio, width, height, is_default, created_at FROM templates WHERE id = ?", (id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    template = {"id": row[0], "name": row[1], "aspect_ratio": row[2], "width": row[3],
                "height": row[4], "is_default": bool(row[5]), "created_at": row[6]}
    # Get elements
    c.execute("""SELECT id, element_key, x, y, font_size, font_family, color_hex, max_chars, max_lines, alignment, background_color_hex
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


def create_template(session_id: str, data: dict) -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO templates (name, aspect_ratio, width, height, user_session_id)
                  VALUES (?, ?, ?, ?, ?)""",
              (data['name'], data.get('aspect_ratio', '4:5'),
               data.get('width', 1080), data.get('height', 1350), session_id))
    template_id = c.lastrowid
    if 'elements' in data:
        for el in data['elements']:
            c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, font_family, color_hex, max_chars, max_lines, alignment, background_color_hex)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (template_id, el['element_key'], el['x'], el['y'],
                       el.get('font_size', 48), el.get('font_family', 'Poppins'),
                       el.get('color_hex', '#1A2A4A'), el.get('max_chars'),
                       el.get('max_lines', 2), el.get('alignment', 'center'),
                       el.get('background_color_hex')))
    conn.commit()
    conn.close()
    return get_template(template_id)


def update_template(template_id: int, data: dict) -> dict:
    conn = get_conn()
    c = conn.cursor()
    updates = []
    params = []
    for field in ['name', 'aspect_ratio', 'width', 'height']:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])
    if updates:
        params.append(template_id)
        c.execute(f"UPDATE templates SET {', '.join(updates)} WHERE id = ?", params)
    if 'elements' in data:
        c.execute("DELETE FROM template_elements WHERE template_id = ?", (template_id,))
        for el in data['elements']:
            c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, font_family, color_hex, max_chars, max_lines, alignment, background_color_hex)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (template_id, el['element_key'], el['x'], el['y'],
                       el.get('font_size', 48), el.get('font_family', 'Poppins'),
                       el.get('color_hex', '#1A2A4A'), el.get('max_chars'),
                       el.get('max_lines', 2), el.get('alignment', 'center'),
                       el.get('background_color_hex')))
    conn.commit()
    conn.close()
    return get_template(template_id)


def delete_template(template_id: int) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM template_elements WHERE template_id = ?", (template_id,))
    c.execute("DELETE FROM templates WHERE id = ? AND is_default = 0", (template_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ── Post Helpers ──────────────────────────────────────────────────────────────

def create_post(session_id: str, data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO posts (session_id, template_id, aspect_ratio, topic, headline, hook, caption, cta, hashtags, image_path, category, brand_name, is_draft)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (session_id, data.get('template_id'), data.get('aspect_ratio', '4:5'),
               data.get('topic'), data.get('headline'), data.get('hook'),
               data.get('caption'), data.get('cta'),
               data.get('hashtags'), data.get('image_path'),
               data.get('category'), data.get('brand_name'),
               data.get('is_draft', 0)))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id


def get_posts(session_id: str, page: int = 1, limit: int = 12, is_draft: bool = False) -> dict:
    conn = get_conn()
    c = conn.cursor()
    offset = (page - 1) * limit
    draft_val = 1 if is_draft else 0
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ? AND is_draft = ?", (session_id, draft_val))
    total = c.fetchone()[0]

    c.execute("""SELECT id, template_id, aspect_ratio, topic, headline, hook, caption, cta, hashtags, image_path, category, brand_name, view_count, download_count, created_at
                  FROM posts WHERE session_id = ? AND is_draft = ?
                  ORDER BY created_at DESC LIMIT ? OFFSET ?""",
              (session_id, draft_val, limit, offset))
    rows = c.fetchall()
    conn.close()
    posts = []
    for r in rows:
        posts.append({
            "id": r[0], "template_id": r[1], "aspect_ratio": r[2], "topic": r[3],
            "headline": r[4], "hook": r[5], "caption": r[6], "cta": r[7],
            "hashtags": r[8], "image_path": r[9], "category": r[10],
            "brand_name": r[11], "view_count": r[12], "download_count": r[13],
            "created_at": r[14]
        })
    return {"posts": posts, "total": total, "page": page, "limit": limit,
            "total_pages": max(1, (total + limit - 1) // limit)}


def get_post(post_id: int) -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT id, template_id, aspect_ratio, topic, headline, hook, caption, cta, hashtags, image_path, category, brand_name, is_draft, view_count, download_count, created_at
                  FROM posts WHERE id = ?""", (post_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r[0], "template_id": r[1], "aspect_ratio": r[2], "topic": r[3],
        "headline": r[4], "hook": r[5], "caption": r[6], "cta": r[7],
        "hashtags": r[8], "image_path": r[9], "category": r[10],
        "brand_name": r[11], "is_draft": bool(r[12]), "view_count": r[13],
        "download_count": r[14], "created_at": r[15]
    }


def delete_post(post_id: int) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT image_path FROM posts WHERE id = ?", (post_id,))
    row = c.fetchone()
    if row and row[0]:
        import os
        if os.path.exists(row[0]):
            try:
                os.remove(row[0])
            except:
                pass
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ── Category Helpers ──────────────────────────────────────────────────────────

def get_categories() -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, key, description, prompt_hint, icon FROM content_categories")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "key": r[2], "description": r[3],
             "prompt_hint": r[4], "icon": r[5]} for r in rows]


# ── Analytics Helpers ─────────────────────────────────────────────────────────

def track_event(session_id: str, event_type: str, event_data: dict = None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO analytics (session_id, event_type, event_data) VALUES (?, ?, ?)",
              (session_id, event_type, json.dumps(event_data) if event_data else None))
    conn.commit()
    conn.close()


def get_analytics(session_id: str) -> dict:
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ? AND is_draft = 0", (session_id,))
    total_posts = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ? AND is_draft = 1", (session_id,))
    total_drafts = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(download_count), 0) FROM posts WHERE session_id = ?", (session_id,))
    total_downloads = c.fetchone()[0]

    c.execute("""SELECT template_id, COUNT(*) as cnt FROM posts 
                  WHERE session_id = ? AND is_draft = 0 GROUP BY template_id ORDER BY cnt DESC LIMIT 5""", (session_id,))
    template_usage = [{"template_id": r[0], "count": r[1]} for r in c.fetchall()]

    c.execute("""SELECT aspect_ratio, COUNT(*) as cnt FROM posts 
                  WHERE session_id = ? AND is_draft = 0 GROUP BY aspect_ratio""", (session_id,))
    ratio_usage = {r[0]: r[1] for r in c.fetchall()}

    c.execute("SELECT COUNT(*) FROM analytics WHERE session_id = ? AND event_type = 'generation'", (session_id,))
    generation_count = c.fetchone()[0]

    conn.close()
    return {
        "total_posts": total_posts,
        "total_drafts": total_drafts,
        "total_downloads": total_downloads,
        "template_usage": template_usage,
        "ratio_usage": ratio_usage,
        "generation_count": generation_count,
    }



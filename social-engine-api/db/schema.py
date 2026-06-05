"""
db/schema.py - Database schema initialization

Creates all required tables on first run and seeds default data.
"""
from db.connection import get_conn


def init_db():
    """Initialize database schema and seed default templates."""
    conn = get_conn()
    c = conn.cursor()

    # ── Users table ──────────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # ── Templates table ──────────────────────────────────────────────────────────
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

    # ── Template Elements table ──────────────────────────────────────────────
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

    # ── Posts table ───────────────────────────────────────────────────────────────
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
        brand_name TEXT,
        view_count INTEGER DEFAULT 0,
        download_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id),
        FOREIGN KEY (template_id) REFERENCES templates(id)
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

        # Story elements
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

    # ── Blog Posts table (AI SEO Blog Generator) ─────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        topic TEXT NOT NULL,
        primary_keyword TEXT DEFAULT '',
        title TEXT DEFAULT '',
        meta_title TEXT DEFAULT '',
        meta_description TEXT DEFAULT '',
        url_slug TEXT DEFAULT '',
        content TEXT DEFAULT '',
        word_count INTEGER DEFAULT 0,
        faq_questions TEXT DEFAULT '[]',
        internal_links TEXT DEFAULT '[]',
        seo_checklist TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES users(session_id)
    )''')

    conn.commit()
    conn.close()

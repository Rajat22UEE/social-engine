import sqlite3
import uuid
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Drop existing tables if they exist (fresh start for schema)
    c.execute('DROP TABLE IF EXISTS generation_sessions')
    c.execute('DROP TABLE IF EXISTS template_elements')
    c.execute('DROP TABLE IF EXISTS goals')
    c.execute('DROP TABLE IF EXISTS platforms')
    c.execute('DROP TABLE IF EXISTS canvas_edits')
    c.execute('DROP TABLE IF EXISTS brand_kits')
    c.execute('DROP TABLE IF EXISTS color_variations')
    c.execute('DROP TABLE IF EXISTS posts')
    c.execute('DROP TABLE IF EXISTS templates')
    c.execute('DROP TABLE IF EXISTS user_sessions')
    
    # 0. User Sessions table
    c.execute('''CREATE TABLE user_sessions
                 (session_id TEXT PRIMARY KEY,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  ip_address TEXT,
                  user_agent TEXT)''')
    
    # 0a. Platforms table
    c.execute('''CREATE TABLE platforms
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  key TEXT UNIQUE NOT NULL,
                  description TEXT,
                  icon TEXT,
                  max_headline_chars INTEGER DEFAULT 60,
                  max_hook_chars INTEGER DEFAULT 100,
                  text_density TEXT DEFAULT 'minimal')''')
    
    # 0b. Goals table
    c.execute('''CREATE TABLE goals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  key TEXT UNIQUE NOT NULL,
                  description TEXT,
                  template_style TEXT,
                  default_cta_style TEXT)''')
    
    # 0c. Brand Kits table
    c.execute('''CREATE TABLE brand_kits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_session_id TEXT UNIQUE NOT NULL,
                  brand_name TEXT,
                  logo_path TEXT,
                  logo_filename TEXT,
                  logo_filesize INTEGER,
                  primary_color_hex TEXT DEFAULT '#FFD700',
                  secondary_color_hex TEXT DEFAULT '#29BE71',
                  accent_color_hex TEXT DEFAULT '#64C8FF',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_session_id) REFERENCES user_sessions(session_id))''')
    
    # 0d. Color Variations table
    c.execute('''CREATE TABLE color_variations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  brand_kit_id INTEGER NOT NULL,
                  variation_name TEXT,
                  color_type TEXT,
                  hex_value TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (brand_kit_id) REFERENCES brand_kits(id))''')
    
    # 1. Templates table
    c.execute('''CREATE TABLE templates
                 (id INTEGER PRIMARY KEY, name TEXT, frame_size TEXT, config_json TEXT)''')
    
    # 1b. Template Elements table (TEMPLATE MAPPING ENGINE)
    c.execute('''CREATE TABLE template_elements
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  template_id INTEGER NOT NULL,
                  element_key TEXT NOT NULL,
                  x INTEGER NOT NULL,
                  y INTEGER NOT NULL,
                  font_size INTEGER DEFAULT 48,
                  max_lines INTEGER DEFAULT 2,
                  max_chars INTEGER,
                  alignment TEXT DEFAULT 'left',
                  color_hex TEXT,
                  FOREIGN KEY (template_id) REFERENCES templates(id))''')
    
    # 2. Posts table
    c.execute('''CREATE TABLE posts
                 (id INTEGER PRIMARY KEY, 
                  session_id TEXT,
                  brand_kit_id INTEGER,
                  platform_id INTEGER,
                  goal_id INTEGER,
                  topic TEXT, 
                  headline TEXT,
                  subheading TEXT,
                  hook TEXT, 
                  caption TEXT, 
                  cta TEXT, 
                  hashtags TEXT, 
                  image_path TEXT, 
                  template_id INTEGER,
                  template_platform TEXT,
                  industry TEXT,
                  tone TEXT,
                  target_audience TEXT,
                  liked BOOLEAN DEFAULT 0,
                  favorite BOOLEAN DEFAULT 0,
                  view_count INTEGER DEFAULT 0,
                  last_downloaded TIMESTAMP,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (session_id) REFERENCES user_sessions(session_id),
                  FOREIGN KEY (brand_kit_id) REFERENCES brand_kits(id),
                  FOREIGN KEY (platform_id) REFERENCES platforms(id),
                  FOREIGN KEY (goal_id) REFERENCES goals(id))''')
    
    # 2b. Canvas Edits table
    c.execute('''CREATE TABLE canvas_edits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  post_id INTEGER NOT NULL,
                  headline_x INTEGER,
                  headline_y INTEGER,
                  headline_size INTEGER,
                  headline_color TEXT,
                  hook_x INTEGER,
                  hook_y INTEGER,
                  hook_size INTEGER,
                  hook_color TEXT,
                  caption_x INTEGER,
                  caption_y INTEGER,
                  caption_size INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (post_id) REFERENCES posts(id))''')
    
    # 2c. Generation Sessions table (tracks full workflow)
    c.execute('''CREATE TABLE generation_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT NOT NULL,
                  platform_id INTEGER,
                  goal_id INTEGER,
                  topic TEXT,
                  industry TEXT,
                  target_audience TEXT,
                  tone TEXT DEFAULT 'professional',
                  cta_text TEXT,
                  template_id INTEGER,
                  brand_kit_id INTEGER,
                  content_angle TEXT,
                  status TEXT DEFAULT 'draft',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (session_id) REFERENCES user_sessions(session_id),
                  FOREIGN KEY (platform_id) REFERENCES platforms(id),
                  FOREIGN KEY (goal_id) REFERENCES goals(id),
                  FOREIGN KEY (template_id) REFERENCES templates(id),
                  FOREIGN KEY (brand_kit_id) REFERENCES brand_kits(id))''')
    
    # ── SEED DATA ────────────────────────────────────────────────────────────────
    
    # Platforms
    c.execute("""INSERT INTO platforms (name, key, description, icon, max_headline_chars, max_hook_chars, text_density)
                 VALUES ('Instagram', 'instagram', 'Visual-first, short hooks, emotional triggers', '📸', 50, 80, 'minimal')""")
    c.execute("""INSERT INTO platforms (name, key, description, icon, max_headline_chars, max_hook_chars, text_density)
                 VALUES ('LinkedIn', 'linkedin', 'Professional, authority-driven, business pain points', '💼', 80, 120, 'medium')""")
    c.execute("""INSERT INTO platforms (name, key, description, icon, max_headline_chars, max_hook_chars, text_density)
                 VALUES ('Twitter / X', 'twitter', 'Ultra-concise, witty, conversation starters', '🐦', 40, 60, 'minimal')""")
    c.execute("""INSERT INTO platforms (name, key, description, icon, max_headline_chars, max_hook_chars, text_density)
                 VALUES ('Facebook', 'facebook', 'Conversational, community tone, slightly longer', '📘', 70, 120, 'medium')""")
    
    # Goals
    c.execute("""INSERT INTO goals (name, key, description, template_style, default_cta_style)
                 VALUES ('Engagement', 'engagement', 'Spark conversations and build community', 'hook-focused', 'question')""")
    c.execute("""INSERT INTO goals (name, key, description, template_style, default_cta_style)
                 VALUES ('Educational', 'educational', 'Share knowledge and establish expertise', 'value-driven', 'learn-more')""")
    c.execute("""INSERT INTO goals (name, key, description, template_style, default_cta_style)
                 VALUES ('Promotional', 'promotional', 'Highlight offers and drive conversions', 'cta-heavy', 'shop-now')""")
    c.execute("""INSERT INTO goals (name, key, description, template_style, default_cta_style)
                 VALUES ('Authority', 'authority', 'Build thought leadership and credibility', 'data-driven', 'read-more')""")
    c.execute("""INSERT INTO goals (name, key, description, template_style, default_cta_style)
                 VALUES ('Motivational', 'motivational', 'Inspire action with aspirational messaging', 'emotional', 'join-now')""")
    
    # Template images (5 templates)
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (1, 'Standard Portrait', '1254x1254', '{"text_x": 50, "text_y": 200}')""")
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (2, 'Stories / Portrait', '941x1672', '{"text_x": 50, "text_y": 200}')""")
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (3, 'LinkedIn Landscape', '1200x628', '{"text_x": 50, "text_y": 100}')""")
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (4, 'Twitter / X Post', '1024x512', '{"text_x": 50, "text_y": 100}')""")
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (5, 'Pinterest Tall', '1000x1500', '{"text_x": 50, "text_y": 200}')""")
    
    # Template Elements for all 5 templates
    # Template 1 (Square 1254x1254) - Headline + Hook + CTA
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (1, 'headline', 64, 350, 90, 1, 50, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (1, 'hook', 64, 500, 48, 2, 80, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (1, 'cta', 64, 1050, 40, 1, 30, 'center')""")
    
    # Template 2 (Stories 941x1672) - Headline + Hook + CTA
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (2, 'headline', 50, 500, 72, 1, 40, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (2, 'hook', 50, 650, 40, 2, 80, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (2, 'cta', 50, 1400, 36, 1, 30, 'center')""")
    
    # Template 3 (LinkedIn 1200x628) - Headline + Hook + Subheading
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (3, 'headline', 60, 100, 64, 2, 80, 'left')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (3, 'subheading', 60, 280, 36, 2, 100, 'left')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (3, 'cta', 60, 450, 32, 1, 30, 'left')""")
    
    # Template 4 (Twitter 1024x512) - Headline + Hook
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (4, 'headline', 50, 80, 56, 2, 40, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (4, 'hook', 50, 250, 32, 2, 60, 'center')""")
    
    # Template 5 (Pinterest 1000x1500) - Headline + Hook + CTA
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (5, 'headline', 55, 350, 68, 1, 50, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (5, 'hook', 55, 500, 38, 2, 80, 'center')""")
    c.execute("""INSERT INTO template_elements (template_id, element_key, x, y, font_size, max_lines, max_chars, alignment)
                 VALUES (5, 'cta', 55, 1300, 36, 1, 30, 'center')""")
    
    conn.commit()
    conn.close()


# ── Session Helpers ────────────────────────────────────────────────────────────

def create_session(session_id: str, ip_address: str = None, user_agent: str = None) -> str:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO user_sessions (session_id, ip_address, user_agent) 
                 VALUES (?, ?, ?)""",
              (session_id, ip_address, user_agent))
    conn.commit()
    conn.close()
    return session_id

def get_session(session_id: str) -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT session_id, created_at, last_activity, ip_address, user_agent FROM user_sessions WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "session_id": row[0],
            "created_at": row[1],
            "last_activity": row[2],
            "ip_address": row[3],
            "user_agent": row[4]
        }
    return None

def update_session_activity(session_id: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


# ── Brand Kit Helpers ──────────────────────────────────────────────────────────

def get_brand_kit(session_id: str) -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT id, user_session_id, brand_name, logo_path, logo_filename, logo_filesize, 
                  primary_color_hex, secondary_color_hex, accent_color_hex, created_at, updated_at
                  FROM brand_kits WHERE user_session_id = ?""", (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "user_session_id": row[1],
            "brand_name": row[2],
            "logo_path": row[3],
            "logo_filename": row[4],
            "logo_filesize": row[5],
            "primary_color": row[6],
            "secondary_color": row[7],
            "accent_color": row[8],
            "created_at": row[9],
            "updated_at": row[10]
        }
    return None

def upsert_brand_kit(session_id: str, data: dict) -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    existing = get_brand_kit(session_id)
    if existing:
        updates = []
        params = []
        for field, db_col in [
            ('brand_name', 'brand_name'),
            ('logo_path', 'logo_path'),
            ('logo_filename', 'logo_filename'),
            ('logo_filesize', 'logo_filesize'),
            ('primary_color', 'primary_color_hex'),
            ('secondary_color', 'secondary_color_hex'),
            ('accent_color', 'accent_color_hex'),
        ]:
            if field in data and data[field] is not None:
                updates.append(f"{db_col} = ?")
                params.append(data[field])
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(session_id)
            c.execute(f"UPDATE brand_kits SET {', '.join(updates)} WHERE user_session_id = ?", params)
    else:
        c.execute("""INSERT INTO brand_kits 
                      (user_session_id, brand_name, logo_path, logo_filename, logo_filesize,
                       primary_color_hex, secondary_color_hex, accent_color_hex)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (session_id, data.get('brand_name'), data.get('logo_path'),
                   data.get('logo_filename'), data.get('logo_filesize'),
                   data.get('primary_color', '#FFD700'),
                   data.get('secondary_color', '#29BE71'),
                   data.get('accent_color', '#64C8FF')))
    conn.commit()
    conn.close()
    return get_brand_kit(session_id)

def delete_brand_kit(session_id: str) -> bool:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM brand_kits WHERE user_session_id = ?", (session_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ── Platform & Goal Helpers ───────────────────────────────────────────────────

def get_platforms() -> list:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, key, description, icon, max_headline_chars, max_hook_chars, text_density FROM platforms")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "key": r[2], "description": r[3],
             "icon": r[4], "max_headline_chars": r[5], "max_hook_chars": r[6],
             "text_density": r[7]} for r in rows]

def get_goals() -> list:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, key, description, template_style, default_cta_style FROM goals")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "key": r[2], "description": r[3],
             "template_style": r[4], "default_cta_style": r[5]} for r in rows]

def get_template_elements(template_id: int) -> list:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT id, element_key, x, y, font_size, max_lines, max_chars, alignment, color_hex
                  FROM template_elements WHERE template_id = ? ORDER BY y ASC""", (template_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "element_key": r[1], "x": r[2], "y": r[3],
             "font_size": r[4], "max_lines": r[5], "max_chars": r[6],
             "alignment": r[7], "color_hex": r[8]} for r in rows]

def create_generation_session(session_id: str, data: dict) -> int:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO generation_sessions 
                  (session_id, platform_id, goal_id, topic, industry, target_audience, tone, cta_text, template_id, brand_kit_id, content_angle)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (session_id, data.get('platform_id'), data.get('goal_id'),
               data.get('topic'), data.get('industry'), data.get('target_audience'),
               data.get('tone', 'professional'), data.get('cta_text'),
               data.get('template_id'), data.get('brand_kit_id'), data.get('content_angle')))
    gen_id = c.lastrowid
    conn.commit()
    conn.close()
    return gen_id


# ── Canvas Edit Helpers ──────────────────────────────────────────────────────

def save_canvas_edit(post_id: int, edits: dict) -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id FROM canvas_edits WHERE post_id = ?", (post_id,))
    existing = c.fetchone()
    fields = ['headline_x', 'headline_y', 'headline_size', 'headline_color',
              'hook_x', 'hook_y', 'hook_size', 'hook_color',
              'caption_x', 'caption_y', 'caption_size']
    if existing:
        updates = []
        params = []
        for f in fields:
            if f in edits and edits[f] is not None:
                updates.append(f"{f} = ?")
                params.append(edits[f])
        if updates:
            params.append(post_id)
            c.execute(f"UPDATE canvas_edits SET {', '.join(updates)} WHERE post_id = ?", params)
    else:
        cols = ['post_id'] + [f for f in fields if f in edits and edits[f] is not None]
        vals = [post_id] + [edits[f] for f in fields if f in edits and edits[f] is not None]
        placeholders = ', '.join(['?'] * len(cols))
        c.execute(f"INSERT INTO canvas_edits ({', '.join(cols)}) VALUES ({placeholders})", vals)
    conn.commit()
    conn.close()
    return get_canvas_edit(post_id)

def get_canvas_edit(post_id: int) -> dict:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT id, post_id, headline_x, headline_y, headline_size, headline_color,
                  hook_x, hook_y, hook_size, hook_color,
                  caption_x, caption_y, caption_size, created_at
                  FROM canvas_edits WHERE post_id = ?""", (post_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "post_id": row[1],
            "headline_x": row[2], "headline_y": row[3],
            "headline_size": row[4], "headline_color": row[5],
            "hook_x": row[6], "hook_y": row[7],
            "hook_size": row[8], "hook_color": row[9],
            "caption_x": row[10], "caption_y": row[11],
            "caption_size": row[12], "created_at": row[13]
        }
    return {}

def delete_canvas_edit(post_id: int) -> bool:
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM canvas_edits WHERE post_id = ?", (post_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

if __name__ == "__main__":
    init_db()
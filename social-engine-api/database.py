import sqlite3


DATABASE_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def init_db():

    conn = get_connection()
    c = conn.cursor()

    # =========================================
    # 1. TEMPLATES TABLE
    # =========================================

    c.execute("""
    CREATE TABLE IF NOT EXISTS templates
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        frame_size TEXT,

        config_json TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =========================================
    # 2. POSTS TABLE
    # =========================================

    c.execute("""
    CREATE TABLE IF NOT EXISTS posts
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        topic TEXT,

        caption TEXT,

        hashtags TEXT,

        image_path TEXT,

        template_id INTEGER,

        platform TEXT,

        status TEXT DEFAULT 'draft',

        scheduled_at TIMESTAMP,

        published_at TIMESTAMP,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(template_id) REFERENCES templates(id)
    )
    """)

    # =========================================
    # 3. SCHEDULED POSTS TABLE
    # =========================================

    c.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_posts
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        post_id INTEGER NOT NULL,

        scheduled_time TIMESTAMP NOT NULL,

        status TEXT DEFAULT 'pending',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(post_id) REFERENCES posts(id)
    )
    """)

    # =========================================
    # 4. PUBLISHING HISTORY TABLE
    # =========================================

    c.execute("""
    CREATE TABLE IF NOT EXISTS publishing_history
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        post_id INTEGER,

        platform TEXT,

        status TEXT,

        response TEXT,

        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(post_id) REFERENCES posts(id)
    )
    """)

    # =========================================
    # 5. INSERT DEFAULT TEMPLATE
    # =========================================

    c.execute("""
    INSERT OR IGNORE INTO templates
    (
        id,
        name,
        frame_size,
        config_json
    )
    VALUES
    (
        1,
        'Standard Portrait',
        '1080x1350',
        '{"text_x": 50, "text_y": 200}'
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully!")


# =========================================
# TEST CONNECTION
# =========================================

def test_db():

    conn = get_connection()

    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")

    tables = c.fetchall()

    print("\nTables Created:\n")

    for table in tables:
        print(table[0])

    conn.close()


# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    init_db()

    print("Database initialized successfully!")
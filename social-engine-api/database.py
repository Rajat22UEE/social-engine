import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 1. Create Templates table
    c.execute('''CREATE TABLE IF NOT EXISTS templates
                 (id INTEGER PRIMARY KEY, name TEXT, frame_size TEXT, config_json TEXT)''')
    
    # 2. Create/Update Posts table
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY, topic TEXT, caption TEXT, hashtags TEXT, 
                  image_path TEXT, template_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # 3. Seed initial template
    c.execute("""INSERT OR IGNORE INTO templates (id, name, frame_size, config_json) 
                 VALUES (1, 'Standard Portrait', '1080x1350', '{"text_x": 50, "text_y": 200}')""")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
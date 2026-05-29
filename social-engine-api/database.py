import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Drop existing tables if they exist (fresh start for schema)
    c.execute('DROP TABLE IF EXISTS posts')
    c.execute('DROP TABLE IF EXISTS templates')
    
    # 1. Create Templates table
    c.execute('''CREATE TABLE templates
                 (id INTEGER PRIMARY KEY, name TEXT, frame_size TEXT, config_json TEXT)''')
    
    # 2. Create Posts table with structured fields
    c.execute('''CREATE TABLE posts
                 (id INTEGER PRIMARY KEY, topic TEXT, headline TEXT, hook TEXT, caption TEXT, 
                  cta TEXT, hashtags TEXT, image_path TEXT, template_id INTEGER, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # 3. Seed initial templates
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (1, 'Standard Portrait', '1254x1254', '{"text_x": 50, "text_y": 200}')""")
    c.execute("""INSERT INTO templates (id, name, frame_size, config_json) 
                 VALUES (2, 'Stories / Portrait', '941x1672', '{"text_x": 50, "text_y": 200}')""")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
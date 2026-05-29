print("CRUD FILE LOADED")
import sqlite3

DATABASE_NAME = "database.db"


# =========================================
# DATABASE CONNECTION
# =========================================

def get_connection():

    conn = sqlite3.connect(DATABASE_NAME)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================
# CREATE POST
# =========================================

def create_post(data):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    INSERT INTO posts
    (
        topic,
        caption,
        hashtags,
        image_path,
        template_id,
        platform,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        data.get("topic"),
        data.get("caption"),
        data.get("hashtags"),
        data.get("image_path"),
        data.get("template_id"),
        data.get("platform"),
        "draft"

    ))

    conn.commit()

    post_id = c.lastrowid

    conn.close()

    return {
        "message": "Post created successfully",
        "post_id": post_id
    }


# =========================================
# GET ALL POSTS
# =========================================

def get_posts():

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM posts
    ORDER BY created_at DESC
    """)

    posts = [dict(row) for row in c.fetchall()]

    conn.close()

    return posts


# =========================================
# GET SINGLE POST
# =========================================

def get_post(post_id):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM posts
    WHERE id = ?
    """, (post_id,))

    post = c.fetchone()

    conn.close()

    if post:

        return dict(post)

    return {
        "message": "Post not found"
    }



# =========================================
# UPDATE POST
# =========================================

def update_post(post_id, data):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    UPDATE posts
    SET
        topic = ?,
        caption = ?,
        hashtags = ?,
        image_path = ?,
        template_id = ?,
        platform = ?,
        status = ?,
        published_at = ?
    WHERE id = ?
    """, (

        data.get("topic"),
        data.get("caption"),
        data.get("hashtags"),
        data.get("image_path"),
        data.get("template_id"),
        data.get("platform"),
        data.get("status"),
        data.get("published_at"),
        post_id

    ))

    conn.commit()

    conn.close()

    return {
        "message": "Post updated successfully"
    }



# =========================================
# DELETE POST
# =========================================

def delete_post(post_id):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    DELETE FROM posts
    WHERE id = ?
    """, (post_id,))

    conn.commit()

    conn.close()

    return {
        "message": "Post deleted successfully"
    }


# =========================================
# SCHEDULE POST
# =========================================

def schedule_post(data):

    conn = get_connection()

    c = conn.cursor()

    # INSERT INTO scheduled_posts
    c.execute("""
    INSERT INTO scheduled_posts
    (
        post_id,
        scheduled_time,
        status
    )
    VALUES (?, ?, ?)
    """, (

        data.get("post_id"),
        data.get("scheduled_time"),
        "pending"

    ))

    # UPDATE posts TABLE
    c.execute("""
    UPDATE posts
    SET
        status = ?,
        scheduled_at = ?
    WHERE id = ?
    """, (

        "scheduled",
        data.get("scheduled_time"),
        data.get("post_id")

    ))

    conn.commit()

    schedule_id = c.lastrowid

    conn.close()

    return {
        "message": "Post scheduled successfully",
        "schedule_id": schedule_id
    }


# =========================================
# GET ALL SCHEDULED POSTS
# =========================================

def get_scheduled_posts():

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM scheduled_posts
    ORDER BY scheduled_time ASC
    """)

    posts = [dict(row) for row in c.fetchall()]

    conn.close()

    return posts


# =========================================
# GET SINGLE SCHEDULED POST
# =========================================

def get_scheduled_post(schedule_id):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM scheduled_posts
    WHERE id = ?
    """, (schedule_id,))

    post = c.fetchone()

    conn.close()

    if post:

        return dict(post)

    return {
        "message": "Scheduled post not found"
    }


# =========================================
# UPDATE SCHEDULED POST
# =========================================

def update_scheduled_post(schedule_id, data):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    UPDATE scheduled_posts
    SET
        scheduled_time = ?,
        status = ?
    WHERE id = ?
    """, (

        data.get("scheduled_time"),
        data.get("status"),
        schedule_id

    ))

    conn.commit()

    conn.close()

    return {
        "message": "Scheduled post updated successfully"
    }


# =========================================
# DELETE SCHEDULED POST
# =========================================

def delete_scheduled_post(schedule_id):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    DELETE FROM scheduled_posts
    WHERE id = ?
    """, (schedule_id,))

    conn.commit()

    conn.close()

    return {
        "message": "Scheduled post deleted successfully"
    }



# =========================================
# CREATE PUBLISHING HISTORY
# =========================================

def create_publishing_history(data):

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    INSERT INTO publishing_history
    (
        post_id,
        platform,
        status,
        response
    )
    VALUES (?, ?, ?, ?)
    """, (

        data.get("post_id"),
        data.get("platform"),
        data.get("status"),
        data.get("response")

    ))

    conn.commit()

    history_id = c.lastrowid

    conn.close()

    return {
        "message": "Publishing history saved",
        "history_id": history_id
    }



# =========================================
# GET PUBLISHING HISTORY
# =========================================

def get_publishing_history():

    conn = get_connection()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM publishing_history
    ORDER BY published_at DESC
    """)

    history = [dict(row) for row in c.fetchall()]

    conn.close()

    return history
"""
db/posts.py - Post & Draft database operations

CRUD and pagination for generated posts and drafts.
"""
import os
from db.connection import get_conn


def get_posts(session_id: str, page: int = 1, limit: int = 12) -> dict:
    """
    Fetch paginated list of posts for a session.
    Returns dict with 'posts' list, 'total', 'page', 'limit', 'pages'.
    """
    conn = get_conn()
    c = conn.cursor()

    # Count total
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ?", (session_id,))
    total = c.fetchone()[0]

    # Paginated fetch
    offset = (page - 1) * limit
    c.execute("""SELECT id, template_id, aspect_ratio, topic, headline, hook,
                  caption, cta, hashtags, image_path, brand_name,
                  view_count, download_count, created_at
                  FROM posts WHERE session_id = ?
                  ORDER BY created_at DESC LIMIT ? OFFSET ?""",
              (session_id, limit, offset))
    rows = c.fetchall()
    conn.close()

    posts = []
    for r in rows:
        posts.append({
            "id": r[0], "template_id": r[1], "aspect_ratio": r[2], "topic": r[3],
            "headline": r[4], "hook": r[5], "caption": r[6], "cta": r[7],
            "hashtags": r[8], "image_path": r[9], "brand_name": r[10],
            "view_count": r[11],
            "download_count": r[12], "created_at": r[13]
        })

    pages = (total + limit - 1) // limit if limit > 0 else 1
    return {"posts": posts, "total": total, "page": page, "limit": limit, "pages": pages}


def create_post(session_id: str, data: dict) -> int:
    """
    Create a new post record and return its ID.
    Accepts: template_id, aspect_ratio, topic, headline, hook, caption,
             cta, hashtags, image_path, brand_name
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO posts
        (session_id, template_id, aspect_ratio, topic, headline, hook,
         caption, cta, hashtags, image_path, brand_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (session_id,
               data.get('template_id'), data.get('aspect_ratio', '4:5'),
               data.get('topic'), data.get('headline'), data.get('hook'),
               data.get('caption'), data.get('cta'),
               data.get('hashtags'), data.get('image_path'),
               data.get('brand_name')))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id


def get_post(post_id: int) -> dict:
    """Fetch a single post by ID. Returns None if not found."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT id, template_id, aspect_ratio, topic, headline, hook,
                  caption, cta, hashtags, image_path, brand_name,
                  view_count, download_count, created_at
                  FROM posts WHERE id = ?""", (post_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r[0], "template_id": r[1], "aspect_ratio": r[2], "topic": r[3],
        "headline": r[4], "hook": r[5], "caption": r[6], "cta": r[7],
        "hashtags": r[8], "image_path": r[9], "brand_name": r[10],
        "view_count": r[11],
        "download_count": r[12], "created_at": r[13]
    }


def increment_download_count(post_id: int):
    """Increment the download counter for a post."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE posts SET download_count = download_count + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()


# ── Blog Posts (AI SEO Blog Generator) ─────────────────────────────────────────


def create_blog_post(session_id: str, data: dict) -> int:
    """Create a new blog post record and return its ID."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO blog_posts
        (session_id, topic, primary_keyword, title, meta_title,
         meta_description, url_slug, content, word_count,
         faq_questions, internal_links, seo_checklist)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (session_id,
               data.get("topic", ""),
               data.get("primary_keyword", ""),
               data.get("title", ""),
               data.get("meta_title", ""),
               data.get("meta_description", ""),
               data.get("url_slug", ""),
               data.get("content", ""),
               data.get("word_count", 0),
               data.get("faq_questions", "[]"),
               data.get("internal_links", "[]"),
               data.get("seo_checklist", "[]")))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id


def get_blog_post(post_id: int) -> dict:
    """Fetch a single blog post by ID. Returns None if not found."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT id, session_id, topic, primary_keyword, title,
                  meta_title, meta_description, url_slug, content, word_count,
                  faq_questions, internal_links, seo_checklist, created_at, updated_at
                  FROM blog_posts WHERE id = ?""", (post_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r[0],
        "session_id": r[1],
        "topic": r[2],
        "primary_keyword": r[3],
        "title": r[4],
        "meta_title": r[5],
        "meta_description": r[6],
        "url_slug": r[7],
        "content": r[8],
        "word_count": r[9],
        "faq_questions": r[10],
        "internal_links": r[11],
        "seo_checklist": r[12],
        "created_at": r[13],
        "updated_at": r[14]
    }


def get_user_blog_posts(session_id: str, page: int = 1, limit: int = 12) -> dict:
    """Fetch paginated list of blog posts for a session."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM blog_posts WHERE session_id = ?", (session_id,))
    total = c.fetchone()[0]
    offset = (page - 1) * limit
    c.execute("""SELECT id, topic, primary_keyword, title, word_count, created_at
                  FROM blog_posts WHERE session_id = ?
                  ORDER BY created_at DESC LIMIT ? OFFSET ?""",
              (session_id, limit, offset))
    rows = c.fetchall()
    conn.close()
    posts = []
    for r in rows:
        posts.append({
            "id": r[0], "topic": r[1], "primary_keyword": r[2],
            "title": r[3], "word_count": r[4], "created_at": r[5]
        })
    pages = (total + limit - 1) // limit if limit > 0 else 1
    return {"posts": posts, "total": total, "page": page, "limit": limit, "pages": pages}

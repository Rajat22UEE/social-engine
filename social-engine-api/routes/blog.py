"""
routes/blog.py - AI SEO Blog Generator endpoints

POST /api/blog/generate      - Generate full SEO blog from topic
GET  /api/blog/{id}          - Retrieve a saved blog post
GET  /api/blog/{id}/download - Download blog as .md file
"""
import json
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from models.schemas import BlogGenerateRequest, BlogGenerateResponse
from services.seo_blog import generate_blog
from db.posts import create_blog_post, get_blog_post

router = APIRouter()


@router.post("/api/blog/generate")
async def generate_blog_endpoint(request: Request, data: BlogGenerateRequest):
    """
    Generate a complete SEO-optimized blog post for a given topic.

    Flow:
      1. Call Gemini via seo_blog service (8-step framework)
      2. Save full response to blog_posts table
      3. Return structured blog response
    """
    try:
        session_id = request.state.session_id
        topic = data.topic.strip()

        if not topic:
            return {"error": "Topic is required"}

        # Generate blog via Gemini (8-step framework)
        blog_data = generate_blog(topic)

        # Prepare data for DB storage
        db_data = {
            "topic": topic,
            "primary_keyword": blog_data.get("primary_keyword", ""),
            "title": blog_data.get("title", ""),
            "meta_title": blog_data.get("meta_title", ""),
            "meta_description": blog_data.get("meta_description", ""),
            "url_slug": blog_data.get("url_slug", ""),
            "content": blog_data.get("content", ""),
            "word_count": blog_data.get("word_count", 0),
            "faq_questions": json.dumps(blog_data.get("faq_questions", [])),
            "internal_links": json.dumps(blog_data.get("internal_links", [])),
            "seo_checklist": json.dumps(blog_data.get("seo_checklist", [])),
        }

        # Save to database
        post_id = create_blog_post(session_id, db_data)

        # Build response
        response_data = BlogGenerateResponse(
            id=post_id,
            title=blog_data.get("title", ""),
            meta_title=blog_data.get("meta_title", ""),
            meta_description=blog_data.get("meta_description", ""),
            url_slug=blog_data.get("url_slug", ""),
            primary_keyword=blog_data.get("primary_keyword", ""),
            secondary_keywords=blog_data.get("secondary_keywords", []),
            content=blog_data.get("content", ""),
            word_count=blog_data.get("word_count", 0),
            faq_questions=blog_data.get("faq_questions", []),
            internal_links=blog_data.get("internal_links", []),
            seo_checklist=blog_data.get("seo_checklist", []),
        )

        return response_data.model_dump()

    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response: {str(e)}"}
    except Exception as e:
        return {"error": f"Blog generation failed: {str(e)}"}


@router.get("/api/blog/{post_id}")
async def get_blog_endpoint(post_id: int):
    """Retrieve a previously generated blog post by ID."""
    try:
        blog = get_blog_post(post_id)
        if not blog:
            return {"error": "Blog post not found"}

        # Parse JSON fields
        faq_questions = json.loads(blog.get("faq_questions", "[]"))
        internal_links = json.loads(blog.get("internal_links", "[]"))
        seo_checklist = json.loads(blog.get("seo_checklist", "[]"))

        return {
            "id": blog["id"],
            "topic": blog["topic"],
            "title": blog["title"],
            "meta_title": blog["meta_title"],
            "meta_description": blog["meta_description"],
            "url_slug": blog["url_slug"],
            "primary_keyword": blog["primary_keyword"],
            "content": blog["content"],
            "word_count": blog["word_count"],
            "faq_questions": faq_questions,
            "internal_links": internal_links,
            "seo_checklist": seo_checklist,
            "created_at": blog["created_at"],
        }

    except Exception as e:
        return {"error": f"Failed to retrieve blog: {str(e)}"}


@router.get("/api/blog/{post_id}/download")
async def download_blog_endpoint(post_id: int):
    """Download a generated blog post as a .md file."""
    try:
        blog = get_blog_post(post_id)
        if not blog:
            return {"error": "Blog post not found"}

        # Build full markdown with frontmatter
        meta = blog.get("meta_title", "")
        desc = blog.get("meta_description", "")
        slug = blog.get("url_slug", "")
        kw = blog.get("primary_keyword", "")

        frontmatter = f"""---
title: "{blog.get('title', '')}"
meta_title: "{meta}"
description: "{desc}"
slug: "{slug}"
primary_keyword: "{kw}"
word_count: {blog.get('word_count', 0)}
generated_by: "Kyma AI - AI SEO Blog Generator"
---

"""
        full_md = frontmatter + blog.get("content", "")

        filename = slug.replace("/blog/", "").replace("/", "-") or f"blog-{post_id}"
        if not filename.endswith(".md"):
            filename += ".md"

        return PlainTextResponse(
            content=full_md,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        return {"error": f"Failed to download blog: {str(e)}"}
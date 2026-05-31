from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os
import json
import uuid
import time
from tenacity import retry, wait_exponential, stop_after_attempt
import sqlite3
from database import (init_db, get_or_create_user, get_templates, get_template,
                      create_template, update_template, delete_template,
                      create_post, get_posts, get_post, delete_post,
                      get_categories, track_event, get_analytics)
from generators import generate_post_image

load_dotenv()
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads/logos", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# ── Session Middleware ─────────────────────────────────────────────────────────
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    if request.url.path.startswith("/outputs") or request.url.path.startswith("/uploads"):
        return await call_next(request)

    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    # Ensure user exists in DB
    get_or_create_user(session_id)
    request.state.session_id = session_id

    response = await call_next(request)
    response.set_cookie(key="session_id", value=session_id, max_age=30*24*60*60,
                        httponly=True, samesite="lax")
    return response


# ── Pydantic Models ────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    topic: str
    template_id: int = 1
    aspect_ratio: str = '4:5'
    category: str = None
    brand_name: str = None
    cta_text: str = None

class TemplateCreate(BaseModel):
    name: str
    aspect_ratio: str = '4:5'
    width: int = 1080
    height: int = 1350
    elements: list = []

class TemplateUpdate(BaseModel):
    name: str = None
    aspect_ratio: str = None
    width: int = None
    height: int = None
    elements: list = None

class PostDraftRequest(BaseModel):
    template_id: int
    aspect_ratio: str = '4:5'
    topic: str = None
    headline: str = None
    hook: str = None
    caption: str = None
    cta: str = None
    hashtags: str = None
    image_path: str = None
    category: str = None
    brand_name: str = None

# ── Gemini Client ──────────────────────────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CATEGORY_PROMPTS = {
    'educational': 'Educational content — share knowledge and industry insights.',
    'promotional': 'Promotional content — highlight value proposition and CTA.',
    'case_study': 'Case study — present before/after or problem/solution narrative.',
    'engagement': 'Engagement content — ask questions, spark conversations.',
    'branding': 'Branding content — company intro, culture, team spotlight.',
    'testimonial': 'Testimonial — showcase customer reviews and social proof.',
    'event': 'Event promotion — create urgency, highlight event details.',
    'quote': 'Quote — inspirational or thought leadership statement.',
}

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(3))
def call_gemini(topic: str, category: str = None, brand_name: str = None, cta_text: str = None) -> dict:
    """Generate Instagram marketing content with AI."""
    cat_instruction = CATEGORY_PROMPTS.get(category, 'Professional business promotion content.')
    brand_instruction = f"Brand: {brand_name}. " if brand_name else ""
    cta_instruction = f"CTA: {cta_text}. " if cta_text else ""

    prompt = f"""You are a professional Instagram content creator for business brands.
Your tone is professional, polished, and business-focused.

{cat_instruction}
{brand_instruction}
{cta_instruction}
Topic: {topic}

Generate Instagram-optimized content. Return ONLY valid JSON (no markdown, no backticks):
{{
  "headline": "Short engaging headline (max 8 words)",
  "hook": "Attention-grabbing first line (1 sentence)",
  "caption": "Main body text (2-3 short sentences for business promotion)",
  "cta": "Clear call-to-action ({cta_text if cta_text else 'Visit, Learn More, Sign Up, Shop Now'})",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text[text.find("{"):text.rfind("}")+1]
    return json.loads(text)


# ── Session / User Endpoints ───────────────────────────────────────────────────

@app.get("/api/session")
async def get_session(request: Request):
    session_id = request.state.session_id
    user = get_or_create_user(session_id)
    return {"status": "success", "session_id": session_id, "user": user}


# ── Template Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/templates")
async def list_templates(request: Request):
    session_id = request.state.session_id
    templates = get_templates(session_id)
    return {"status": "success", "templates": templates}

@app.get("/api/templates/{template_id}")
async def get_template_endpoint(template_id: int):
    template = get_template(template_id)
    if not template:
        return {"error": "Template not found"}
    return {"status": "success", "template": template}

@app.post("/api/templates")
async def create_template_endpoint(request: Request, data: TemplateCreate):
    session_id = request.state.session_id
    template = create_template(session_id, data.dict())
    return {"status": "success", "template": template}

@app.post("/api/templates/{template_id}/duplicate")
async def duplicate_template_endpoint(request: Request, template_id: int):
    """Duplicate an existing template (user-created or default)."""
    session_id = request.state.session_id
    original = get_template(template_id)
    if not original:
        return {"error": "Template not found"}
    dup = create_template(session_id, {
        "name": f"{original['name']} (Copy)",
        "aspect_ratio": original["aspect_ratio"],
        "width": original["width"],
        "height": original["height"],
        "elements": [{"element_key": e["element_key"], "x": e["x"], "y": e["y"],
                       "font_size": e["font_size"], "font_family": e.get("font_family", "Poppins"),
                       "color_hex": e.get("color_hex", "#1A2A4A"),
                       "max_chars": e.get("max_chars"), "max_lines": e.get("max_lines", 2),
                       "alignment": e.get("alignment", "center"),
                       "background_color_hex": e.get("background_color_hex")}
                      for e in original.get("elements", [])]
    })
    return {"status": "success", "template": dup}

@app.put("/api/templates/{template_id}")
async def update_template_endpoint(template_id: int, data: TemplateUpdate):
    template = update_template(template_id, data.dict(exclude_none=True))
    if not template:
        return {"error": "Template not found"}
    return {"status": "success", "template": template}

@app.delete("/api/templates/{template_id}")
async def delete_template_endpoint(template_id: int):
    deleted = delete_template(template_id)
    if not deleted:
        return {"error": "Template not found or is default"}
    return {"status": "success", "message": "Template deleted"}


# ── Content Generation Endpoint ───────────────────────────────────────────────

@app.post("/api/generate")
async def generate_post_endpoint(request: Request, data: GenerateRequest):
    """Generate Instagram content + image."""
    try:
        start_time = time.time()
        session_id = request.state.session_id

        # Get template to check aspect ratio
        template = get_template(data.template_id)
        if not template:
            return {"error": "Template not found"}
        aspect_ratio = template.get("aspect_ratio", data.aspect_ratio)

        # Generate AI content
        content_data = call_gemini(
            topic=data.topic,
            category=data.category,
            brand_name=data.brand_name,
            cta_text=data.cta_text
        )

        # Generate image
        image_path = generate_post_image(
            data.template_id, data.topic, content_data
        )

        # Store in DB
        hashtags_json = json.dumps(content_data.get("hashtags", []))
        post_id = create_post(session_id, {
            "template_id": data.template_id,
            "aspect_ratio": aspect_ratio,
            "topic": data.topic,
            "headline": content_data.get("headline", ""),
            "hook": content_data.get("hook", ""),
            "caption": content_data.get("caption", ""),
            "cta": content_data.get("cta", ""),
            "hashtags": hashtags_json,
            "image_path": image_path,
            "category": data.category,
            "brand_name": data.brand_name,
            "is_draft": 0,
        })

        # Track analytics
        track_event(session_id, "generation", {
            "template_id": data.template_id,
            "aspect_ratio": aspect_ratio,
            "category": data.category,
            "duration_ms": int((time.time() - start_time) * 1000),
        })

        return {
            "status": "success",
            "post_id": post_id,
            "headline": content_data.get("headline", ""),
            "hook": content_data.get("hook", ""),
            "caption": content_data.get("caption", ""),
            "cta": content_data.get("cta", ""),
            "hashtags": content_data.get("hashtags", []),
            "image_path": image_path,
            "aspect_ratio": aspect_ratio,
        }
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response: {str(e)}"}
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}


# ── Post Endpoints (History) ───────────────────────────────────────────────────

@app.get("/api/posts")
async def list_posts(request: Request, page: int = 1, limit: int = 12):
    session_id = request.state.session_id
    result = get_posts(session_id, page, limit, is_draft=False)
    return {"status": "success", **result}

@app.get("/api/posts/{post_id}")
async def get_post_endpoint(post_id: int):
    post = get_post(post_id)
    if not post:
        return {"error": "Post not found"}
    return {"status": "success", "post": post}

@app.delete("/api/posts/{post_id}")
async def delete_post_endpoint(post_id: int):
    deleted = delete_post(post_id)
    if not deleted:
        return {"error": "Post not found"}
    return {"status": "success", "message": "Post deleted"}

@app.post("/api/posts/{post_id}/duplicate")
async def duplicate_post_endpoint(post_id: int):
    """Duplicate an existing post."""
    session_id = request.state.session_id
    post = get_post(post_id)
    if not post:
        return {"error": "Post not found"}
    new_post_id = create_post(session_id, {
        "template_id": post["template_id"],
        "aspect_ratio": post["aspect_ratio"],
        "topic": post["topic"],
        "headline": post["headline"],
        "hook": post["hook"],
        "caption": post["caption"],
        "cta": post["cta"],
        "hashtags": post["hashtags"],
        "image_path": post["image_path"],
        "category": post["category"],
        "brand_name": post["brand_name"],
        "is_draft": 0,
    })
    new_post = get_post(new_post_id)
    return {"status": "success", "post": new_post}


# ── Draft Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/drafts")
async def list_drafts(request: Request, page: int = 1, limit: int = 12):
    session_id = request.state.session_id
    result = get_posts(session_id, page, limit, is_draft=True)
    return {"status": "success", **result}

@app.post("/api/drafts")
async def create_draft(request: Request, data: PostDraftRequest):
    session_id = request.state.session_id
    post_id = create_post(session_id, {**data.dict(), "is_draft": 1})
    post = get_post(post_id)
    return {"status": "success", "post": post}

@app.put("/api/drafts/{draft_id}")
async def update_draft(draft_id: int, data: PostDraftRequest):
    """Update an existing draft."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT session_id FROM posts WHERE id = ?", (draft_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {"error": "Draft not found"}
    c.execute("""UPDATE posts SET template_id = ?, aspect_ratio = ?, topic = ?,
                  headline = ?, hook = ?, caption = ?, cta = ?, hashtags = ?,
                  image_path = ?, category = ?, brand_name = ?
                  WHERE id = ?""",
              (data.template_id, data.aspect_ratio, data.topic, data.headline,
               data.hook, data.caption, data.cta, data.hashtags, data.image_path,
               data.category, data.brand_name, draft_id))
    conn.commit()
    conn.close()
    post = get_post(draft_id)
    return {"status": "success", "post": post}

@app.delete("/api/drafts/{draft_id}")
async def delete_draft(draft_id: int):
    """Delete a draft."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT is_draft FROM posts WHERE id = ?", (draft_id,))
    row = c.fetchone()
    if not row or not row[0]:
        conn.close()
        return {"error": "Draft not found"}
    c.execute("DELETE FROM posts WHERE id = ?", (draft_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Draft deleted"}

@app.post("/api/drafts/{draft_id}/duplicate")
async def duplicate_draft(draft_id: int):
    """Duplicate a draft."""
    session_id = request.state.session_id
    post = get_post(draft_id)
    if not post:
        return {"error": "Draft not found"}
    new_post_id = create_post(session_id, {
        "template_id": post["template_id"],
        "aspect_ratio": post["aspect_ratio"],
        "topic": post["topic"],
        "headline": post["headline"],
        "hook": post["hook"],
        "caption": post["caption"],
        "cta": post["cta"],
        "hashtags": post["hashtags"],
        "image_path": post["image_path"],
        "category": post["category"],
        "brand_name": post["brand_name"],
        "is_draft": 1,
    })
    new_post = get_post(new_post_id)
    return {"status": "success", "post": new_post}


# ── Category Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/categories")
async def list_categories():
    categories = get_categories()
    return {"status": "success", "categories": categories}


# ── Analytics Endpoints ────────────────────────────────────────────────────────

@app.get("/api/analytics")
async def get_analytics_endpoint(request: Request):
    session_id = request.state.session_id
    stats = get_analytics(session_id)
    return {"status": "success", "analytics": stats}


# ── Export Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/posts/{post_id}/export")
async def export_post(request: Request, post_id: int, format: str = "png"):
    session_id = request.state.session_id
    post = get_post(post_id)
    if not post:
        return {"error": "Post not found"}

    image_path = post.get("image_path")
    if not image_path or not os.path.exists(image_path):
        return {"error": "Image file not found"}

    # Track download
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET download_count = download_count + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

    filename = f"kyma_post_{post_id}.{format}"
    return FileResponse(
        path=image_path,
        media_type="image/png" if format == "png" else "image/jpeg",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# ── Image Upload Endpoint (Background Replacement) ───────────────────────────

@app.post("/api/posts/{post_id}/image/background")
async def upload_background(request: Request, post_id: int, file: UploadFile = File(...)):
    """Upload a custom background image for a post."""
    session_id = request.state.session_id
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.webp'}:
        return JSONResponse(status_code=400, content={"error": "Invalid file type. Use PNG, JPG, or WebP."})

    unique_name = f"bg_{post_id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = f"uploads/posts/{unique_name}"
    os.makedirs("uploads/posts", exist_ok=True)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Update post's image_path to use new background
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET image_path = ? WHERE id = ?", (file_path, post_id))
    conn.commit()
    conn.close()

    return {"status": "success", "image_path": file_path, "filename": file.filename, "filesize": len(content)}

@app.delete("/api/posts/{post_id}/image/background")
async def delete_background(post_id: int):
    """Remove custom background and reset to template default."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT template_id FROM posts WHERE id = ?", (post_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {"error": "Post not found"}
    template_id = row[0]
    default_path = f"templates/template_{template_id}.png"
    c.execute("UPDATE posts SET image_path = ? WHERE id = ?", (default_path, post_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Background reset to template default"}


# ── Font List Endpoint ────────────────────────────────────────────────────────

@app.get("/api/fonts")
async def list_fonts():
    """Return available font families for text customization."""
    fonts = [
        {"name": "Poppins", "key": "poppins"},
        {"name": "Inter", "key": "inter"},
        {"name": "Roboto", "key": "roboto"},
        {"name": "Open Sans", "key": "open-sans"},
        {"name": "Lato", "key": "lato"},
        {"name": "Montserrat", "key": "montserrat"},
        {"name": "Playfair Display", "key": "playfair"},
        {"name": "Source Sans Pro", "key": "source-sans"},
    ]
    return {"status": "success", "fonts": fonts}


# ── Utility ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "platform": "Kyma AI Instagram Content Generator"}

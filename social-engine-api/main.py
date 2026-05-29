from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
import os
import sqlite3
import json
import uuid
from tenacity import retry, wait_exponential, stop_after_attempt
from database import init_db, create_session, get_session, update_session_activity, get_brand_kit, upsert_brand_kit, delete_brand_kit, save_canvas_edit, get_canvas_edit, delete_canvas_edit, get_platforms, get_goals, get_template_elements
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

if not os.path.exists("outputs"): os.makedirs("outputs")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# ── Session Middleware ──────────────────────────────────────────────────────────
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Skip session handling for static files
    if request.url.path.startswith("/outputs"):
        return await call_next(request)
    
    # Get or create session_id from cookies
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        # Create new session
        session_id = str(uuid.uuid4())
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        create_session(session_id, ip_address, user_agent)
    
    else:
        # Verify session exists, create new if not
        session = get_session(session_id)
        if not session:
            session_id = str(uuid.uuid4())
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent", "")
            create_session(session_id, ip_address, user_agent)
        else:
            # Update last activity
            update_session_activity(session_id)
    
    # Add session_id to request state
    request.state.session_id = session_id
    
    # Process request
    response = await call_next(request)
    
    # Set session_id cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=30*24*60*60,  # 30 days
        httponly=True,
        samesite="lax"
    )
    
    return response

# ── Session Models ──────────────────────────────────────────────────────────────
class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    last_activity: str

class PostRequest(BaseModel):
    topic: str
    template_id: int

# ── Brand Kit Models ────────────────────────────────────────────────────────────
class BrandKitCreateRequest(BaseModel):
    brand_name: str
    primary_color: str = '#FFD700'
    secondary_color: str = '#29BE71'
    accent_color: str = '#64C8FF'

class BrandKitUpdateColorsRequest(BaseModel):
    primary_color: str = None
    secondary_color: str = None
    accent_color: str = None

class BrandKitResponse(BaseModel):
    id: int
    brand_name: str
    logo_path: str = None
    logo_filename: str = None
    logo_filesize: int = None
    primary_color: str
    secondary_color: str
    accent_color: str

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Enhanced Generation ─────────────────────────────────────────────────────────
class GenerateV2Request(BaseModel):
    platform_id: int
    goal_id: int
    topic: str
    industry: str = None
    target_audience: str = None
    tone: str = 'professional'
    cta_text: str = None
    template_id: int = 1
    brand_kit_id: int = None

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(3))
def call_gemini_v2(platform: dict, goal: dict, topic: str, industry: str = None,
                    audience: str = None, tone: str = 'professional', cta_text: str = None) -> dict:
    """Generate platform + goal aware marketing content."""
    
    # Platform-specific rules
    platform_rules = {
        'instagram': {
            'style': 'short punchy hook, emotional trigger, visual-first, minimal text',
            'headline_max': platform.get('max_headline_chars', 50),
            'density': 'minimal'
        },
        'linkedin': {
            'style': 'authority-driven, professional tone, business pain points, slightly longer',
            'headline_max': platform.get('max_headline_chars', 80),
            'density': 'medium'
        },
        'twitter': {
            'style': 'ultra-concise, witty, conversation starter, hook-heavy',
            'headline_max': platform.get('max_headline_chars', 40),
            'density': 'minimal'
        },
        'facebook': {
            'style': 'conversational, community tone, relatable, slightly longer',
            'headline_max': platform.get('max_headline_chars', 70),
            'density': 'medium'
        }
    }
    
    # Goal-specific rules
    goal_rules = {
        'engagement': {
            'hook_style': 'curiosity, question-based',
            'cta_style': 'question or poll'
        },
        'educational': {
            'hook_style': 'value-driven, list-style',
            'cta_style': 'learn more'
        },
        'promotional': {
            'hook_style': 'urgency, benefit-focused',
            'cta_style': 'shop now or sign up'
        },
        'authority': {
            'hook_style': 'data-driven, thought leadership',
            'cta_style': 'read more'
        },
        'motivational': {
            'hook_style': 'inspirational, aspirational',
            'cta_style': 'join now'
        }
    }
    
    platform_key = platform.get('key', 'instagram')
    goal_key = goal.get('key', 'engagement')
    p_rule = platform_rules.get(platform_key, platform_rules['instagram'])
    g_rule = goal_rules.get(goal_key, goal_rules['engagement'])
    
    max_chars = p_rule['headline_max']
    tone_desc = tone or 'professional'
    audience_str = f"Target audience: {audience}" if audience else ""
    industry_str = f"Industry: {industry}" if industry else ""
    
    prompt = f"""You are a professional social media copywriter generating content for {platform['name']}.

Platform Rules:
- Style: {p_rule['style']}
- Max headline chars: {max_chars}
- Text density: {p_rule['density']}

Content Goal: {goal['name']}
- Hook style: {g_rule['hook_style']}
- CTA style: {g_rule['cta_style']}

Tone: {tone_desc}
{industry_str}
{audience_str}

Topic: {topic}

Return ONLY valid JSON (no markdown, no backticks):
{{
  "headline": "Short engaging title (max {max_chars} chars, {max_chars//10} words max)",
  "subheading": "Supporting line that expands on headline (1 line only)",
  "hook": "Attention-grabbing first line - {g_rule['hook_style']}",
  "caption": "Main body - 1-2 short sentences for promotion (keep brief for {p_rule['density']} density)",
  "cta": "Call-to-action - {g_rule['cta_style']} style{f' - {cta_text}' if cta_text else ''}",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "content_angle": "The creative angle or emotional trigger used"
}}"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    text = response.text.strip()
    if text.startswith("```"):
        text = text[text.find("{"):text.rfind("}")+1]
    
    parsed = json.loads(text)
    return parsed

def call_gemini(topic: str):
    prompt = f"""Generate marketing content for the topic: {topic}

Return ONLY valid JSON (no markdown, no backticks, no extra text):
{{
  "headline": "Short engaging title (max 8 words)",
  "hook": "Attention-grabbing first line for the post",
  "caption": "Main body - 2-3 sentences of engaging content for promotion",
  "cta": "Clear call-to-action (Visit, Buy, Learn More, Shop Now, etc.)",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    # Parse JSON response
    text = response.text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text[text.find("{"):text.rfind("}")+1]
    
    parsed = json.loads(text)
    return parsed

# ── History & Dashboard Endpoints ────────────────────────────────────────────

@app.get("/api/v1/history")
async def get_history_endpoint(request: Request, page: int = 1, limit: int = 12):
    """Get paginated generation history for current session."""
    session_id = request.state.session_id
    offset = (page - 1) * limit
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ?", (session_id,))
    total = c.fetchone()[0]
    
    # Get paginated posts
    c.execute("""SELECT id, topic, headline, hook, caption, cta, hashtags, image_path, 
                  template_id, liked, favorite, view_count, created_at
                  FROM posts WHERE session_id = ?
                  ORDER BY created_at DESC LIMIT ? OFFSET ?""",
              (session_id, limit, offset))
    rows = c.fetchall()
    conn.close()
    
    posts = []
    for row in rows:
        posts.append({
            "id": row[0],
            "topic": row[1],
            "headline": row[2],
            "hook": row[3],
            "caption": row[4],
            "cta": row[5],
            "hashtags": json.loads(row[6]) if row[6] else [],
            "image_path": row[7],
            "template_id": row[8],
            "liked": bool(row[9]),
            "favorite": bool(row[10]),
            "view_count": row[11],
            "created_at": row[12]
        })
    
    return {
        "status": "success",
        "posts": posts,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total + limit - 1) // limit)
    }

@app.get("/api/v1/stats")
async def get_stats_endpoint(request: Request):
    """Get generation statistics for current session."""
    session_id = request.state.session_id
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Total posts
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ?", (session_id,))
    total_posts = c.fetchone()[0]
    
    # Posts today
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ? AND date(created_at) = date('now')", (session_id,))
    posts_today = c.fetchone()[0]
    
    # Posts this week
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ? AND created_at >= datetime('now', '-7 days')", (session_id,))
    posts_week = c.fetchone()[0]
    
    # Favorites
    c.execute("SELECT COUNT(*) FROM posts WHERE session_id = ? AND favorite = 1", (session_id,))
    favorites = c.fetchone()[0]
    
    # Total views (downloads)
    c.execute("SELECT COALESCE(SUM(view_count), 0) FROM posts WHERE session_id = ?", (session_id,))
    total_views = c.fetchone()[0]
    
    # Most used hashtags (get last 50 posts hashtags)
    c.execute("SELECT hashtags FROM posts WHERE session_id = ? AND hashtags IS NOT NULL ORDER BY created_at DESC LIMIT 50", (session_id,))
    hashtag_rows = c.fetchall()
    
    hashtag_counts = {}
    for hr in hashtag_rows:
        tags = json.loads(hr[0]) if hr[0] else []
        for tag in tags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: -x[1])[:10]
    
    conn.close()
    
    return {
        "status": "success",
        "stats": {
            "total_posts": total_posts,
            "posts_today": posts_today,
            "posts_week": posts_week,
            "favorites": favorites,
            "total_views": total_views,
            "top_hashtags": [{"tag": t, "count": c} for t, c in top_hashtags]
        }
    }

@app.post("/api/v1/posts/{post_id}/favorite")
async def toggle_favorite_endpoint(request: Request, post_id: int):
    """Toggle favorite status for a post."""
    session_id = request.state.session_id
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT favorite FROM posts WHERE id = ? AND session_id = ?", (post_id, session_id))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return {"error": "Post not found"}
    
    new_value = 0 if row[0] else 1
    c.execute("UPDATE posts SET favorite = ? WHERE id = ?", (new_value, post_id))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "favorite": bool(new_value),
        "message": "Added to favorites" if new_value else "Removed from favorites"
    }

@app.delete("/api/v1/posts/{post_id}")
async def delete_post_endpoint(request: Request, post_id: int):
    """Delete a post."""
    session_id = request.state.session_id
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT image_path FROM posts WHERE id = ? AND session_id = ?", (post_id, session_id))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return {"error": "Post not found"}
    
    # Delete the image file
    image_path = row[0]
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except:
            pass
    
    c.execute("DELETE FROM posts WHERE id = ? AND session_id = ?", (post_id, session_id))
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Post deleted"}

# ── Session Endpoints ───────────────────────────────────────────────────────────
@app.get("/session")
async def get_current_session(request: Request):
    """Get current session information."""
    session_id = request.state.session_id
    session = get_session(session_id)
    if session:
        return {
            "session_id": session["session_id"],
            "created_at": session["created_at"],
            "last_activity": session["last_activity"]
        }
    return {"error": "Session not found"}

# ── Brand Kit Endpoints ────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

@app.get("/api/v1/brand-kit/get")
async def get_brand_kit_endpoint(request: Request):
    """Get brand kit for current session."""
    session_id = request.state.session_id
    kit = get_brand_kit(session_id)
    if kit:
        return {
            "status": "success",
            "brand_kit": {
                "id": kit["id"],
                "brand_name": kit["brand_name"],
                "logo_path": kit["logo_path"],
                "logo_filename": kit["logo_filename"],
                "logo_filesize": kit["logo_filesize"],
                "primary_color": kit["primary_color"],
                "secondary_color": kit["secondary_color"],
                "accent_color": kit["accent_color"],
                "created_at": kit["created_at"],
                "updated_at": kit["updated_at"]
            }
        }
    return {"status": "success", "brand_kit": None}

@app.post("/api/v1/brand-kit/create")
async def create_brand_kit_endpoint(request: Request, data: BrandKitCreateRequest):
    """Create a new brand kit for the current session."""
    session_id = request.state.session_id
    kit_data = {
        'brand_name': data.brand_name,
        'primary_color': data.primary_color,
        'secondary_color': data.secondary_color,
        'accent_color': data.accent_color
    }
    kit = upsert_brand_kit(session_id, kit_data)
    return {
        "status": "success",
        "message": "Brand kit created successfully",
        "brand_kit": {
            "id": kit["id"],
            "brand_name": kit["brand_name"],
            "primary_color": kit["primary_color"],
            "secondary_color": kit["secondary_color"],
            "accent_color": kit["accent_color"]
        }
    }

@app.post("/api/v1/brand-kit/upload-logo")
async def upload_logo_endpoint(request: Request, file: UploadFile = File(...)):
    """Upload a logo image for the brand kit."""
    session_id = request.state.session_id
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
        )
    
    # Ensure upload directory exists
    upload_dir = "uploads/logos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file with unique name
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update brand kit with logo info
    kit_data = {
        'logo_path': file_path,
        'logo_filename': file.filename,
        'logo_filesize': len(content)
    }
    kit = upsert_brand_kit(session_id, kit_data)
    
    return {
        "status": "success",
        "message": "Logo uploaded successfully",
        "logo_path": file_path,
        "logo_filename": file.filename,
        "logo_filesize": len(content)
    }

@app.put("/api/v1/brand-kit/update-colors")
async def update_colors_endpoint(request: Request, data: BrandKitUpdateColorsRequest):
    """Update brand kit colors."""
    session_id = request.state.session_id
    
    kit_data = {}
    if data.primary_color is not None:
        kit_data['primary_color'] = data.primary_color
    if data.secondary_color is not None:
        kit_data['secondary_color'] = data.secondary_color
    if data.accent_color is not None:
        kit_data['accent_color'] = data.accent_color
    
    if not kit_data:
        return {"error": "No colors provided to update"}
    
    kit = upsert_brand_kit(session_id, kit_data)
    return {
        "status": "success",
        "message": "Colors updated successfully",
        "brand_kit": {
            "primary_color": kit["primary_color"],
            "secondary_color": kit["secondary_color"],
            "accent_color": kit["accent_color"]
        }
    }

# ── Platform & Goal Endpoints ─────────────────────────────────────────────────

@app.get("/api/v1/platforms")
async def get_platforms_endpoint():
    """Get all available platforms with their rules."""
    platforms = get_platforms()
    return {"status": "success", "platforms": platforms}

@app.get("/api/v1/goals")
async def get_goals_endpoint():
    """Get all content goals with their styles."""
    goals = get_goals()
    return {"status": "success", "goals": goals}

@app.get("/api/v1/templates")
async def get_templates_endpoint(platform: str = None):
    """Get templates, optionally filtered by platform compatibility."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if platform:
        # Filter templates by platform keyword in name
        c.execute("SELECT id, name, frame_size, config_json FROM templates WHERE LOWER(name) LIKE ?", (f'%{platform.lower()}%',))
    else:
        c.execute("SELECT id, name, frame_size, config_json FROM templates")
    
    rows = c.fetchall()
    conn.close()
    
    templates = []
    for r in rows:
        templates.append({
            "id": r[0], "name": r[1], "frame_size": r[2], "config_json": r[3]
        })
    
    return {"status": "success", "templates": templates}

@app.delete("/api/v1/brand-kit/delete")
async def delete_brand_kit_endpoint(request: Request):
    """Delete brand kit for current session."""
    session_id = request.state.session_id
    deleted = delete_brand_kit(session_id)
    if deleted:
        return {"status": "success", "message": "Brand kit deleted"}
    return {"error": "No brand kit found to delete"}

# ── Export Endpoints ──────────────────────────────────────────────────────────

class ExportTextRequest(BaseModel):
    post_id: int = None

@app.get("/api/v1/export/download")
async def export_download_endpoint(request: Request, post_id: int = None, image_path: str = None):
    """
    Download a generated image.
    Provide either post_id (fetches from DB) or image_path directly.
    """
    file_path = None
    post_row = None
    
    if post_id:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT image_path FROM posts WHERE id = ?", (post_id,))
        row = c.fetchone()
        conn.close()
        if row:
            file_path = row[0]
            # Track download
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("UPDATE posts SET view_count = view_count + 1, last_downloaded = CURRENT_TIMESTAMP WHERE id = ?", (post_id,))
            conn.commit()
            conn.close()
    elif image_path:
        file_path = image_path
    else:
        return JSONResponse(status_code=400, content={"error": "Provide post_id or image_path"})
    
    if not file_path or not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Image not found"})
    
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.post("/api/v1/export/get-text")
async def export_get_text_endpoint(request: Request, data: ExportTextRequest):
    """Get formatted text from a post (caption + CTA + hashtags)."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT caption, cta, hashtags FROM posts WHERE id = ?", (data.post_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Post not found"}
    
    caption, cta, hashtags_json = row
    hashtags = json.loads(hashtags_json) if hashtags_json else []
    hashtags_str = " ".join(hashtags)
    
    text_parts = [p for p in [caption, cta, hashtags_str] if p]
    formatted_text = "\n\n".join(text_parts)
    
    return {
        "status": "success",
        "text": formatted_text,
        "caption": caption,
        "cta": cta,
        "hashtags": hashtags_str
    }

# ── Generate V2 Endpoint ──────────────────────────────────────────────────────

@app.post("/api/v1/generate-v2")
async def generate_post_v2(request: Request, data: GenerateV2Request):
    """Enhanced generation with platform + goal awareness."""
    try:
        session_id = request.state.session_id
        
        # Fetch platform & goal info
        platforms = get_platforms()
        goals = get_goals()
        platform = next((p for p in platforms if p['id'] == data.platform_id), None)
        goal = next((g for g in goals if g['id'] == data.goal_id), None)
        
        if not platform or not goal:
            return {"error": "Invalid platform or goal selection"}
        
        # Fetch brand kit colors
        brand_colors = None
        brand_kit = get_brand_kit(session_id) if data.brand_kit_id else None
        if brand_kit:
            brand_colors = {
                'primary_color': brand_kit['primary_color'],
                'secondary_color': brand_kit['secondary_color'],
                'accent_color': brand_kit['accent_color'],
                'logo_path': brand_kit.get('logo_path'),
            }
        
        # Generate platform-aware content
        content_data = call_gemini_v2(
            platform, goal, data.topic,
            industry=data.industry,
            audience=data.target_audience,
            tone=data.tone,
            cta_text=data.cta_text
        )
        
        # Generate image
        image_path = generate_post_image(data.template_id, data.topic, content_data, brand_colors)
        
        # Store in database with all metadata
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO posts (session_id, brand_kit_id, platform_id, goal_id, topic, 
                    headline, subheading, hook, caption, cta, hashtags, image_path, template_id, 
                    industry, tone, target_audience)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (session_id,
                   brand_kit['id'] if brand_kit else None,
                   data.platform_id, data.goal_id,
                   data.topic,
                   content_data.get('headline', ''),
                   content_data.get('subheading', ''),
                   content_data.get('hook', ''),
                   content_data.get('caption', ''),
                   content_data.get('cta', ''),
                   json.dumps(content_data.get('hashtags', [])),
                   image_path,
                   data.template_id,
                   data.industry,
                   data.tone,
                   data.target_audience))
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "post_id": post_id,
            "platform": platform['name'],
            "goal": goal['name'],
            "headline": content_data.get('headline', ''),
            "subheading": content_data.get('subheading', ''),
            "hook": content_data.get('hook', ''),
            "caption": content_data.get('caption', ''),
            "cta": content_data.get('cta', ''),
            "hashtags": content_data.get('hashtags', []),
            "content_angle": content_data.get('content_angle', ''),
            "image_path": image_path,
            "branded": brand_colors is not None,
            "design_rules": {
                "platform": platform['key'],
                "text_density": next((pr['density'] for pk, pr in [
                    ('instagram', {'density': 'minimal'}), ('linkedin', {'density': 'medium'}),
                    ('twitter', {'density': 'minimal'}), ('facebook', {'density': 'medium'})
                ] if pk == platform['key']), 'minimal')
            }
        }
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse Gemini response as JSON: {str(e)}"}
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}

# ── Canvas Editor Endpoints ──────────────────────────────────────────────────

class CanvasEditRequest(BaseModel):
    headline_x: int = None
    headline_y: int = None
    headline_size: int = None
    headline_color: str = None
    hook_x: int = None
    hook_y: int = None
    hook_size: int = None
    hook_color: str = None
    caption_x: int = None
    caption_y: int = None
    caption_size: int = None

@app.get("/api/v1/canvas-edit/{post_id}")
async def get_canvas_edit_endpoint(post_id: int):
    """Get saved canvas edits for a post."""
    edits = get_canvas_edit(post_id)
    return {"status": "success", "edits": edits}

@app.post("/api/v1/canvas-edit/{post_id}/save")
async def save_canvas_edit_endpoint(post_id: int, data: CanvasEditRequest):
    """Save custom positioning for a post."""
    edits = {k: v for k, v in data.dict().items() if v is not None}
    saved = save_canvas_edit(post_id, edits)
    return {"status": "success", "edits": saved}

@app.post("/api/v1/canvas-edit/{post_id}/preview")
async def preview_canvas_edit_endpoint(request: Request, post_id: int, data: CanvasEditRequest):
    """Re-render an existing post with custom positioning and return new image."""
    session_id = request.state.session_id
    
    # Fetch original post data
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT topic, headline, hook, caption, cta, hashtags, image_path, template_id 
                  FROM posts WHERE id = ? AND session_id = ?""", (post_id, session_id))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Post not found"}
    
    topic, headline, hook, caption, cta, hashtags_json, old_image_path, template_id = row
    hashtags = json.loads(hashtags_json) if hashtags_json else []
    
    # Fetch brand kit colors
    brand_colors = None
    brand_kit = get_brand_kit(session_id)
    if brand_kit:
        brand_colors = {
            'primary_color': brand_kit['primary_color'],
            'secondary_color': brand_kit['secondary_color'],
            'accent_color': brand_kit['accent_color'],
            'logo_path': brand_kit.get('logo_path'),
        }
    
    # Build canvas edits from request
    canvas_edits = {k: v for k, v in data.dict().items() if v is not None}
    
    # Generate preview image with custom edits
    content_data = {
        "headline": headline,
        "hook": hook,
        "caption": caption,
        "cta": cta,
        "hashtags": hashtags
    }
    new_image_path = generate_post_image(
        template_id, f"preview_{post_id}", content_data, brand_colors, canvas_edits
    )
    
    return {
        "status": "success",
        "image_path": new_image_path
    }

@app.delete("/api/v1/canvas-edit/{post_id}/reset")
async def reset_canvas_edit_endpoint(post_id: int):
    """Reset canvas edits to template defaults."""
    deleted = delete_canvas_edit(post_id)
    return {"status": "success", "reset": deleted}

@app.get("/templates")
async def get_templates():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, frame_size FROM templates")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "frame_size": r[2]} for r in rows]

@app.post("/generate")
async def generate_post(request: Request, data: PostRequest):
    try:
        session_id = request.state.session_id
        
        # Fetch brand kit colors (if exists)
        brand_colors = None
        brand_kit = get_brand_kit(session_id)
        if brand_kit:
            brand_colors = {
                'primary_color': brand_kit['primary_color'],
                'secondary_color': brand_kit['secondary_color'],
                'accent_color': brand_kit['accent_color'],
                'logo_path': brand_kit.get('logo_path'),
            }
        
        content_data = call_gemini(data.topic)
        image_path = generate_post_image(data.template_id, data.topic, content_data, brand_colors)
        
        # Store in database with session_id and brand_kit_id
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO posts (session_id, brand_kit_id, topic, headline, hook, caption, cta, hashtags, image_path, template_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (session_id, 
                   brand_kit['id'] if brand_kit else None,
                   data.topic, content_data['headline'], content_data['hook'], 
                   content_data['caption'], content_data['cta'], 
                   json.dumps(content_data['hashtags']), image_path, data.template_id))
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "post_id": post_id,
            "headline": content_data['headline'],
            "hook": content_data['hook'],
            "caption": content_data['caption'],
            "cta": content_data['cta'],
            "hashtags": content_data['hashtags'],
            "image_path": image_path,
            "branded": brand_colors is not None
        }
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse Gemini response as JSON: {str(e)}"}
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}

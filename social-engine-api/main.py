"""
main.py - FastAPI Application Entry Point

Initializes the server, middleware, static file serving,
and registers all route modules.

Run: uvicorn main:app --reload
"""
import os
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from db.schema import init_db
from db.users import get_or_create_user

# ── Route imports ─────────────────────────────────────────────────────────────
from routes.session import router as session_router
from routes.generate import router as generate_router
from routes.posts import router as posts_router
from routes.health import router as health_router
from routes.blog import router as blog_router

# ── Load environment & initialize database ────────────────────────────────────
load_dotenv()
init_db()

app = FastAPI(title="Kyma AI - Instagram Content Generator")

# ── CORS configuration ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file directories ───────────────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads/logos", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# ── Session middleware ────────────────────────────────────────────────────────
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """
    Attach a session_id to every request.
    Creates a new anonymous user if no session cookie exists.
    Skips static file paths.
    """
    if request.url.path.startswith("/outputs") or request.url.path.startswith("/uploads"):
        return await call_next(request)

    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    # Ensure user record exists
    get_or_create_user(session_id)
    request.state.session_id = session_id

    response = await call_next(request)
    response.set_cookie(
        key="session_id", value=session_id,
        max_age=30 * 24 * 60 * 60,
        httponly=True, samesite="lax"
    )
    return response


# ── Register route modules ────────────────────────────────────────────────────
app.include_router(session_router)
app.include_router(generate_router)
app.include_router(posts_router)
app.include_router(health_router)
app.include_router(blog_router)

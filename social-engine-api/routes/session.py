"""
routes/session.py - User session endpoint

GET /api/session - Get or create anonymous user session.
"""
from fastapi import APIRouter, Request
from db.users import get_or_create_user

router = APIRouter()


@router.get("/api/session")
async def get_session(request: Request):
    """Return current session info. Creates user if not exists."""
    session_id = request.state.session_id
    user = get_or_create_user(session_id)
    return {"status": "success", "session_id": session_id, "user": user}
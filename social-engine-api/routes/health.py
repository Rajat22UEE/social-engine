"""
routes/health.py - Health check endpoint

GET /api/health - Simple health check to verify server is running.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
async def health():
    """Return server health status."""
    return {"status": "ok", "platform": "Kyma AI Instagram Content Generator"}
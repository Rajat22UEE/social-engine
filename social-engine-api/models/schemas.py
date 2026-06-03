"""
models/schemas.py - Pydantic request/response schemas

Defines all data models used by the API endpoints for validation and documentation.
"""
from pydantic import BaseModel
from typing import Optional


# ── Generation Request ───────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Request body for POST /api/generate - AI content generation."""
    topic: str
    template_id: int = 1
    aspect_ratio: str = '4:5'
    category: Optional[str] = None
    brand_name: Optional[str] = None
    cta_text: Optional[str] = None
"""
models/schemas.py - Pydantic request/response schemas

Defines all data models used by the API endpoints for validation and documentation.
"""
from pydantic import BaseModel
from typing import Optional, List


# ── Generation Request ───────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Request body for POST /api/generate - AI content generation."""
    topic: str
    template_id: int = 1
    aspect_ratio: str = '4:5'
    brand_name: Optional[str] = None
    cta_text: Optional[str] = None


# ── Blog Generator (AI SEO Blog Generator) ────────────────────────────────────────

class BlogGenerateRequest(BaseModel):
    """Request body for POST /api/blog/generate."""
    topic: str

class FAQItem(BaseModel):
    question: str
    answer: str

class InternalLink(BaseModel):
    text: str
    url: str

class BlogGenerateResponse(BaseModel):
    """Response from blog generation."""
    id: Optional[int] = None
    title: str = ""
    meta_title: str = ""
    meta_description: str = ""
    url_slug: str = ""
    primary_keyword: str = ""
    secondary_keywords: List[str] = []
    content: str = ""
    word_count: int = 0
    faq_questions: List[FAQItem] = []
    internal_links: List[InternalLink] = []
    seo_checklist: List[str] = []

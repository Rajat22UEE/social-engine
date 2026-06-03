"""
routes/categories.py - Content categories endpoint

GET /api/categories - List all content categories for generation flow.
"""
from fastapi import APIRouter
from db.categories import get_categories

router = APIRouter()


@router.get("/api/categories")
async def list_categories():
    """Return all content categories with icons and prompt hints."""
    categories = get_categories()
    return {"status": "success", "categories": categories}
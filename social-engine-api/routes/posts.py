"""
routes/posts.py - Post export endpoints

Endpoints for published posts:
  GET    /api/posts/{id}/export       - Download image file
"""
import os
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from db.posts import get_post, increment_download_count

router = APIRouter()


@router.get("/api/posts/{post_id}/export")
async def export_post(request: Request, post_id: int, format: str = "png"):
    """
    Download a post's generated image.
    Increments download count counter.
    """
    post = get_post(post_id)
    if not post:
        return {"error": "Post not found"}

    image_path = post.get("image_path")
    if not image_path or not os.path.exists(image_path):
        return {"error": "Image file not found"}

    # Track download
    increment_download_count(post_id)

    filename = f"kyma_post_{post_id}.{format}"
    return FileResponse(
        path=image_path,
        media_type="image/png" if format == "png" else "image/jpeg",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
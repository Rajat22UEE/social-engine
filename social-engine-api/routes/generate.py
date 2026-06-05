"""
routes/generate.py - Content generation endpoint

POST /api/generate - Generate Instagram content + image via AI.
"""
import json
from fastapi import APIRouter, Request
from db.templates import get_template
from db.posts import create_post
from services.gemini import call_gemini
from generators import generate_post_image
from models.schemas import GenerateRequest

router = APIRouter()


@router.post("/api/generate")
async def generate_post_endpoint(request: Request, data: GenerateRequest):
    """
    Generate Instagram-optimized content + image for a given topic.

    Flow:
      1. Fetch template for aspect ratio
      2. Call Gemini AI for content
      3. Generate image with Pillow
      4. Store in database
    """
    try:
        session_id = request.state.session_id

        # Get template to determine aspect ratio
        template = get_template(data.template_id)
        if not template:
            return {"error": "Template not found"}
        aspect_ratio = template.get("aspect_ratio", data.aspect_ratio)

        # Generate AI content (headline, hook, caption, cta, hashtags)
        content_data = call_gemini(
            topic=data.topic,
            brand_name=data.brand_name,
            cta_text=data.cta_text
        )

        # Generate image with text overlays (headline + hook)
        image_path = generate_post_image(
            data.template_id, data.topic, content_data
        )

        # Store in database
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
            "brand_name": data.brand_name,
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
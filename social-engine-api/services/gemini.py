"""
services/gemini.py - Google Gemini AI integration

Handles prompt engineering, API calls with retry logic,
and response parsing for Instagram content generation.
"""
import os
import json
import sys
import time
from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Lazy Gemini client — created on first use
_gemini_client = None


def _get_client():
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Please create a .env file with: GEMINI_API_KEY=your_key_here"
            )
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


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


# Only retry on rate limits / transient failures, not on auth errors
def call_gemini(topic: str, category: str = None, brand_name: str = None, cta_text: str = None) -> dict:
    """
    Generate Instagram marketing content using Gemini AI.
    Retries up to 3 times on transient errors.

    Returns:
        Dict with keys: headline, hook, caption, cta, hashtags
    """
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

    client = _get_client()
    last_error = None

    # Manual retry loop (3 attempts)
    for attempt in range(3):
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            text = response.text.strip()

            # Handle markdown code block wrapping if present
            if text.startswith("```"):
                text = text[text.find("{"):text.rfind("}") + 1]

            return json.loads(text)

        except json.JSONDecodeError:
            raise  # Don't retry on parse errors
        except Exception as e:
            last_error = e
            error_msg = str(e)

            # Try to get details from the API response
            if hasattr(e, 'response'):
                try:
                    error_msg = e.response.text[:500]
                except Exception:
                    pass

            # Print the actual Gemini error to the backend console
            print(f"\n❌ Gemini API error (attempt {attempt + 1}/3): {error_msg}\n", file=sys.stderr)

            # Don't retry on auth/not-found errors
            error_lower = error_msg.lower()
            if any(x in error_lower for x in ['api key', 'not found', 'not valid', 'permission', '404', '403', '401']):
                break

            if attempt < 2:
                wait = (4 ** attempt)  # 1s, 4s, 16s exponential
                print(f"⏳ Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)

    # All retries exhausted — raise the original error with context
    raise Exception(f"Gemini API error (after {attempt + 1} attempts): {last_error}")
"""
services/seo_blog.py - AI SEO Blog Generator using Gemini

Implements the 8-step framework from the PRD:
1. Keyword Research & Planning
2. Detailed Outline Creation
3. Full Content Writing
4. SEO Optimization
5. Visuals & Tables
6. Pre-Publish Checklist
7. Publish & Promote Strategy
8. Monitor & Update Guidance
"""
import os
import json
import re
import sys
import time
from google import genai
from google.genai import types

from models.schemas import BlogGenerateResponse, FAQItem, InternalLink

# Lazy Gemini client — shared with services/gemini.py pattern
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


# ── Adapted 8-Step SEO Blog Prompt (compressed from PRD) ─────────────────────

SYSTEM_PROMPT = """You are an expert SEO blog writer with 10+ years of experience. 
Generate a COMPLETE, SEO-optimized blog post based on the user's topic.

FOLLOW THIS EXACT PROCESS:

STEP 1 - ANALYZE TOPIC:
- Identify PRIMARY KEYWORD (main search term)
- Identify 3-5 SECONDARY KEYWORDS
- Determine SEARCH INTENT (listicle/tutorial/comparison)
- Set WORD COUNT TARGET (1800-2200 words for listicles)
- Determine CONTENT STRUCTURE

STEP 2 - CREATE OUTLINE:
H1: Main title with primary keyword
H2 sections: Introduction, Why Topic Matters, How We Selected, Main Content (10 items), Comparison Table, How to Choose, Best Practices, Company CTA, FAQs, Conclusion

STEP 3 - WRITE CONTENT:
- Introduction: 150 words, keyword in first 100 words
- Each H3 section (10 items): 150-200 words with Best For, Key Features, Free/Paid, Use Case, Pros/Cons, Rating
- Comparison table in Markdown
- FAQs: 5-7 questions
- Conclusion: 100 words + CTA

STEP 4 - SEO OPTIMIZATION:
- Keyword in title, H1, first 100 words, H2/H3, conclusion
- Meta title (max 60 chars) + meta description (150-160 chars)
- URL slug: /blog/keyword-rich-slug
- 3-5 internal link suggestions
- Image alt text: [key Image: Description]
- 1-2% keyword density only

STEP 5 - VISUALS & TABLES:
- 1 comparison table (mandatory)
- 3-5 image placeholders with alt text
- Bullet points for features/pros/cons
- Quote blocks for use cases

STEP 6 - CHECKLIST:
Add SEO checklist at end (10 items)

STEP 7 - PUBLISH & PROMOTE:
Provide promotion guidance

STEP 8 - MONITOR & UPDATE:
Provide tracking instructions

COMPANY CONTEXT:
- Company: Kyma AI Innovations (AI startup in Agartala, Tripura, Northeast India)
- Founders: Oracle, HCL, IBM veterans
- Products: Teacher's Companion, Interview Assistant, CRM Suite
- CTA: Join Kyma AI's GenAI coaching program at https://kyma-ai.in

OUTPUT FORMAT:
Return ONLY valid JSON (no markdown wrapping, no backticks):
{
  "title": "H1 title with primary keyword",
  "meta_title": "Under 60 chars",
  "meta_description": "150-160 char description",
  "url_slug": "/blog/slug",
  "primary_keyword": "main keyword",
  "secondary_keywords": ["kw1", "kw2", "kw3"],
  "content": "FULL MARKDOWN BLOG (2000+ words with H1/H2/H3/comparison table/FAQ)",
  "word_count": 2100,
  "faq_questions": [
    {"question": "Q1?", "answer": "Concise answer"}
  ],
  "internal_links": [
    {"text": "Page Name", "url": "https://kyma-ai.in/page"}
  ],
  "seo_checklist": [
    "✅ Keyword in title, H1, first 100 words, H2/H3, conclusion"
  ],
  "publish_promote": "Promotion guidance text",
  "monitor_update": "Tracking guidance text"
}

TONE: Professional yet accessible, data-driven, actionable, no fluff.
QUALITY: 1800-2200 words, short paragraphs (2-3 sentences), bullet points, no keyword stuffing."""


def _escape_newlines_in_strings(text: str) -> str:
    """
    Escape literal newlines (\\n) and control characters that are inside JSON string values.
    This fixes Gemini responses where the markdown content has unescaped newlines.
    """
    result = []
    in_string = False
    escape_next = False
    i = 0
    while i < len(text):
        ch = text[i]
        if escape_next:
            result.append(ch)
            escape_next = False
            i += 1
            continue
        if ch == '\\':
            result.append(ch)
            escape_next = True
            i += 1
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            i += 1
            continue
        if in_string and ch in '\n\r\t':
            result.append('\\n' if ch in '\n\r' else '\\t')
            i += 1
            continue
        result.append(ch)
        i += 1
    return ''.join(result)


def _safe_json_parse(text: str) -> dict:
    """
    Safely parse JSON that may have unescaped newlines/control chars in string values.

    1. Try json.loads with strict=False (allows control chars)
    2. If fails, pre-escape newlines inside string values and retry
    3. Final fallback: regex extraction
    """
    # Attempt 1: standard parse with strict=False
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass

    # Attempt 2: escape literal newlines inside string values
    try:
        # Replace newlines that are inside string values (between quotes)
        fixed = _escape_newlines_in_strings(text)
        return json.loads(fixed, strict=False)
    except json.JSONDecodeError:
        pass

    # Attempt 3: regex fallback extraction
    result = {}

    # Extract simple string fields
    simple_fields = ['title', 'meta_title', 'meta_description', 'url_slug',
                     'primary_keyword', 'word_count', 'publish_promote', 'monitor_update']
    for field in simple_fields:
        pattern = rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)"'
        m = re.search(pattern, text, re.DOTALL)
        if m:
            val = m.group(1)
            result[field] = val.replace('\\n', '\n').replace('\\t', '\t')

    # Extract content field (can span multiple lines)
    content_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
    if content_match:
        content = content_match.group(1)
        # Unescape known escape sequences
        content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
        result['content'] = content

    # Extract arrays
    for field in ['secondary_keywords', 'seo_checklist']:
        arr_match = re.search(rf'"{field}"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if arr_match:
            arr_content = arr_match.group(1)
            items = re.findall(r'"((?:[^"\\]|\\.)*)"', arr_content)
            result[field] = [item.replace('\\"', '"') for item in items]
        else:
            result[field] = []

    # Extract array of objects
    for field in ['faq_questions', 'internal_links']:
        obj_match = re.search(rf'"{field}"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if obj_match:
            obj_content = obj_match.group(1)
            objects = re.findall(r'\{([^}]*)\}', obj_content)
            parsed_objects = []
            for obj in objects:
                obj_dict = {}
                for key, val in re.findall(r'"(\w+)"\s*:\s*"((?:[^"\\]|\\.)*)"', obj):
                    obj_dict[key] = val.replace('\\"', '"')
                if obj_dict:
                    parsed_objects.append(obj_dict)
            result[field] = parsed_objects
        else:
            result[field] = []

    # Try to extract word_count as int
    wc_match = re.search(r'"word_count"\s*:\s*(\d+)', text)
    if wc_match:
        result['word_count'] = int(wc_match.group(1))

    if 'content' not in result or not result['content']:
        raise ValueError("Could not parse blog content from AI response")

    return result


def generate_blog(topic: str) -> dict:
    """
    Generate a complete SEO-optimized blog post using Gemini.

    Args:
        topic: The blog topic from user input

    Returns:
        Dict matching BlogGenerateResponse schema
    """
    client = _get_client()
    last_error = None

    prompt = f"""Generate a complete SEO-optimized blog post about this topic:

TOPIC: {topic}

Follow the 8-step framework exactly. Return ONLY valid JSON.
Ensure the blog content is 1800-2200 words with proper H1/H2/H3 structure.
Include all SEO elements, comparison tables, FAQ section, and company CTA for Kyma AI."""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=SYSTEM_PROMPT + "\n\n" + prompt)]
                    )
                ]
            )
            text = response.text.strip()

            # Handle markdown code block wrapping if present
            if text.startswith("```"):
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    text = text[start:end + 1]

            # Parse JSON - handle control characters and embedded newlines
            result = _safe_json_parse(text)

            # Validate required fields
            if not result.get("content"):
                raise ValueError("AI response missing 'content' field")

            # Parse internal_links if they came as dicts
            links = result.get("internal_links", [])
            if isinstance(links, list):
                result["internal_links"] = [
                    {"text": l.get("text", ""), "url": l.get("url", "")}
                    for l in links if isinstance(l, dict)
                ]

            # Parse faq_questions if they came as dicts
            faqs = result.get("faq_questions", [])
            if isinstance(faqs, list):
                result["faq_questions"] = [
                    {"question": f.get("question", ""), "answer": f.get("answer", "")}
                    for f in faqs if isinstance(f, dict)
                ]

            return result

        except ValueError as e:
            raise  # Don't retry on parse/validation errors
        except Exception as e:
            last_error = e
            error_msg = str(e)
            if hasattr(e, 'response'):
                try:
                    error_msg = e.response.text[:500]
                except Exception:
                    pass

            print(f"\n❌ Gemini SEO Blog API error (attempt {attempt + 1}/3): {error_msg}\n", file=sys.stderr)

            error_lower = error_msg.lower()
            if any(x in error_lower for x in ['api key', 'not found', 'not valid', 'permission', '404', '403', '401']):
                break

            if attempt < 2:
                wait = (4 ** attempt)
                print(f"⏳ Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)

    raise Exception(f"Gemini SEO Blog API error (after {attempt + 1} attempts): {last_error}")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os
import sqlite3
import json
from tenacity import retry, wait_exponential, stop_after_attempt
from database import init_db
from generators import generate_post_image

load_dotenv()
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("outputs"): os.makedirs("outputs")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

class PostRequest(BaseModel):
    topic: str
    template_id: int

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Retry logic: Wait longer between each attempt if a 429 occurs
@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(3))
def call_gemini(topic: str):
    prompt = f"""Generate marketing content for the topic: {topic}

Return ONLY valid JSON (no markdown, no backticks, no extra text):
{{
  "headline": "Short engaging title (max 8 words)",
  "hook": "Attention-grabbing first line for the post",
  "caption": "Main body - 2-3 sentences of engaging content for promotion",
  "cta": "Clear call-to-action (Visit, Buy, Learn More, Shop Now, etc.)",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    # Parse JSON response
    text = response.text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text[text.find("{"):text.rfind("}")+1]
    
    parsed = json.loads(text)
    return parsed

@app.get("/templates")
async def get_templates():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, frame_size FROM templates")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "frame_size": r[2]} for r in rows]

@app.post("/generate")
async def generate_post(data: PostRequest):
    try:
        content_data = call_gemini(data.topic)
        image_path = generate_post_image(data.template_id, data.topic, content_data)
        
        # Store in database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO posts (topic, headline, hook, caption, cta, hashtags, image_path, template_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (data.topic, content_data['headline'], content_data['hook'], 
                   content_data['caption'], content_data['cta'], 
                   json.dumps(content_data['hashtags']), image_path, data.template_id))
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "headline": content_data['headline'],
            "hook": content_data['hook'],
            "caption": content_data['caption'],
            "cta": content_data['cta'],
            "hashtags": content_data['hashtags'],
            "image_path": image_path
        }
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse Gemini response as JSON: {str(e)}"}
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os
import sqlite3
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
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Write an Instagram caption and 5 hashtags for: {topic}"
    )

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
        response = call_gemini(data.topic)
        image_path = generate_post_image(data.template_id, data.topic, response.text)
        return {"content": response.text, "image_path": image_path, "status": "success"}
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}
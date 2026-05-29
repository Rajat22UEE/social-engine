from scheduler import start_scheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from tenacity import retry, wait_exponential, stop_after_attempt

import os
import sqlite3
import crud

from database import init_db
from generators import generate_post_image


# =========================================
# LOAD ENV + INIT DB
# =========================================

load_dotenv()

init_db()


# =========================================
# FASTAPI APP
# =========================================

app = FastAPI()

start_scheduler()

# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# STATIC OUTPUTS
# =========================================

if not os.path.exists("outputs"):

    os.makedirs("outputs")

app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs"
)


# =========================================
# REQUEST MODELS
# =========================================

class PostRequest(BaseModel):

    topic: str

    template_id: int

    platform: str = "instagram"


# =========================================
# GEMINI CLIENT
# =========================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================================
# GEMINI RETRY LOGIC
# =========================================

@retry(
    wait=wait_exponential(
        multiplier=1,
        min=4,
        max=60
    ),
    stop=stop_after_attempt(3)
)

def call_gemini(topic: str):

    return client.models.generate_content(

        model="gemini-2.5-flash",

        contents=f"""
        Write:

        1. Instagram caption
        2. 5 hashtags

        Topic: {topic}
        """
    )


# =========================================
# ROOT
# =========================================

@app.get("/")
async def root():

    return {
        "message": "Social Engine API Running"
    }


# =========================================
# GET TEMPLATES
# =========================================

@app.get("/templates")
async def get_templates():

    conn = sqlite3.connect("database.db")

    c = conn.cursor()

    c.execute("""
    SELECT id, name, frame_size
    FROM templates
    """)

    rows = c.fetchall()

    conn.close()

    return [

        {
            "id": r[0],
            "name": r[1],
            "frame_size": r[2]
        }

        for r in rows
    ]


# =========================================
# GENERATE AI POST
# =========================================

@app.post("/generate")
async def generate_post(data: PostRequest):

    try:

        # Generate AI content
        response = call_gemini(data.topic)

        content = response.text

        # Generate image
        image_path = generate_post_image(
            data.template_id,
            data.topic,
            content
        )

        # Save post to DB
        post_data = {

            "topic": data.topic,

            "caption": content,

            "hashtags": "#ai #automation",

            "image_path": image_path,

            "template_id": data.template_id,

            "platform": data.platform

        }

        saved_post = crud.create_post(post_data)

        return {

            "status": "success",

            "content": content,

            "image_path": image_path,

            "saved_post": saved_post
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)
        }


# =========================================
# GET ALL POSTS
# =========================================

@app.get("/posts")
async def get_posts():

    return crud.get_posts()


# =========================================
# GET SINGLE POST
# =========================================

@app.get("/posts/{post_id}")
async def get_post(post_id: int):

    return crud.get_post(post_id)


# =========================================
# UPDATE POST
# =========================================

@app.put("/posts/{post_id}")
async def update_post(post_id: int, data: dict):

    return crud.update_post(post_id, data)


# =========================================
# DELETE POST
# =========================================

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):

    return crud.delete_post(post_id)


# =========================================
# SCHEDULE POST
# =========================================

@app.post("/schedule")
async def schedule_post(data: dict):

    return crud.schedule_post(data)


# =========================================
# GET ALL SCHEDULED POSTS
# =========================================

@app.get("/scheduled-posts")
async def get_scheduled_posts():

    return crud.get_scheduled_posts()


# =========================================
# GET SINGLE SCHEDULED POST
# =========================================

@app.get("/scheduled-posts/{schedule_id}")
async def get_scheduled_post(schedule_id: int):

    return crud.get_scheduled_post(schedule_id)


# =========================================
# UPDATE SCHEDULED POST
# =========================================

@app.put("/scheduled-posts/{schedule_id}")
async def update_scheduled_post(schedule_id: int, data: dict):

    return crud.update_scheduled_post(
        schedule_id,
        data
    )


# =========================================
# DELETE SCHEDULED POST
# =========================================

@app.delete("/scheduled-posts/{schedule_id}")
async def delete_scheduled_post(schedule_id: int):

    return crud.delete_scheduled_post(schedule_id)


# =========================================
# GET PUBLISHING HISTORY
# =========================================

@app.get("/publishing-history")
async def get_publishing_history():

    return crud.get_publishing_history()

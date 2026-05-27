# Social Engine - AI Image Generation Platform

## Comprehensive Technical Documentation

**Last Updated:** May 27, 2026  
**Project Status:** Phase 2 - Image Engine (50% Complete)  
**Development Environment:** FastAPI + Next.js 16

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Code Organization](#code-organization)
7. [Current Implementation Status](#current-implementation-status)
8. [Completed Features](#completed-features)
9. [Known Issues & Limitations](#known-issues--limitations)
10. [Next Phases & TODO](#next-phases--todo)
11. [Setup & Deployment](#setup--deployment)
12. [Testing Guide](#testing-guide)

---

## Project Overview

### Purpose

A web-based system that allows users to input a topic and generate ready-to-post social media assets (Image + Caption + Hashtags) optimized for marketing and promotion.

### Core Features

- **Dashboard**: View project stats, system status, and generation history
- **Create**: Input topic, select design template, generate optimized marketing content + image
- **Output**: Download generated image with overlay text (headline, hook, caption, hashtags)
- **Database**: Store generation history with structured metadata

### Target Use Cases

- Social media content creators
- Marketing agencies
- Small business owners
- E-commerce product promotion
- Content marketing professionals

---

## Architecture

### High-Level Flow

```
User Input (Topic + Template)
    ↓
[Frontend: Next.js UI] → POST /generate
    ↓
[Backend: FastAPI]
    ├─ Call Gemini API (JSON prompt)
    ├─ Parse structured response
    └─ Pass to image generator
    ↓
[Image Generator: Pillow]
    ├─ Load template image
    ├─ Multi-layer text overlay
    ├─ Save to outputs/
    └─ Return file path
    ↓
[Database: SQLite]
    ├─ Store metadata
    ├─ Store individual fields
    └─ Persist for history
    ↓
[Response to Frontend]
    ├─ Headline
    ├─ Hook
    ├─ Caption
    ├─ CTA
    ├─ Hashtags
    └─ Image URL
    ↓
[Frontend Display]
    └─ Display structured content with styling
```

### System Components

```
social-engine-api/
├── main.py                    # FastAPI server + API routes
├── database.py                # SQLite schema initialization
├── generators.py              # Image generation with Pillow
├── templates/                 # Base template images (PNG)
│   └── template_1.png         # 1080x1350px template
├── outputs/                   # Generated images (auto-created)
├── venv/                      # Python virtual environment
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (GEMINI_API_KEY)
└── database.db               # SQLite database (auto-created)

social-engine-ui/
├── src/
│   └── app/
│       ├── page.tsx          # Main dashboard/create page
│       ├── layout.tsx        # Root layout
│       └── globals.css       # Global styles
├── public/                   # Static assets
├── package.json              # Node dependencies
├── tsconfig.json             # TypeScript config
├── next.config.ts            # Next.js config
├── eslint.config.mjs         # Linting config
└── tailwind.config.mjs       # Tailwind CSS config
```

---

## Technology Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **AI/LLM**: Google Generative AI SDK (Gemini 2.5-flash)
- **Image Processing**: Pillow (PIL)
- **Database**: SQLite
- **Server**: Uvicorn
- **Retry Logic**: Tenacity (exponential backoff for rate limits)
- **CORS**: CORSMiddleware (allow_origins=["*"])

### Frontend

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **UI Components**: Lucide React (icons)
- **Runtime**: React 19.2.4

### Environment & Dependencies

- **Package Manager**: npm (Node.js)
- **Python Version**: 3.11+
- **Virtual Environment**: venv
- **API Port**: 8000 (FastAPI)
- **UI Port**: 3000 (Next.js)

---

## Database Schema

### Table 1: `templates`

Store available design templates for image generation

| Field         | Type         | Description                              |
| ------------- | ------------ | ---------------------------------------- |
| `id`          | INTEGER (PK) | Template identifier                      |
| `name`        | TEXT         | Display name (e.g., "Standard Portrait") |
| `frame_size`  | TEXT         | Dimensions (e.g., "1080x1350")           |
| `config_json` | TEXT         | JSON config with text positioning        |

**Current Data:**

```sql
INSERT INTO templates VALUES
(1, 'Standard Portrait', '1080x1350', '{"text_x": 50, "text_y": 200}');
```

### Table 2: `posts`

Store generated content metadata and history

| Field         | Type         | Description                      |
| ------------- | ------------ | -------------------------------- |
| `id`          | INTEGER (PK) | Post identifier                  |
| `topic`       | TEXT         | Original user input topic        |
| `headline`    | TEXT         | Generated headline (max 8 words) |
| `hook`        | TEXT         | Attention-grabbing first line    |
| `caption`     | TEXT         | Main body text (2-3 sentences)   |
| `cta`         | TEXT         | Call-to-action statement         |
| `hashtags`    | TEXT         | JSON array of 5-7 hashtags       |
| `image_path`  | TEXT         | Relative path to generated image |
| `template_id` | INTEGER (FK) | Reference to templates table     |
| `created_at`  | TIMESTAMP    | Auto-timestamp of creation       |

**Schema SQL:**

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    topic TEXT,
    headline TEXT,
    hook TEXT,
    caption TEXT,
    cta TEXT,
    hashtags TEXT,
    image_path TEXT,
    template_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

### 1. GET `/templates`

**Purpose:** Retrieve list of available design templates

**Request:**

```http
GET /templates HTTP/1.1
Host: http://127.0.0.1:8000
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "Standard Portrait",
    "frame_size": "1080x1350"
  }
]
```

**Error Handling:** N/A (simple database query)

---

### 2. POST `/generate`

**Purpose:** Generate marketing content and image for given topic

**Request:**

```http
POST /generate HTTP/1.1
Host: http://127.0.0.1:8000
Content-Type: application/json

{
  "topic": "Artisan Coffee Shop",
  "template_id": 1
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "headline": "Experience Handcrafted Coffee Perfection",
  "hook": "Tired of the ordinary? Discover extraordinary.",
  "caption": "Step into our artisan coffee shop and savor the difference true craftsmanship makes. Every bean is carefully selected, roasted to perfection, and expertly brewed by our passionate baristas to create a rich, unparalleled flavor. Elevate your daily ritual with a cup that's truly a work of art.",
  "cta": "Find Your Perfect Brew Today!",
  "hashtags": [
    "#ArtisanCoffee",
    "#SpecialtyCoffee",
    "#HandcraftedBrew",
    "#CoffeeShopVibes",
    "#LocalCoffee"
  ],
  "image_path": "outputs/gen_Artisan_1.png"
}
```

**Error Response (400/500):**

```json
{
  "error": "Failed to parse Gemini response as JSON: [error details]"
}
```

**Internal Process:**

1. Receive `topic` and `template_id`
2. Call Gemini API with structured JSON prompt
3. Parse returned JSON (with fallback for markdown blocks)
4. Generate image with text overlays using Pillow
5. Store metadata in database
6. Return complete structured response

**Retry Logic:**

- Uses Tenacity decorator with exponential backoff
- Max retries: 3 attempts
- Initial wait: 4 seconds
- Max wait: 60 seconds
- Triggers on rate limit (429) errors

---

## Code Organization

### Backend - `social-engine-api/main.py`

#### Key Components:

**1. Initialization**

```python
load_dotenv()  # Load GEMINI_API_KEY from .env
init_db()      # Create/verify database schema
```

**2. FastAPI Setup**

```python
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])  # Enable CORS
app.mount("/outputs", StaticFiles(directory="outputs"))   # Serve generated images
```

**3. Request Model**

```python
class PostRequest(BaseModel):
    topic: str          # User input (required)
    template_id: int    # Template selection (required)
```

**4. Gemini Integration**

```python
@retry(wait=wait_exponential(multiplier=1, min=4, max=60),
       stop=stop_after_attempt(3))
def call_gemini(topic: str):
    # Prompt engineering with JSON schema
    # Response parsing with markdown block removal
    # Return parsed dictionary
```

**5. API Route Handlers**

```python
@app.get("/templates")  # Fetch available templates
@app.post("/generate")  # Generate content and image
```

---

### Backend - `social-engine-api/database.py`

**Functionality:**

- SQLite initialization on app startup
- Schema creation (drop + recreate for fresh setup)
- Template seeding with default "Standard Portrait"

**Current Approach:**

```python
def init_db():
    # DROP existing tables (for testing/fresh start)
    # CREATE new tables with proper schema
    # INSERT default template
    # COMMIT changes
```

**⚠️ TODO:** Change to production-safe schema migration (see Next Phases)

---

### Backend - `social-engine-api/generators.py`

#### Class: `TextOverlay`

Handles image manipulation with Pillow

**Initialization:**

```python
def __init__(self, template_path):
    self.image = Image.open(template_path)
    self.draw = ImageDraw.Draw(self.image)
    # Load fonts: headline (50px), body (32px), small (24px)
```

**Methods:**

1. **add_text(text, position, font, color)**
   - Single-line text overlay
   - Used for headline and hashtags

2. **add_multiline_text(text, position, font, color, max_width)**
   - Multi-line text with automatic word wrapping
   - Calculates line breaks based on font width
   - Used for hook and caption

3. **save(output_path)**
   - Persist modified image to disk

#### Function: `generate_post_image(template_id, topic, content_data)`

**Input:**

- `template_id`: Int referencing template in database
- `topic`: String used for filename generation
- `content_data`: Dict with keys {headline, hook, caption, cta, hashtags}

**Process:**

1. Load template image from `templates/template_{id}.png`
2. Create TextOverlay instance
3. Overlay headline (gold, 50px) at y=100
4. Overlay hook (white, 32px) at y=200 with wrapping
5. Overlay caption (light gray, 32px) at y=450 with wrapping
6. Overlay hashtags (cyan, 24px) at y=1200
7. Save to `outputs/gen_{topic[:8]}_{template_id}.png`
8. Return relative file path

**Text Color Scheme:**

- Headline: Gold (#FFD700)
- Hook: White (255, 255, 255)
- Caption: Light Gray (200, 200, 200)
- Hashtags: Cyan (100, 200, 255)

---

### Frontend - `social-engine-ui/src/app/page.tsx`

#### State Management:

```typescript
const [view, setView] = useState("create"); // 'dashboard' | 'create'
const [topic, setTopic] = useState("");
const [templates, setTemplates] = useState<{ id; name }[]>([]);
const [selectedTemplate, setSelectedTemplate] = useState(1);
const [loading, setLoading] = useState(false);
const [result, setResult] = useState<{
  headline: string;
  hook: string;
  caption: string;
  cta: string;
  hashtags: string[];
  image_path: string;
} | null>(null);
```

#### Key Functions:

**useEffect Hook:**

- Fetch templates from `/templates` on component mount
- Populate template selector

**handleCreate:**

- Validate topic input
- POST to `/generate` endpoint
- Handle JSON response
- Update result state
- Error handling with user alerts

#### UI Sections:

**Sidebar Navigation:**

- Dashboard button (placeholder)
- Create Post button (active)

**Main Content - Create Tab:**

- Template selector dropdown
- Topic input field
- Generate button (disabled during loading)
- Result display (conditional render)

**Result Display Components:**

- **Headline Box**: Yellow border, large bold text
- **Hook Box**: White text, normal border
- **Caption Box**: Gray text, normal border
- **CTA Box**: Blue border, button-style
- **Hashtags**: Cyan pills/tags with flex layout
- **Image Preview**: Full-width image with download link

#### Styling:

- Dark theme (bg-[#0f172a])
- Tailwind CSS utilities
- Color scheme: Blue, Yellow, Cyan, White/Gray
- Responsive grid layouts

---

## Current Implementation Status

### ✅ Completed (Phase 1 + Phase 2 Part 1)

#### Backend

- [x] FastAPI server setup with CORS
- [x] Environment variable handling (.env)
- [x] SQLite database initialization
- [x] Gemini API integration with retry logic
- [x] JSON response parsing with markdown fallback
- [x] Static file serving for generated images
- [x] `/templates` GET endpoint
- [x] `/generate` POST endpoint with full workflow

#### Image Generation

- [x] Template image loading (Pillow)
- [x] Multi-font support (headline, body, small)
- [x] Multi-line text wrapping algorithm
- [x] Color-coded overlays
- [x] File naming convention (gen*{topic}*{template_id}.png)
- [x] Output directory creation and management

#### Database

- [x] SQLite schema with structured fields
- [x] Posts table with: headline, hook, caption, cta, hashtags, image_path
- [x] Templates table with frame sizing
- [x] Database seeding with default template

#### Frontend

- [x] Next.js 16 setup with TypeScript
- [x] Tailwind CSS styling
- [x] Component state management (useState, useEffect)
- [x] API fetch to /templates endpoint
- [x] API fetch to /generate endpoint
- [x] Structured result display
- [x] Color-coded content sections
- [x] Image preview
- [x] Download button

#### Testing

- [x] API endpoint testing (curl/PowerShell)
- [x] JSON parsing validation
- [x] Image generation validation
- [x] Database schema verification

---

## Completed Features

### 1. Structured Content Generation

**What:** Gemini AI now returns marketing content in JSON format instead of raw text

**How:**

- Custom prompt with JSON schema specification
- Includes: headline, hook, caption, cta, hashtags
- Markdown block removal for parsing robustness

**Result:** Structured data enables proper UI display and image overlay

---

### 2. Multi-Layer Image Overlay

**What:** Generated images now include multiple layers of text with proper hierarchy

**Layers:**

1. **Headline** (Gold, 50px, top)
2. **Hook** (White, 32px, upper-middle)
3. **Caption** (Light Gray, 32px, middle)
4. **Hashtags** (Cyan, 24px, bottom)

**Features:**

- Automatic text wrapping for long content
- Color-coded for visual hierarchy
- Proper spacing and positioning

---

### 3. Database Schema

**What:** Structured SQLite database with individual fields for each content component

**Tables:**

- `templates`: Design templates with sizing
- `posts`: Generation history with metadata

**Benefits:**

- Separates content components for flexible querying
- Enables analytics (track hashtags, headlines, etc.)
- Supports future filtering/search

---

### 4. Frontend Display

**What:** Beautiful, styled UI that displays structured content

**Components:**

- Template selector
- Topic input
- Generate button with loading state
- Structured result cards (headline, hook, caption, cta, hashtags)
- Image preview
- Download button

**Styling:**

- Dark theme (professional look)
- Color-coded sections
- Responsive layout
- Tailwind CSS utilities

---

## Known Issues & Limitations

### Current Issues

1. **Database Reset on Startup**
   - **Issue:** `database.py` drops tables on every startup
   - **Impact:** Data not persisted between server restarts
   - **Cause:** Used for fresh testing
   - **Fix:** Change to CREATE TABLE IF NOT EXISTS with migrations (see next phases)

2. **Single Template**
   - **Issue:** Only 1 template available (1080x1350 portrait)
   - **Impact:** Limited image size options
   - **Fix:** Add more templates (landscape, square, stories, etc.)

3. **No Dashboard History**
   - **Issue:** Dashboard placeholder only, no actual history display
   - **Impact:** Users can't see past generations
   - **Fix:** Implement history query endpoint and dashboard UI

4. **No User Authentication**
   - **Issue:** No login/logout, no user tracking
   - **Impact:** Can't track user activity or limit API calls
   - **Fix:** Add auth system (Supabase JWT or similar)

5. **Rate Limiting**
   - **Issue:** No per-user rate limiting
   - **Impact:** Potential API abuse
   - **Fix:** Implement rate limiting middleware

### Limitations

- **Gemini API Dependency:** System requires Gemini API key and active internet
- **File Storage:** Images stored locally (not scalable for production)
- **No CDN:** Images served directly from backend
- **No Caching:** Each request calls Gemini API (potential cost)
- **Single Language:** Content generated only in English
- **Template Customization:** Users can't create/edit templates via UI

---

## Next Phases & TODO

### Phase 2 (Continued) - Advanced Image Engine

#### Phase 2B: Production Database Migration

- [ ] Update `database.py` to use CREATE TABLE IF NOT EXISTS
- [ ] Implement ALTER TABLE for schema evolution
- [ ] Add migration tracking table
- [ ] Remove DROP TABLE behavior
- [ ] Test data persistence across restarts

#### Phase 2C: Multiple Templates

- [ ] Create additional template images:
  - [ ] Landscape (16:9, 1920x1080)
  - [ ] Square (1:1, 1080x1080)
  - [ ] Stories (9:16, 1080x1920)
  - [ ] LinkedIn (1200x627)
  - [ ] Twitter (1200x628)
- [ ] Update database seeding with all templates
- [ ] Test image generation for each size
- [ ] Add template preview in frontend

#### Phase 2D: History & Dashboard

- [ ] Create `/history` GET endpoint
  - Query: SELECT \* FROM posts ORDER BY created_at DESC LIMIT 50
  - Response: Array of past generations
- [ ] Implement Dashboard tab in frontend
  - Display generation statistics
  - Show recent posts in grid
  - Click to view/download past results
- [ ] Add stats calculations:
  - Total posts generated
  - Posts generated today
  - Most used hashtags
  - System uptime

---

### Phase 3: Enhanced Content Generation

#### Phase 3A: Multi-Platform Optimization

- [ ] Add platform selector (Instagram, TikTok, LinkedIn, Twitter)
- [ ] Customize prompt per platform:
  - Instagram: Lifestyle-focused, emoji-friendly
  - LinkedIn: Professional, B2B angle
  - TikTok: Trendy, casual, hook-focused
  - Twitter: Short, witty, engagement-focused
- [ ] Update Gemini prompt to vary tone per platform

#### Phase 3B: Tone & Style Selector

- [ ] Add tone options:
  - Professional
  - Casual
  - Humorous
  - Inspirational
  - Urgent/FOMO
- [ ] Add industry selector:
  - E-commerce
  - SaaS
  - Food & Beverage
  - Fitness
  - Fashion
  - Tech
- [ ] Create industry-specific prompts in Gemini

#### Phase 3C: Advanced Customization

- [ ] Allow users to edit generated content before image creation
- [ ] Allow custom hashtag input
- [ ] Font/color customization in image overlay
- [ ] Add filters/effects to generated images

---

### Phase 4: Backend Features

#### Phase 4A: User Authentication

- [ ] Integrate Supabase for auth (JWT-based)
- [ ] Add user table to database
- [ ] Protect `/generate` endpoint with auth middleware
- [ ] Track user_id with each post
- [ ] Implement login/logout on frontend

#### Phase 4B: Rate Limiting & Quotas

- [ ] Add rate limiting middleware (e.g., slowapi)
- [ ] Limit: 10 generations per hour per user
- [ ] Add usage tracking in database
- [ ] Return remaining quota in API response
- [ ] Display quota on frontend

#### Phase 4C: Cloud Storage & CDN

- [ ] Integrate Supabase Storage (S3-like)
- [ ] Store generated images in cloud
- [ ] Return CDN URL instead of local path
- [ ] Clean up old local images
- [ ] Implement image expiration (delete after 30 days)

---

### Phase 5: Advanced Features

#### Phase 5A: Batch Generation

- [ ] Allow multiple topics in single request
- [ ] Generate multiple variations of same topic
- [ ] ZIP download for batch results

#### Phase 5B: Analytics & Insights

- [ ] Track which content performs best
- [ ] Analyze hashtag effectiveness
- [ ] Suggest improvements to captions
- [ ] A/B test different tones

#### Phase 5C: Integration & Automation

- [ ] Direct posting to social platforms (Twitter, LinkedIn API)
- [ ] Schedule posts for future posting
- [ ] Social media calendar view
- [ ] Webhook for platform notifications

#### Phase 5D: AI Improvements

- [ ] Fine-tune prompts based on engagement
- [ ] Multi-model support (Claude, GPT-4, etc.)
- [ ] Image generation (beyond overlays) - DALL-E, Midjourney
- [ ] Context memory for consistent branding

---

## Setup & Deployment

### Development Setup

#### Prerequisites

- Python 3.11+ with pip
- Node.js 20+ with npm
- Git
- GEMINI_API_KEY from Google AI Studio

#### Backend Setup

```bash
# Navigate to backend
cd social-engine-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Start backend
uvicorn main:app --reload
# Backend runs on http://127.0.0.1:8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd social-engine-ui

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:3000
```

#### Database Initialization

- Automatic on first backend startup
- Creates `database.db` with schema
- Seeds default template

---

### Environment Variables

**Backend (.env file):**

```env
GEMINI_API_KEY=your_google_genai_api_key_here
```

**Get API Key:**

1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Create new project or select existing
4. Copy API key
5. Paste in .env file

---

### Running the Full Stack

**Terminal 1 - Backend:**

```bash
cd social-engine-api
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Mac/Linux
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**

```bash
cd social-engine-ui
npm run dev
```

**Browser:**

- Open http://localhost:3000
- System is ready to use

---

## Testing Guide

### Manual API Testing

**Test 1: Fetch Templates**

```bash
curl http://127.0.0.1:8000/templates
```

Expected Output:

```json
[
  {
    "id": 1,
    "name": "Standard Portrait",
    "frame_size": "1080x1350"
  }
]
```

---

**Test 2: Generate Content**

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"Organic Tea Brand","template_id":1}'
```

Expected Output:

```json
{
  "status": "success",
  "headline": "Pure Wellness in Every Sip",
  "hook": "Discover authentic organic tea traditions...",
  "caption": "Experience the harmony of nature with...",
  "cta": "Shop Our Collection Today",
  "hashtags": ["#OrganicTea", "#WellnessJourney", ...],
  "image_path": "outputs/gen_Organic_1.png"
}
```

---

**Test 3: Download Generated Image**

```bash
# From browser or curl
curl http://127.0.0.1:8000/outputs/gen_Organic_1.png > image.png
```

---

### Frontend Testing

1. **Navigation Test**
   - Click "Dashboard" (placeholder shows)
   - Click "Create Post" (form displays)

2. **Generation Test**
   - Enter topic (e.g., "Fitness Center")
   - Select template
   - Click "Generate Content & Image"
   - Wait for loading
   - Verify structured sections display

3. **Display Test**
   - Headline: Should be gold, large text
   - Hook: Should be white, readable
   - Caption: Should be gray, wrapped
   - CTA: Should be in blue box
   - Hashtags: Should be cyan pills
   - Image: Should display preview

4. **Download Test**
   - Click download button
   - Verify image downloads to Downloads folder

---

### Database Testing

**View All Posts:**

```bash
sqlite3 social-engine-api/database.db "SELECT topic, headline, cta FROM posts;"
```

**Count Posts:**

```bash
sqlite3 social-engine-api/database.db "SELECT COUNT(*) FROM posts;"
```

**View Specific Post:**

```bash
sqlite3 social-engine-api/database.db "SELECT * FROM posts WHERE topic='Coffee Shop' LIMIT 1;"
```

---

## File Structure Reference

```
c:\Users\rajat\Desktop\AI Image Gen Project\
├── .git/                          # Git repository
├── .gitignore                     # Git ignore rules
├── PROJECT_DOCUMENTATION.md       # ← This file
│
├── social-engine-api/             # Backend FastAPI application
│   ├── main.py                    # FastAPI routes & Gemini integration
│   ├── database.py                # SQLite schema initialization
│   ├── generators.py              # Pillow image generation
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (GEMINI_API_KEY)
│   ├── venv/                      # Python virtual environment
│   ├── templates/                 # Base template images
│   │   └── template_1.png         # 1080x1350 portrait template
│   ├── outputs/                   # Generated images (auto-created)
│   │   ├── gen_Artisan_1.png
│   │   ├── gen_Coffee_1.png
│   │   └── gen_Spa_1.png
│   ├── database.db                # SQLite database (auto-created)
│   └── __pycache__/               # Python cache
│
└── social-engine-ui/              # Frontend Next.js application
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx           # Main page (dashboard + create)
    │   │   ├── layout.tsx         # Root layout
    │   │   └── globals.css        # Global styles
    │   └── components/            # Reusable components (future)
    ├── public/                    # Static assets
    ├── package.json               # Node dependencies
    ├── tsconfig.json              # TypeScript configuration
    ├── next.config.ts             # Next.js configuration
    ├── eslint.config.mjs          # ESLint rules
    ├── tailwind.config.mjs        # Tailwind CSS configuration
    ├── postcss.config.mjs         # PostCSS configuration
    ├── next-env.d.ts              # Next.js type definitions
    ├── node_modules/              # Node packages (ignored in git)
    ├── .next/                     # Next.js build output (ignored in git)
    ├── AGENTS.md                  # AI agent instructions (optional)
    ├── CLAUDE.md                  # Claude-specific instructions (optional)
    └── README.md                  # Frontend-specific README
```

---

## Key Metrics & Statistics

### Current Performance

- **Gemini Response Time:** ~2-5 seconds
- **Image Generation Time:** ~0.5-1 second
- **Total End-to-End Time:** ~3-6 seconds
- **Image File Size:** ~50-150 KB per image
- **Database Query Time:** <10ms

### Estimated Costs (Monthly at Scale)

- **Gemini API:** ~$0.005 per 1M tokens (~$5 for 1M requests)
- **Cloud Storage:** ~$0.023 per GB (~$23 for 1TB)
- **Bandwidth:** ~$0.12 per GB (~$120 for 1TB outbound)

---

## Debugging Guide

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`

- **Solution:** Activate virtual environment before running backend
  ```bash
  .\venv\Scripts\Activate.ps1
  ```

**Issue:** `table posts has no column named headline`

- **Solution:** Delete database.db and restart backend (triggers fresh schema)
  ```bash
  Remove-Item database.db
  ```

**Issue:** `Connection refused: [Errno 10061]` (Can't connect to backend)

- **Solution:** Ensure backend is running on port 8000
  ```bash
  uvicorn main:app --reload
  ```

**Issue:** `GEMINI_API_KEY not found in environment`

- **Solution:** Create .env file in backend directory
  ```bash
  echo "GEMINI_API_KEY=your_key" > .env
  ```

**Issue:** Gemini returns markdown code blocks instead of JSON

- **Solution:** Already handled by fallback parsing in main.py

---

## For LLM Assistants

### Context Summary for Next Development

When continuing development, focus on:

1. **Current Priority:** Production database migration (Phase 2B)
   - Remove DROP TABLE behavior
   - Implement CREATE TABLE IF NOT EXISTS
   - Test data persistence

2. **Quick Wins:** Multiple template support (Phase 2C)
   - Add landscape template (1920x1080)
   - Add square template (1080x1080)
   - Minimal code changes needed

3. **Dashboard Implementation:** History display (Phase 2D)
   - Create `/history` endpoint
   - Update frontend to show past generations
   - Add basic statistics

4. **Known Gotchas:**
   - Database schema changes require server restart
   - Gemini API calls are rate-limited (use tenacity retry)
   - Image overlays position relative to 1080x1350 template size
   - Frontend expects structured JSON response from `/generate`

5. **Testing Approach:**
   - Always test API endpoints before frontend changes
   - Use curl for quick API validation
   - Check database.db directly for schema verification
   - Verify image files exist in outputs/ before checking display

---

## Version History

| Version | Date         | Changes                                                                         |
| ------- | ------------ | ------------------------------------------------------------------------------- |
| 1.0     | May 27, 2026 | Phase 2 Part 1 Complete: Structured JSON, Multi-layer overlays, Database schema |
| 0.9     | May 27, 2026 | Phase 1 Complete: FastAPI + Next.js boilerplate, CORS, Gemini integration       |

---

## Contact & References

- **Framework Docs:**
  - FastAPI: https://fastapi.tiangolo.com/
  - Next.js: https://nextjs.org/docs
  - Pillow: https://python-pillow.org/
  - Tailwind CSS: https://tailwindcss.com/docs

- **API Docs:**
  - Gemini AI: https://ai.google.dev/docs/
  - Tenacity: https://tenacity.readthedocs.io/

- **Database:**
  - SQLite: https://www.sqlite.org/docs.html

---

**Last Updated:** May 27, 2026  
**Documentation Status:** Complete for Phase 2 Part 1  
**Ready for:** Phase 2B - Database Production Migration

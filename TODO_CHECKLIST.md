# BrandEngine AI - Complete TODO Checklist

## Target Workflow Flow
1. Choose Platform → 2. Choose Goal → 3. Enter Business Info → 4. Choose Template → 5. AI Generates Preview → 6. User Edits Text → 7. Export/Download

---

## PHASE 1: Enhanced Database Schema

### Tables to Create/Update

#### 1.1 `platforms` table
```sql
CREATE TABLE platforms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- "Instagram", "LinkedIn", "Facebook"
    key TEXT UNIQUE NOT NULL,     -- "instagram", "linkedin", "facebook"
    description TEXT,
    icon TEXT,                    -- emoji or icon name
    max_headline_chars INTEGER DEFAULT 60,
    max_hook_chars INTEGER DEFAULT 100,
    text_density TEXT DEFAULT 'minimal'  -- "minimal", "medium", "maximal"
);
```
- [ ] Create platforms table
- [ ] Seed Instagram, LinkedIn, Twitter/X, Facebook rows
- [ ] Seed platform-specific rules (text density, char limits)

#### 1.2 `goals` table
```sql
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,            -- "Engagement", "Educational", "Promotional", "Authority", "Motivational"
    key TEXT UNIQUE NOT NULL,      -- "engagement", "educational", "promotional", "authority", "motivational"
    description TEXT,
    template_style TEXT,           -- hook-focused, value-driven, cta-heavy
    default_cta_style TEXT
);
```
- [ ] Create goals table
- [ ] Seed 5 goal types

#### 1.3 `template_elements` table (TEMPLATE MAPPING ENGINE)
```sql
CREATE TABLE template_elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    element_key TEXT NOT NULL,      -- "headline", "subheading", "hook", "cta"
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    font_size INTEGER DEFAULT 48,
    max_lines INTEGER DEFAULT 2,
    max_chars INTEGER,
    alignment TEXT DEFAULT 'left',  -- "left", "center", "right"
    color_hex TEXT,
    FOREIGN KEY (template_id) REFERENCES templates(id)
);
```
- [ ] Create template_elements table
- [ ] Define elements for each of 5 templates
- [ ] Seed element positioning data

#### 1.4 `generation_sessions` table (tracks full workflow)
```sql
CREATE TABLE generation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    platform_id INTEGER,
    goal_id INTEGER,
    topic TEXT,
    industry TEXT,
    target_audience TEXT,
    tone TEXT DEFAULT 'professional',
    cta_text TEXT,
    template_id INTEGER,
    brand_kit_id INTEGER,
    content_angle TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id),
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (brand_kit_id) REFERENCES brand_kits(id)
);
```
- [ ] Create generation_sessions table

#### 1.5 Update `posts` table
- [ ] Add `platform_id` column
- [ ] Add `goal_id` column  
- [ ] Add `subheading` column
- [ ] Add `industry` column
- [ ] Add `tone` column
- [ ] Add `target_audience` column

---

## PHASE 2: Backend - Content Strategy Engine

### 2.1 Platform Endpoints
- [ ] `GET /api/v1/platforms` - List all platforms with rules
- [ ] `GET /api/v1/goals` - List all goals

### 2.2 Smart Content Generation (Enhanced Gemini Prompt)
- [ ] Create `generate_content_strategy()` function
  - Input: platform, goal, topic, industry, audience, tone, cta
  - Output: structured creative brief + content
- [ ] Update Gemini prompt to be **platform-aware**
  - Instagram: short punchy hook, emotional, visual-first
  - LinkedIn: authority-driven, professional, slightly longer
  - Twitter: ultra-concise, witty, hook-heavy
  - Facebook: conversational, community tone
- [ ] Create **goal-based prompt templates**
  - Engagement → curiosity, question-based hooks
  - Educational → value-driven, list-style headlines
  - Promotional → urgency, benefit-focused
  - Authority → data-driven, thought leadership
  - Motivational → inspirational, aspirational

### 2.3 Template Mapping Engine
- [ ] `GET /api/v1/templates?platform=instagram&goal=engagement`
  - Filter templates by platform compatibility
- [ ] Update `GET /api/v1/templates` to include template_elements data
- [ ] Auto-adjust font size based on text length (overflow prevention)

### 2.4 Content Safety & Validation
- [ ] Text overflow detection
- [ ] Max line break enforcement
- [ ] Spammy language filter
- [ ] Character limit per element

### 2.5 Generation Session Endpoint
- [ ] `POST /api/v1/generate-v2` (enhanced version)
  - Input: { platform_id, goal_id, topic, industry, audience, tone, cta, template_id, brand_kit_id }
  - Internal: Strategy → Copy gen → Template mapping → Design generation
  - Output: { headline, subheading, hook, cta, content_angle, design_rules, image_path }

---

## PHASE 3: Frontend - New Workflow UI

### 3.1 Step-by-Step Form (Replace current single-page form)
- [ ] **Step 1: Platform Selection**
  - Visual card grid (Instagram, LinkedIn, Twitter, Facebook)
  - Platform icon + name
  - Brief description
- [ ] **Step 2: Goal Selection**
  - 5 goal cards with icons
  - Engagement, Educational, Promotional, Authority, Motivational
- [ ] **Step 3: Business Info**
  - Topic/Post topic (required)
  - Industry dropdown (optional)
  - Target audience (optional)
  - Tone selector (Professional, Casual, Humorous, Inspirational, Urgent)
  - CTA input (optional)
- [ ] **Step 4: Template Selection**
  - Visual grid of templates filtered by platform
  - Template preview thumbnails
  - Platform compatibility badges

### 3.2 Result Display (Enhanced)
- [ ] Show content strategy (goal, angle)
- [ ] Display: headline, subheading, hook, cta
- [ ] Image preview with injected text
- [ ] "Edit Text" button (inline editing)
- [ ] "Regenerate" button for specific elements

### 3.3 Smart Features
- [ ] Text length indicator (shows remaining chars per platform)
- [ ] Auto brand colors applied in preview
- [ ] Platform-optimized display hints

---

## PHASE 4: Enhanced Canvas Editor

### 4.1 Update for New Template System
- [ ] Read template_elements for positioning guides
- [ ] Show element boundaries on canvas
- [ ] Platform-specific sizing guides

---

## IMPLEMENTATION ORDER

### Week 1: Database + Backend Core
- [ ] PHASE 1.1: Platforms table + seed
- [ ] PHASE 1.2: Goals table + seed
- [ ] PHASE 1.3: Template elements table + seed
- [ ] PHASE 1.4: Generation sessions table
- [ ] PHASE 1.5: Update posts table
- [ ] PHASE 2.1: Platform + Goal endpoints
- [ ] PHASE 2.2: Enhanced Gemini prompts (platform + goal aware)

### Week 2: Backend Engine + Frontend Steps 1-2
- [ ] PHASE 2.3: Template mapping engine
- [ ] PHASE 2.4: Content safety
- [ ] PHASE 2.5: Generation v2 endpoint
- [ ] PHASE 3.1: Step 1 - Platform selection UI
- [ ] PHASE 3.1: Step 2 - Goal selection UI

### Week 3: Frontend Steps 3-4 + Result Display
- [ ] PHASE 3.1: Step 3 - Business info form
- [ ] PHASE 3.1: Step 4 - Template selection grid
- [ ] PHASE 3.2: Enhanced result display
- [ ] PHASE 3.3: Smart features (char count, brand colors)

### Week 4: Polish
- [ ] PHASE 4: Canvas Editor updates
- [ ] Error handling
- [ ] Performance optimization
- [ ] Testing

---

## START HERE: PHASE 1.1 - Platforms Table (Database Schema)
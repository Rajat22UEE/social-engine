# Action Steps: Scheduling & Publishing Implementation
**Project:** Social Media Content Scheduling & Publishing Platform  
**Date:** May 27, 2026  
**Scope:** Scheduling (FEAT-002) + Publishing (FEAT-003)

---

## PHASE 1: BACKEND DATABASE & API SETUP (Scheduling)
### Duration: 3-4 Days

### Step 1.1: Extend Database Schema
**File:** `social-engine-api/database.py`

**Current State:**
- Posts table exists with basic fields (topic, caption, hashtags, image_path, template_id, created_at)
- No scheduling or publishing status fields

**Required Actions:**
1. Add new fields to existing `posts` table:
   - `status` (TEXT) - Values: 'draft', 'scheduled', 'published', 'failed'
   - `scheduled_at` (TIMESTAMP) - When post should be published
   - `published_at` (TIMESTAMP) - When post was actually published
   - `platform` (TEXT) - Target platform: 'instagram', 'facebook', 'twitter', 'tiktok'
   - `platform_post_id` (TEXT) - ID from social platform

2. Create new `scheduled_posts` table:
   - `id` (INTEGER PRIMARY KEY)
   - `post_id` (INTEGER FOREIGN KEY)
   - `platform` (TEXT)
   - `scheduled_at` (TIMESTAMP)
   - `status` (TEXT)
   - `published_at` (TIMESTAMP)
   - `error_message` (TEXT) - For failed posts
   - `created_at` (TIMESTAMP)

3. Create new `publishing_history` table:
   - `id` (INTEGER PRIMARY KEY)
   - `post_id` (INTEGER FOREIGN KEY)
   - `platform` (TEXT)
   - `platform_post_id` (TEXT)
   - `status` (TEXT)
   - `published_at` (TIMESTAMP)
   - `last_updated` (TIMESTAMP)

---

### Step 1.2: Create Scheduling API Endpoints
**File:** `social-engine-api/main.py`

**Current Endpoints:**
- GET `/templates` - ✅ Works
- POST `/generate` - ✅ Works
- GET `/outputs` - ✅ Works (static files)

**New Endpoints Required:**

1. **POST `/schedule`** - Schedule a generated post
   - Input: `{ post_id, platform, scheduled_at }`
   - Output: `{ scheduled_post_id, status, scheduled_at }`
   - Action: Save to `scheduled_posts` table

2. **GET `/scheduled-posts`** - List all scheduled posts
   - Input: Optional filters (platform, status, date_range)
   - Output: Array of scheduled posts with details
   - Action: Query `scheduled_posts` table with filters

3. **GET `/scheduled-posts/{id}`** - Get single scheduled post
   - Input: scheduled_post_id
   - Output: Full scheduled post details
   - Action: Query by ID

4. **PUT `/scheduled-posts/{id}`** - Reschedule a post
   - Input: `{ scheduled_at, platform }`
   - Output: `{ success, updated_fields }`
   - Action: Update `scheduled_at` in database

5. **DELETE `/scheduled-posts/{id}`** - Cancel scheduled post
   - Input: scheduled_post_id
   - Output: `{ success, message }`
   - Action: Delete from `scheduled_posts` table

6. **GET `/posts`** - Get all posts (with pagination)
   - Input: Optional `{ page, limit, status, platform }`
   - Output: Paginated list of posts
   - Action: Query `posts` table with filters

7. **GET `/posts/{id}`** - Get single post details
   - Input: post_id
   - Output: Post with all details + scheduling info
   - Action: Join posts with scheduled_posts

---

### Step 1.3: Create Database Helper Functions
**File:** `social-engine-api/database.py` (new functions)

**Functions Needed:**

1. `save_scheduled_post(post_id, platform, scheduled_at)` → Returns scheduled_post_id
2. `get_scheduled_posts(filters=None, limit=50, offset=0)` → Returns list
3. `get_scheduled_post_by_id(scheduled_post_id)` → Returns dict
4. `update_scheduled_post(scheduled_post_id, updates)` → Returns success
5. `delete_scheduled_post(scheduled_post_id)` → Returns success
6. `get_posts_by_status(status)` → Returns list of posts
7. `update_post_status(post_id, new_status)` → Returns success
8. `save_publishing_history(post_id, platform, platform_post_id, status)` → Returns history_id

---

## PHASE 2: FRONTEND UI FOR SCHEDULING
### Duration: 3-4 Days

### Step 2.1: Create Schedule Page Component
**File:** `social-engine-ui/src/app/page.tsx` (modify + add schedule tab)

**Current State:**
- Has "Create Post" tab ✅
- Has "Dashboard" tab (placeholder)
- No scheduling interface

**Required Actions:**

1. Add new view state: `view = 'schedule'` (in addition to 'create' and 'dashboard')

2. Create new button in sidebar:
   ```
   Schedule Post (new)
   ```

3. Build Schedule Post UI with:
   - List of generated posts (status='draft' or 'published')
   - Date & time picker for scheduling
   - Platform selector (Instagram, Facebook, Twitter, TikTok)
   - Schedule button
   - Cancel button

4. Show scheduled posts calendar view:
   - Visual calendar showing scheduled posts by date
   - Color coding by platform
   - Quick view/edit popup on click

---

### Step 2.2: Create API Call Functions
**File:** `social-engine-ui/src/app/page.tsx` (add helper functions)

**Functions Needed:**

1. `fetchScheduledPosts()` - Get list of scheduled posts
2. `schedulePost(postId, platform, scheduledTime)` - Schedule a post
3. `reschedulePost(scheduledPostId, newTime)` - Reschedule existing
4. `cancelSchedule(scheduledPostId)` - Cancel scheduled post
5. `getPosts()` - Get all posts for selection

---

### Step 2.3: Create Calendar Component (Optional for Phase 1)
**New File:** `social-engine-ui/src/components/ScheduleCalendar.tsx`

**Features:**
- Month view calendar
- Show scheduled posts on calendar
- Click to reschedule
- Drag-to-reschedule (advanced)

---

## PHASE 3: PUBLISHING INTEGRATION (Instagram API)
### Duration: 5-7 Days

### Step 3.1: Set Up Instagram Business API
**Files Affected:** `social-engine-api/main.py`, `social-engine-api/.env`

**Prerequisites:**
- Meta Business Account (required)
- Instagram Business Account (required)
- Facebook App created in Meta Dashboard
- App approved for Instagram Graph API

**Actions:**

1. Create Instagram API handler class:
   ```
   File: social-engine-api/instagram_handler.py
   
   Class: InstagramPublisher
   Methods:
   - authenticate()
   - post_image(image_path, caption, hashtags)
   - get_account_info()
   - get_post_insights(post_id)
   ```

2. Add environment variables to `.env`:
   ```
   INSTAGRAM_ACCESS_TOKEN=...
   INSTAGRAM_BUSINESS_ACCOUNT_ID=...
   INSTAGRAM_APP_ID=...
   INSTAGRAM_APP_SECRET=...
   ```

3. Create publishing function:
   ```python
   async def publish_to_instagram(post_id, image_path, caption, hashtags)
   ```

---

### Step 3.2: Create Publishing Queue System
**New File:** `social-engine-api/publisher_queue.py`

**Components:**

1. Queue Manager:
   - Check for scheduled posts ready to publish (scheduled_at <= now)
   - Execute publishing in order
   - Retry failed posts (up to 3 times)
   - Log results to `publishing_history`

2. Background Task (using APScheduler or similar):
   - Run every 1 minute
   - Check for due scheduled posts
   - Process publishing queue

3. Error Handling:
   - Catch API errors
   - Log error messages
   - Update status to 'failed'
   - Send retry notification

---

### Step 3.3: Add Publishing Endpoints
**File:** `social-engine-api/main.py` (add new endpoints)

**New Endpoints:**

1. **POST `/publish/{id}`** - Manually publish scheduled post immediately
   - Input: scheduled_post_id
   - Output: `{ success, platform_post_id, published_at }`
   - Action: Execute publishing to platform

2. **GET `/publishing-history`** - View all published posts
   - Input: Optional filters (platform, date_range)
   - Output: List of published posts with metrics

3. **GET `/publishing-history/{id}`** - Get publishing details
   - Input: history_id
   - Output: Full publishing info + engagement metrics

4. **POST `/retry-publish/{id}`** - Retry failed publish
   - Input: scheduled_post_id
   - Output: `{ success, error (if failed) }`
   - Action: Re-attempt publishing

---

## PHASE 4: FRONTEND PUBLISHING UI
### Duration: 2-3 Days

### Step 4.1: Add Publishing Tab to UI
**File:** `social-engine-ui/src/app/page.tsx` (modify)

**New View:** `view = 'publish'` or `view = 'publishing-history'`

**UI Elements:**

1. Publishing Queue Status:
   - Number of posts in queue
   - Next scheduled post time
   - Last published post info

2. Publishing History List:
   - Table of published posts
   - Columns: Date, Platform, Caption (preview), Status, Engagement
   - Sort & filter options

3. Manual Publish Button:
   - Select scheduled post
   - Publish immediately button
   - Confirm dialog

---

### Step 4.2: Add Real-time Status Updates
**File:** `social-engine-ui/src/app/page.tsx` (modify)

**Implementation:**
- Poll backend every 10 seconds for scheduled posts
- Show publishing progress notifications
- Display success/failure alerts
- Auto-refresh after publishing completes

---

## PHASE 5: ANALYTICS & DASHBOARD
### Duration: 4-5 Days

### Step 5.1: Add Analytics Endpoints
**File:** `social-engine-api/main.py` (add new endpoints)

**New Endpoints:**

1. **GET `/analytics/overview`** - Dashboard summary
   - Total posts created
   - Scheduled posts count
   - Published posts count
   - Engagement metrics

2. **GET `/analytics/performance`** - Performance by platform
   - Posts per platform
   - Success rate by platform
   - Average engagement per platform

3. **GET `/analytics/trending`** - Trending topics
   - Most used topics
   - Best performing topics
   - Engagement by topic

---

### Step 5.2: Create Dashboard UI
**File:** `social-engine-ui/src/app/page.tsx` (enhance dashboard view)

**Dashboard Components:**

1. Stats Cards:
   - Total posts generated
   - Scheduled posts
   - Published posts
   - Average engagement

2. Charts:
   - Posts per day (line chart)
   - Platform distribution (pie chart)
   - Engagement trend (line chart)

3. Recent Activity:
   - Last 10 posts created
   - Last 10 posts published
   - Quick actions (reschedule, republish)

---

## IMPLEMENTATION PRIORITY & TIMELINE

### Week 1: Phase 1 (Backend Database & API)
- Day 1-2: Database schema design and migration
- Day 3-4: API endpoints development & testing
- **Deliverable:** All scheduling endpoints functional

### Week 2: Phase 2 (Frontend Scheduling UI)
- Day 1-2: UI component creation
- Day 3-4: API integration in frontend
- **Deliverable:** Schedule post functionality working end-to-end

### Week 3: Phase 3 (Instagram Publishing)
- Day 1-2: Instagram API setup & authentication
- Day 3-4: Publishing queue & background task
- Day 5: Manual publish endpoints
- **Deliverable:** Posts can be published to Instagram

### Week 4: Phase 4 (Frontend Publishing UI)
- Day 1-2: Publishing tab and UI
- Day 3-4: Real-time updates & notifications
- **Deliverable:** User can see publishing status in UI

### Week 5: Phase 5 (Analytics)
- Day 1-2: Analytics API endpoints
- Day 3-4: Dashboard UI implementation
- **Deliverable:** Analytics dashboard functional

---

## TESTING CHECKLIST

### Unit Tests Required:
- [ ] Database operations (CRUD for all tables)
- [ ] Scheduling logic (date/time validation)
- [ ] Publishing queue (retry logic, error handling)
- [ ] API endpoints (all 7+ new endpoints)

### Integration Tests Required:
- [ ] End-to-end scheduling workflow
- [ ] End-to-end publishing workflow
- [ ] Multi-platform publishing
- [ ] Error handling & recovery

### Manual Testing Required:
- [ ] Schedule post for future date
- [ ] Reschedule post
- [ ] Cancel scheduled post
- [ ] Publish to Instagram
- [ ] View publishing history
- [ ] Dashboard analytics accuracy

---

## DEPENDENCIES & PREREQUISITES

### New Python Packages (requirements.txt):
```
APScheduler==3.10.x  # For background task scheduling
instagram-business-sdk==x.x.x  # Instagram API
python-dateutil==2.8.x  # Better date/time handling
pytz==2024.x  # Timezone support
```

### Infrastructure:
- Meta Business Account setup
- Instagram Business Account linked
- Facebook App created and approved
- Test Instagram account for publishing

### Configuration:
- Environment variables for API keys
- Timezone settings
- Retry logic configuration
- Rate limiting setup

---

## ESTIMATED EFFORT

| Phase | Days | Complexity | Risk |
|-------|------|-----------|------|
| Phase 1 (Backend) | 3-4 | Medium | Low |
| Phase 2 (Frontend) | 3-4 | Medium | Low |
| Phase 3 (Publishing) | 5-7 | High | High |
| Phase 4 (UI) | 2-3 | Low | Low |
| Phase 5 (Analytics) | 4-5 | Medium | Low |
| **Total** | **18-23** | - | - |

---

## SUCCESS CRITERIA

✅ **Phase 1 Complete:** All database operations working, API returns correct responses  
✅ **Phase 2 Complete:** Users can schedule posts 30+ days in advance  
✅ **Phase 3 Complete:** Posts successfully publish to Instagram  
✅ **Phase 4 Complete:** Users can monitor publishing status in real-time  
✅ **Phase 5 Complete:** Dashboard shows accurate metrics and trends  

---

## RISKS & MITIGATION

| Risk | Mitigation |
|------|-----------|
| Instagram API rate limiting | Implement queue with exponential backoff |
| Image upload failures | Retry logic + fallback notifications |
| Timezone issues | Use UTC in DB, convert on frontend |
| Concurrent scheduling conflicts | Database transactions & locks |
| API key compromise | Rotate keys, use environment variables |

---

**Next Step:** Await approval to proceed with Phase 1 implementation.

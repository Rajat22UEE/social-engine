# Product Requirements Document (PRD)
## Social Media Content Scheduling & Publishing Platform

**Document Version:** 1.0  
**Last Updated:** May 27, 2026  
**Status:** MVP Phase

---

## 1. Executive Summary

The Social Media Content Scheduling & Publishing Platform (Social Engine) is an AI-powered application that automates content creation and management for social media. The system enables users to generate Instagram-ready content (captions, hashtags, and visual assets) by leveraging AI (Google Gemini) and provides a user-friendly interface for content management.

**Core Value Proposition:**
- Automated AI-driven content generation for social media
- One-click image generation with custom templates
- Scheduling and publishing capabilities
- Centralized content management dashboard

---

## 2. Product Overview

### 2.1 Scope
This PRD covers the content scheduling and publishing features for the Social Engine platform:
- Content creation workflow
- Scheduling engine
- Publishing automation
- Analytics and tracking

### 2.2 Target Users
- Social media managers
- Content creators
- Small to medium business owners
- Marketing agencies

### 2.3 Success Criteria
- [ ] 100+ posts scheduled within first month
- [ ] Average content generation time < 30 seconds
- [ ] 95% successful post publication rate
- [ ] User engagement tracking implemented

---

## 3. Current Architecture

### 3.1 Technology Stack

**Backend:**
- FastAPI (Python)
- SQLite3 (Database)
- Google Generative AI (Gemini 2.5 Flash)
- Pillow (Image Processing)
- UVicorn (ASGI Server)

**Frontend:**
- Next.js 16.2.6
- React 19.2.4
- TypeScript
- Tailwind CSS
- Lucide React (Icons)

### 3.2 System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                   │
│  - Create Post UI                                        │
│  - Dashboard (Planned)                                   │
│  - Template Selection                                    │
│  - Result Display & Download                            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ HTTP/JSON
                  ↓
┌─────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                     │
│  ├─ /templates (GET) - Retrieve available templates     │
│  ├─ /generate (POST) - Create content & images          │
│  └─ /outputs (Static Files) - Serve generated images    │
└─────────────┬───────────────────────────────────────────┘
              │
              ├─────────────────┬────────────────────┐
              ↓                 ↓                    ↓
        ┌──────────┐      ┌────────────┐      ┌─────────┐
        │ SQLite3  │      │ Gemini AI  │      │ Pillow  │
        │ Database │      │ API        │      │ (Images)│
        └──────────┘      └────────────┘      └─────────┘
```

---

## 4. Feature Requirements

### 4.1 Content Creation (IMPLEMENTED)

**Requirement ID:** FEAT-001  
**Status:** MVP

#### 4.1.1 AI-Powered Caption Generation
- **Description:** Generate Instagram captions and hashtags using Google Gemini AI
- **Input:** Content topic (text)
- **Output:** Caption text + 5 hashtags
- **Acceptance Criteria:**
  - Captions must be Instagram-friendly (under 2,200 characters)
  - Hashtags must be relevant to the topic
  - Response time: < 10 seconds
  - Retry logic on API failure (up to 3 attempts)

#### 4.1.2 Image Generation
- **Description:** Create visual assets using predefined templates with text overlays
- **Input:** Topic, caption text, selected template
- **Output:** PNG image file (1080x1350px)
- **Acceptance Criteria:**
  - Image dimensions must be Instagram-optimized
  - Text must be readable and centered
  - File size < 5MB
  - Saved in `/outputs` directory

#### 4.1.3 Template Management
- **Description:** Store and retrieve image templates for content generation
- **Current Templates:** 1 (Standard Portrait - 1080x1350)
- **Database Schema:**
  - `id` (Primary Key)
  - `name` (Template name)
  - `frame_size` (Dimensions: WIDTHxHEIGHT)
  - `config_json` (Layout configuration)

### 4.2 Content Scheduling (PLANNED)

**Requirement ID:** FEAT-002  
**Status:** Backlog

#### 4.2.1 Schedule Management
- Allow users to schedule posts for future publication
- Support bulk scheduling (multiple posts)
- Time zone support for global scheduling
- **Database Fields to Add:**
  - `scheduled_at` (TIMESTAMP)
  - `status` (ENUM: draft, scheduled, published, failed)
  - `platform` (ENUM: instagram, facebook, twitter, tiktok)
  - `published_at` (TIMESTAMP)

#### 4.2.2 Calendar View
- Visual calendar interface for scheduled posts
- Drag-and-drop rescheduling
- Conflict detection and resolution
- Preview generation before publication

### 4.3 Publishing Integration (PLANNED)

**Requirement ID:** FEAT-003  
**Status:** Backlog

#### 4.3.1 Multi-Platform Support
- Instagram direct posting (via Business API)
- Facebook integration
- Twitter/X integration
- TikTok integration
- LinkedIn scheduling

#### 4.3.2 Automated Publishing Queue
- Queue system for scheduled posts
- Automatic retry on failure
- Error logging and notifications
- Success/failure callbacks

#### 4.3.3 Analytics Tracking
- Post performance metrics
- Engagement tracking (likes, comments, shares)
- Audience insights
- Content performance reports

### 4.4 Dashboard & Analytics (PLANNED)

**Requirement ID:** FEAT-004  
**Status:** Backlog

#### 4.4.1 Content Dashboard
- Overview of published/scheduled posts
- Performance statistics
- Content calendar
- Bulk operations (delete, reschedule, clone)

#### 4.4.2 Analytics Reports
- Weekly/monthly performance summaries
- Trending content analysis
- Best posting times
- Audience demographics

---

## 5. Database Schema

### 5.1 Current Tables

#### Templates Table
```sql
CREATE TABLE templates (
  id INTEGER PRIMARY KEY,
  name TEXT,
  frame_size TEXT,
  config_json TEXT
)
```

#### Posts Table
```sql
CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  topic TEXT,
  caption TEXT,
  hashtags TEXT,
  image_path TEXT,
  template_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (template_id) REFERENCES templates(id)
)
```

### 5.2 Planned Extensions

#### Scheduled Posts Table
```sql
CREATE TABLE scheduled_posts (
  id INTEGER PRIMARY KEY,
  post_id INTEGER NOT NULL,
  platform TEXT NOT NULL,
  scheduled_at TIMESTAMP NOT NULL,
  status TEXT DEFAULT 'scheduled',
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id)
)
```

#### Publishing History Table
```sql
CREATE TABLE publishing_history (
  id INTEGER PRIMARY KEY,
  post_id INTEGER NOT NULL,
  platform TEXT,
  platform_post_id TEXT,
  status TEXT,
  engagement_count INTEGER DEFAULT 0,
  published_at TIMESTAMP,
  last_updated TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id)
)
```

---

## 6. API Specifications

### 6.1 Current Endpoints

#### GET /templates
- **Description:** Retrieve all available templates
- **Response:**
```json
[
  {
    "id": 1,
    "name": "Standard Portrait",
    "frame_size": "1080x1350"
  }
]
```

#### POST /generate
- **Description:** Generate content and image for a post
- **Request:**
```json
{
  "topic": "string (required)",
  "template_id": "integer (required)"
}
```
- **Response:**
```json
{
  "content": "string (caption + hashtags)",
  "image_path": "string (relative path to generated image)",
  "status": "success|error"
}
```

### 6.2 Planned Endpoints

#### GET /posts
- Retrieve all posts with pagination and filters

#### GET /posts/{id}
- Retrieve specific post details

#### POST /posts/{id}/schedule
- Schedule a post for publication

#### GET /schedule
- Retrieve scheduled posts calendar view

#### POST /publish/{id}
- Manually publish a scheduled post

#### GET /analytics
- Retrieve performance analytics

---

## 7. Implementation Roadmap

### Phase 1: MVP (Current)
- ✅ Content generation
- ✅ Image creation
- ⚠️ Basic UI

### Phase 2: Scheduling (Next 2 Weeks)
- [ ] Schedule management endpoints
- [ ] Calendar UI
- [ ] Database schema extension
- [ ] Schedule persistence

### Phase 3: Publishing (Weeks 3-4)
- [ ] Instagram API integration
- [ ] Publishing queue system
- [ ] Error handling & retry logic
- [ ] Notification system

### Phase 4: Analytics (Weeks 5-6)
- [ ] Dashboard implementation
- [ ] Analytics collection
- [ ] Reporting features
- [ ] Performance optimization

### Phase 5: Advanced Features (Week 7+)
- [ ] Multi-platform support
- [ ] AI content optimization
- [ ] Competitor analysis
- [ ] Team collaboration

---

## 8. Known Issues & Limitations

### 8.1 Current Issues

| Issue ID | Severity | Description | Status |
|----------|----------|-------------|--------|
| BUG-001 | HIGH | Missing error handling in image generation | Open |
| BUG-002 | MEDIUM | CORS configuration too permissive | Open |
| BUG-003 | MEDIUM | No input validation on topic text | Open |
| BUG-004 | LOW | API key exposed in .env (security risk) | Open |

### 8.2 Limitations

1. **Single Template:** Only one template available (Standard Portrait)
2. **No Scheduling:** Posts are created immediately, no scheduling capability
3. **No Publishing:** Generated content cannot be directly published to platforms
4. **No Authentication:** No user login system implemented
5. **Single Database:** SQLite is suitable for MVP but needs migration to PostgreSQL for production
6. **Limited Analytics:** No engagement tracking implemented
7. **No Rate Limiting:** API endpoints lack rate limiting for cost control

---

## 9. Security Considerations

### 9.1 Implemented
- CORS middleware configured
- Dotenv for API key management

### 9.2 To Be Implemented
- [ ] Input validation and sanitization
- [ ] Rate limiting per user
- [ ] Authentication and authorization
- [ ] API key rotation mechanism
- [ ] HTTPS enforcement
- [ ] Database encryption
- [ ] Audit logging
- [ ] XSS/CSRF protection

---

## 10. Performance Requirements

| Metric | Target | Current |
|--------|--------|---------|
| Content Generation | < 30s | ~10s |
| Image Generation | < 5s | ~2s |
| API Response Time | < 100ms | ~50ms |
| Concurrent Users | 1000+ | 10 (MVP) |
| Database Response | < 50ms | ~10ms |

---

## 11. Success Metrics

### 11.1 Business KPIs
- Monthly active users
- Posts generated per user
- Publishing success rate
- User retention rate

### 11.2 Technical KPIs
- API uptime (target: 99.9%)
- Average response time
- Error rate < 1%
- Database query optimization

---

## 12. Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Gemini API Rate Limiting | HIGH | MEDIUM | Implement queue system & rate limiting |
| Template Image Not Found | MEDIUM | LOW | Add validation & default fallback |
| Database Performance | MEDIUM | LOW | Monitor queries, plan PostgreSQL migration |
| Security Breach | CRITICAL | LOW | Implement auth, encryption, audit logs |

---

## 13. Next Steps

1. **Week 1:** Implement scheduling features (FEAT-002)
2. **Week 2:** Add publishing integration (FEAT-003)
3. **Week 3:** Build analytics dashboard (FEAT-004)
4. **Week 4:** Security hardening and testing
5. **Week 5:** Beta launch to early users

---

## 14. Appendix: Technical Debt

- [ ] Migrate from SQLite to PostgreSQL
- [ ] Add comprehensive error logging
- [ ] Implement proper unit and integration tests
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Optimize image generation performance
- [ ] Implement caching layer (Redis)
- [ ] Add monitoring and alerting
- [ ] Refactor UI components for reusability

---

**Document Owner:** Development Team  
**Last Review Date:** May 27, 2026  
**Next Review Date:** June 10, 2026

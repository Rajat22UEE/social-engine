from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


# =========================================
# TEMPLATE MODEL
# =========================================

@dataclass
class Template:

    id: Optional[int] = None

    name: str = ""

    frame_size: str = ""

    config_json: str = ""

    created_at: Optional[str] = None


# =========================================
# POST MODEL
# =========================================

@dataclass
class Post:

    id: Optional[int] = None

    topic: str = ""

    caption: str = ""

    hashtags: str = ""

    image_path: str = ""

    template_id: Optional[int] = None

    platform: str = ""

    status: str = "draft"

    scheduled_at: Optional[str] = None

    published_at: Optional[str] = None

    created_at: Optional[str] = None


# =========================================
# SCHEDULED POST MODEL
# =========================================

@dataclass
class ScheduledPost:

    id: Optional[int] = None

    post_id: int = 0

    scheduled_time: str = ""

    status: str = "pending"

    created_at: Optional[str] = None


# =========================================
# PUBLISHING HISTORY MODEL
# =========================================

@dataclass
class PublishingHistory:

    id: Optional[int] = None

    post_id: int = 0

    platform: str = ""

    status: str = ""

    response: str = ""

    published_at: Optional[str] = None

    from pydantic import BaseModel


# =========================================
# API REQUEST MODELS
# =========================================

class PostRequest(BaseModel):

    topic: str

    template_id: int

    platform: str


class UpdatePostRequest(BaseModel):

    topic: str | None = None

    caption: str | None = None

    hashtags: str | None = None

    image_path: str | None = None

    template_id: int | None = None

    platform: str | None = None

    status: str | None = None

    published_at: str | None = None


class SchedulePostRequest(BaseModel):

    post_id: int

    scheduled_time: str
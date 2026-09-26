from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Create Content Request
# ==========================================================

class ContentCreate(BaseModel):

    project_id: int

    title: str

    hook: Optional[str] = None

    script: str

    caption: Optional[str] = None

    hashtags: Optional[str] = None

    keywords: Optional[str] = None

    cta: Optional[str] = None

    platform: str

    content_type: str

    language: str = "English"

    ai_provider: Optional[str] = None

    ai_model: Optional[str] = None

    prompt: Optional[str] = None


# ==========================================================
# Update Content Request
# ==========================================================

class ContentUpdate(BaseModel):

    description: Optional[str] = None

    title: Optional[str] = None

    hook: Optional[str] = None

    script: Optional[str] = None

    caption: Optional[str] = None

    hashtags: Optional[str] = None

    keywords: Optional[str] = None

    cta: Optional[str] = None

    platform: Optional[str] = None

    content_type: Optional[str] = None

    language: Optional[str] = None

    ai_provider: Optional[str] = None

    ai_model: Optional[str] = None

    prompt: Optional[str] = None

    status: Optional[str] = None

    generation_config: Optional[dict[str, Any]] = None


# ==========================================================
# Content Response
# ==========================================================

class ContentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    project_id: int

    title: str

    hook: Optional[str]

    script: str

    caption: Optional[str]

    hashtags: Optional[str]

    keywords: Optional[str]

    cta: Optional[str]

    platform: str

    content_type: str

    language: str

    ai_provider: Optional[str]

    ai_model: Optional[str]

    prompt: Optional[str]

    status: str

    generation_config: Optional[dict[str, Any]] = None

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Create Response
# ==========================================================

class ContentCreateResponse(BaseModel):

    success: bool

    message: str

    content: ContentResponse


# ==========================================================
# Update Response
# ==========================================================

class ContentUpdateResponse(BaseModel):

    success: bool

    message: str

    content: ContentResponse


# ==========================================================
# Single Content Response
# ==========================================================

class ContentSingleResponse(BaseModel):

    success: bool

    content: ContentResponse


# ==========================================================
# List Response
# ==========================================================

class ContentListResponse(BaseModel):

    success: bool

    total: int

    contents: list[ContentResponse]


# ==========================================================
# Delete Response
# ==========================================================

class ContentDeleteResponse(BaseModel):

    success: bool

    message: str


# ==========================================================
# Generic Message
# ==========================================================

class ContentMessage(BaseModel):

    success: bool

    message: str

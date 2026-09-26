from typing import Any, List, Optional, Literal

from pydantic import BaseModel, Field


# ==========================================================
# AI Generate Request
# ==========================================================

class GenerateRequest(BaseModel):

    project_id: int = Field(..., gt=0)

    platforms: List[str]

    content_types: List[str]

    niche: str

    topic: str

    package: str

    language: Optional[str] = "English"

    provider: Optional[str] = "auto"
    providers: Optional[List[str]] = None

    outputs: Optional[List[str]] = None

    scene_count: Optional[int] = Field(None, ge=1, le=12)
    total_duration: Optional[int] = Field(None, ge=5, le=180)
    style: Optional[str] = Field(None, max_length=50)
    content_goal: Optional[Literal["Reach", "Shares", "Saves", "Comments", "Followers"]] = None
    visual_style: Optional[Literal["minimal", "bold", "cinematic", "professional", "playful", "scrapbook"]] = None


# ==========================================================
# AI Generated Content
# ==========================================================

class SceneItem(BaseModel):

    scene: Optional[int]

    title: Optional[str] = ""

    text: Optional[str] = ""

    keyword: Optional[str] = ""

    image_prompt: Optional[str] = ""

    video_prompt: Optional[str] = ""

    media_type: Optional[str] = "image"

    duration: Optional[int] = 5

    platform: Optional[str] = ""


class AIContent(BaseModel):

    title: str

    hook: Optional[str] = ""

    description: Optional[str] = ""

    script: Optional[str] = ""

    script: str

    caption: str

    hashtags: List[str] = []

    keywords: List[str] = []

    cta: Optional[str] = ""

    story: Optional[str] = ""

    scenes: List[SceneItem] = []


# ==========================================================
# AI Generate Response
# ==========================================================

class GenerateResponse(BaseModel):

    success: bool

    provider: str

    content_id: int

    branding: Optional[dict[str, Any]] = None

    data: Any


# ==========================================================
# AI Error Response
# ==========================================================

class AIErrorResponse(BaseModel):

    success: bool

    error: str

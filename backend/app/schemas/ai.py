from typing import Any, List, Optional

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

    provider: Optional[str] = "groq"
    providers: Optional[List[str]] = None

    outputs: Optional[List[str]] = None


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

    data: Any


# ==========================================================
# AI Error Response
# ==========================================================

class AIErrorResponse(BaseModel):

    success: bool

    error: str
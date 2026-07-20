from typing import List, Optional

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


# ==========================================================
# AI Generated Content
# ==========================================================

class AIContent(BaseModel):

    title: str

    hook: str

    script: str

    caption: str

    hashtags: List[str] = []

    keywords: List[str] = []

    cta: str


# ==========================================================
# AI Generate Response
# ==========================================================

class GenerateResponse(BaseModel):

    success: bool

    provider: str

    content_id: int

    data: AIContent


# ==========================================================
# AI Error Response
# ==========================================================

class AIErrorResponse(BaseModel):

    success: bool

    error: str
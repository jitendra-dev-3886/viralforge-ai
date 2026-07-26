from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Create Scene
# ==========================================================

class SceneCreate(BaseModel):

    project_id: int

    content_id: int

    scene_number: int

    text: str

    keyword: Optional[str] = None

    media_type: str = "image"

    duration: int = 5

    media_id: Optional[int] = None

    status: str = "pending"


# ==========================================================
# Update Scene
# ==========================================================

class SceneUpdate(BaseModel):

    text: Optional[str] = None

    keyword: Optional[str] = None

    media_type: Optional[str] = None

    duration: Optional[int] = None

    media_id: Optional[int] = None

    status: Optional[str] = None


# ==========================================================
# Scene Response
# ==========================================================

class SceneResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    project_id: int

    content_id: int

    scene_number: int

    text: str

    keyword: Optional[str]

    media_type: str

    duration: int

    media_id: Optional[int]

    status: str

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Create Response
# ==========================================================

class SceneCreateResponse(BaseModel):

    success: bool

    message: str

    scene: SceneResponse


# ==========================================================
# List Response
# ==========================================================

class SceneListResponse(BaseModel):

    success: bool

    total: int

    scenes: list[SceneResponse]


# ==========================================================
# Message Response
# ==========================================================

class SceneMessage(BaseModel):

    success: bool

    message: str
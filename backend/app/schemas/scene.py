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

    title: Optional[str] = None

    text: str

    keyword: Optional[str] = None

    image_prompt: Optional[str] = None

    video_prompt: Optional[str] = None

    voice_text: Optional[str] = None

    subtitle: Optional[str] = None

    camera_angle: Optional[str] = None

    transition: Optional[str] = None

    media_type: str = "image"

    duration: int = 5

    media_id: Optional[int] = None

    status: str = "pending"


# ==========================================================
# Update Scene
# ==========================================================

class SceneUpdate(BaseModel):

    title: Optional[str] = None

    text: Optional[str] = None

    keyword: Optional[str] = None

    image_prompt: Optional[str] = None

    video_prompt: Optional[str] = None

    voice_text: Optional[str] = None

    subtitle: Optional[str] = None

    camera_angle: Optional[str] = None

    transition: Optional[str] = None

    media_type: Optional[str] = None

    duration: Optional[int] = None

    media_id: Optional[int] = None

    status: Optional[str] = None


class SceneReorder(BaseModel):
    scene_ids: list[int]


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

    title: Optional[str]

    text: str

    keyword: Optional[str]

    image_prompt: Optional[str]

    video_prompt: Optional[str]

    voice_text: Optional[str]

    subtitle: Optional[str]

    camera_angle: Optional[str]

    transition: Optional[str]

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
# Scene List
# ==========================================================

class SceneListResponse(BaseModel):

    success: bool

    total: int

    scenes: list[SceneResponse]


# ==========================================================
# Generic Response
# ==========================================================

class SceneMessage(BaseModel):

    success: bool

    message: str

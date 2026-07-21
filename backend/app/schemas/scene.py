from pydantic import BaseModel
from typing import Optional


# ==========================================================
# Create Scene
# ==========================================================

class SceneCreate(BaseModel):

    user_id: int

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
# Response
# ==========================================================

class SceneResponse(BaseModel):

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

    class Config:
        from_attributes = True
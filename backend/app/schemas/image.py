from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Generate Image
# ==========================================================

class ImageCreate(BaseModel):

    project_id: int

    content_id: int

    scene_id: int

    provider: str = "pollinations"

    model: Optional[str] = None

    prompt: str

    negative_prompt: Optional[str] = None

    width: int = 1024

    height: int = 1024


# ==========================================================
# Update Image
# ==========================================================

class ImageUpdate(BaseModel):

    provider: Optional[str] = None

    model: Optional[str] = None

    prompt: Optional[str] = None

    negative_prompt: Optional[str] = None

    width: Optional[int] = None

    height: Optional[int] = None

    status: Optional[str] = None

    error_message: Optional[str] = None


# ==========================================================
# Image Response
# ==========================================================

class ImageResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    project_id: int

    content_id: int

    scene_id: int

    provider: str

    model: Optional[str]

    prompt: str

    negative_prompt: Optional[str]

    image_name: Optional[str]

    image_path: Optional[str]

    image_url: Optional[str]

    width: int

    height: int

    file_size: Optional[int]

    status: str

    error_message: Optional[str]

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Generate Image Response
# ==========================================================

class ImageCreateResponse(BaseModel):

    success: bool

    message: str

    image: ImageResponse


# ==========================================================
# Image List Response
# ==========================================================

class ImageListResponse(BaseModel):

    success: bool

    total: int

    images: list[ImageResponse]


# ==========================================================
# Generic Message
# ==========================================================

class ImageMessage(BaseModel):

    success: bool

    message: str
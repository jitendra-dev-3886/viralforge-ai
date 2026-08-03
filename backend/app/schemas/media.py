from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Create Media
# ==========================================================

class MediaCreate(BaseModel):

    user_id: int

    project_id: int

    media_type: str

    provider: Optional[str] = None

    title: Optional[str] = None

    file_name: str

    file_path: str

    file_url: Optional[str] = None

    mime_type: Optional[str] = None

    extension: Optional[str] = None

    duration: Optional[int] = None

    width: Optional[int] = None

    height: Optional[int] = None

    file_size: Optional[int] = None

    status: Optional[str] = "ready"


# ==========================================================
# Update Media
# ==========================================================

class MediaUpdate(BaseModel):

    provider: Optional[str] = None

    title: Optional[str] = None

    file_name: Optional[str] = None

    file_path: Optional[str] = None

    file_url: Optional[str] = None

    mime_type: Optional[str] = None

    extension: Optional[str] = None

    duration: Optional[int] = None

    width: Optional[int] = None

    height: Optional[int] = None

    file_size: Optional[int] = None

    status: Optional[str] = None


class MediaDownloadRequest(BaseModel):
    """One item downloads directly; multiple items are bundled as a ZIP."""

    media_ids: list[int] = Field(min_length=1, max_length=50)


# ==========================================================
# Media Response
# ==========================================================

class MediaResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    project_id: int

    media_type: str

    provider: Optional[str]

    title: Optional[str]

    file_name: str

    file_path: str

    file_url: Optional[str]

    mime_type: Optional[str]

    extension: Optional[str]

    duration: Optional[int]

    width: Optional[int]

    height: Optional[int]

    file_size: Optional[int]

    status: str

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Media List
# ==========================================================

class MediaListResponse(BaseModel):

    success: bool

    total: int

    media: list[MediaResponse]


# ==========================================================
# Generic Message
# ==========================================================

class MediaMessage(BaseModel):

    success: bool

    message: str

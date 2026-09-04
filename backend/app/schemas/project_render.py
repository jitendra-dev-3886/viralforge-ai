from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Generate Project Render
# ==========================================================

class ProjectRenderRequest(BaseModel):

    project_id: int
    content_id: Optional[int] = None


# ==========================================================
# Final Video Response
# ==========================================================

class ProjectRenderResponse(BaseModel):

    success: bool

    project_id: int

    media_id: int

    file_name: str

    file_path: str

    status: str


# ==========================================================
# Final Video Details
# ==========================================================

class ProjectRenderDetails(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    project_id: int

    media_type: str

    provider: str

    title: str

    file_name: str

    file_path: str

    file_url: str | None = None

    mime_type: str

    extension: str

    duration: int | None = None

    width: int | None = None

    height: int | None = None

    file_size: int | None = None

    status: str

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Get Final Video
# ==========================================================

class ProjectRenderGetResponse(BaseModel):

    success: bool

    video: ProjectRenderDetails


# ==========================================================
# Message Response
# ==========================================================

class ProjectRenderMessage(BaseModel):

    success: bool

    message: str

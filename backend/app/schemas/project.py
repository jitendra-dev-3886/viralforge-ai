from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Base Project Schema
# ==========================================================

class ProjectCreate(BaseModel):
    title: str
    topic: str
    platform: str
    content_type: str

    niche: Optional[str] = None
    category: Optional[str] = None
    language: str = "English"

    brand_id: Optional[int] = None

    ai_provider: Optional[str] = None
    prompt: Optional[str] = None


# ==========================================================
# Create Project
# ==========================================================

class CreateProjectRequest(ProjectCreate):
    pass


# ==========================================================
# Update Project
# ==========================================================

class UpdateProjectRequest(BaseModel):

    title: Optional[str] = None
    topic: Optional[str] = None

    platform: Optional[str] = None
    content_type: Optional[str] = None

    niche: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None

    brand_id: Optional[int] = None

    ai_provider: Optional[str] = None
    prompt: Optional[str] = None

    status: Optional[str] = None


# ==========================================================
# Project Response
# ==========================================================

class ProjectResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    brand_id: Optional[int]

    title: str
    topic: str

    niche: Optional[str]
    category: Optional[str]

    platform: str
    content_type: str

    language: str

    status: str

    ai_provider: Optional[str]
    prompt: Optional[str]

    created_at: datetime
    updated_at: datetime


# ==========================================================
# Create Response
# ==========================================================

class CreateProjectResponse(BaseModel):

    success: bool

    message: str

    project: ProjectResponse


# ==========================================================
# Single Project Response
# ==========================================================

class SingleProjectResponse(BaseModel):

    success: bool

    project: ProjectResponse


# ==========================================================
# Project List Response
# ==========================================================

class ProjectListResponse(BaseModel):

    success: bool

    total: int

    projects: list[ProjectResponse]


# ==========================================================
# Generic Message Response
# ==========================================================

class ProjectMessage(BaseModel):

    success: bool

    message: str
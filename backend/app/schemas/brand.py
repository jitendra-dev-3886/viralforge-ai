from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


# ==========================================================
# Create Brand Request
# ==========================================================

class CreateBrandRequest(BaseModel):

    name: str

    description: Optional[str] = None

    niche: Optional[str] = None

    website: Optional[HttpUrl] = None

    logo: Optional[str] = None

    primary_color: Optional[str] = "#2563EB"

    secondary_color: Optional[str] = "#1E293B"

    font: Optional[str] = "Inter"


# ==========================================================
# Update Brand Request
# ==========================================================

class UpdateBrandRequest(BaseModel):

    name: Optional[str] = None

    description: Optional[str] = None

    niche: Optional[str] = None

    website: Optional[HttpUrl] = None

    logo: Optional[str] = None

    primary_color: Optional[str] = None

    secondary_color: Optional[str] = None

    font: Optional[str] = None


# ==========================================================
# Brand Response
# ==========================================================

class BrandResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int

    name: str

    description: Optional[str]

    niche: Optional[str]

    website: Optional[str]

    logo: Optional[str]

    primary_color: Optional[str]

    secondary_color: Optional[str]

    font: Optional[str]

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Create Brand Response
# ==========================================================

class CreateBrandResponse(BaseModel):

    success: bool

    message: str

    brand: BrandResponse


# ==========================================================
# Brand List Response
# ==========================================================

class BrandListResponse(BaseModel):

    success: bool

    total: int

    brands: list[BrandResponse]


# ==========================================================
# Generic Message Response
# ==========================================================

class BrandMessage(BaseModel):

    success: bool

    message: str
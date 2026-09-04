from typing import Optional
from pydantic import BaseModel, Field


class NicheCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: str = Field("✨", max_length=20)
    color: str = Field("blue", max_length=30)
    is_active: bool = True


class NicheUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    is_active: Optional[bool] = None

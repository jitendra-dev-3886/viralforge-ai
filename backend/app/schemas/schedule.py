from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID

class ScheduleCreate(BaseModel):
    project_id: int
    content_id: int
    platform: str = Field(..., min_length=2, max_length=50)
    account_name: str | None = None
    scheduled_at: datetime
    timezone: str = "Asia/Kolkata"
    publishing_account_id: int | None = None
    media_ids: list[int] = Field(default_factory=list, max_length=10)
    privacy: Literal["public", "unlisted", "private"] = "private"
    made_for_kids: bool = False
    request_key: UUID | None = None

class ScheduleUpdate(BaseModel):
    platform: str | None = None
    account_name: str | None = None
    scheduled_at: datetime | None = None
    timezone: str | None = None
    status: str | None = None

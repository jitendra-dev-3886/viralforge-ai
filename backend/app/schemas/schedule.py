from datetime import datetime
from pydantic import BaseModel, Field

class ScheduleCreate(BaseModel):
    project_id: int
    content_id: int
    platform: str = Field(..., min_length=2, max_length=50)
    account_name: str | None = None
    scheduled_at: datetime
    timezone: str = "Asia/Kolkata"

class ScheduleUpdate(BaseModel):
    platform: str | None = None
    account_name: str | None = None
    scheduled_at: datetime | None = None
    timezone: str | None = None
    status: str | None = None

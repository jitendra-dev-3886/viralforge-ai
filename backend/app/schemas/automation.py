from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AutomationConfig(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    project_id: int = Field(gt=0)
    platform: Literal["instagram", "facebook", "youtube"] = "instagram"
    content_type: Literal["Reel", "Carousel", "Post", "Quote", "Story", "Shorts", "Video"] = "Carousel"
    # Accept older saved schedules; new runs select their topic from live trends.
    topic: str = Field(default="", max_length=500)
    niche: str = Field(min_length=2, max_length=100)
    language: str = Field(default="English", min_length=2, max_length=30)
    style: str = Field(default="Engaging", min_length=2, max_length=50)
    visual_style: Literal["minimal", "bold", "cinematic", "professional", "playful", "scrapbook"] = "minimal"
    scene_count: int = Field(default=5, ge=1, le=10)
    total_duration: int = Field(default=30, ge=5, le=180)
    voice: Literal["auto", "off", "en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "hi-IN-SwaraNeural", "hi-IN-MadhurNeural"] = "auto"
    voice_speed: Literal["-10%", "-5%", "+0%", "+5%", "+10%"] = "+0%"
    music_id: int | None = Field(default=None, gt=0)
    music_volume: float = Field(default=0.18, ge=0, le=1)
    days: list[int] = Field(default_factory=lambda: list(range(7)), min_length=1, max_length=7)
    time: str = Field(default="09:00", pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    timezone: str = Field(default="Asia/Kolkata", max_length=100)
    lead_minutes: int = Field(default=30, ge=5, le=1440)
    mode: Literal["approval", "automatic"] = "approval"
    publishing_account_id: int | None = Field(default=None, gt=0)
    privacy: Literal["public", "unlisted", "private"] = "private"
    made_for_kids: bool | None = None
    enabled: bool = True

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Choose a valid IANA timezone, such as Asia/Kolkata.")
        return value

    @field_validator("days")
    @classmethod
    def valid_days(cls, value):
        if any(day < 0 or day > 6 for day in value) or len(set(value)) != len(value):
            raise ValueError("Choose distinct weekdays from 0 (Monday) to 6 (Sunday).")
        return sorted(value)

    @model_validator(mode="after")
    def valid_output(self):
        allowed = {"Shorts", "Video"} if self.platform == "youtube" else {"Reel", "Carousel", "Post", "Quote", "Story"}
        if self.content_type not in allowed:
            raise ValueError("Choose a format supported by this platform.")
        if self.content_type == "Carousel" and self.scene_count < 3:
            raise ValueError("Carousels need 3–10 slides.")
        if self.mode == "automatic":
            if not self.publishing_account_id:
                raise ValueError("Choose a connected publishing account.")
            if self.content_type == "Story":
                raise ValueError("Stories support drafts for approval only.")
            if self.platform == "youtube" and self.made_for_kids is None:
                raise ValueError("Choose the YouTube audience setting.")
        return self


class AutomationState(BaseModel):
    enabled: bool

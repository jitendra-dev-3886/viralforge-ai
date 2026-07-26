from pydantic import BaseModel, Field


# ==========================================================
# Subtitle Request
# ==========================================================

class SubtitleRequest(BaseModel):

    scene_id: int = Field(
        ...,
        gt=0,
        description="Scene ID"
    )


# ==========================================================
# Subtitle Response
# ==========================================================

class SubtitleResponse(BaseModel):

    success: bool

    scene_id: int

    media_id: int

    provider: str

    file_name: str

    file_path: str

    status: str
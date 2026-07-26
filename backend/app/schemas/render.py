from pydantic import BaseModel, Field


# ==========================================================
# Render Request
# ==========================================================

class RenderRequest(BaseModel):

    scene_id: int = Field(
        ...,
        gt=0,
        description="Scene ID to render"
    )


# ==========================================================
# Render Response
# ==========================================================

class RenderResponse(BaseModel):

    success: bool

    scene_id: int

    media_id: int

    file_name: str

    file_path: str

    status: str
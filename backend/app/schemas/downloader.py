from pydantic import BaseModel


# ==========================================================
# Download Request
# ==========================================================

class DownloadRequest(BaseModel):

    scene_id: int


# ==========================================================
# Download Response
# ==========================================================

class DownloadResponse(BaseModel):

    success: bool

    scene_id: int

    media_id: int

    provider: str

    file_name: str

    file_path: str

    file_url: str

    media_type: str

    status: str
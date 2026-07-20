from pydantic import BaseModel
from typing import Optional


class DownloadImageRequest(BaseModel):
    project_id: int
    keyword: str


class MediaResponse(BaseModel):
    success: bool
    media_id: int
    file: str


class SearchImageRequest(BaseModel):
    query: str
    per_page: Optional[int] = 10
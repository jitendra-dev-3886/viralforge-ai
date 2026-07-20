from pydantic import BaseModel
from typing import List, Optional


class GenerateRequest(BaseModel):

    project_id: int

    platforms: List[str]

    content_types: List[str]

    niche: str

    topic: str

    package: str

    language: Optional[str] = "English"
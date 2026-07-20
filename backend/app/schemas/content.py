from pydantic import BaseModel, Field
from typing import List, Optional


class GeneratedContent(BaseModel):

    title: str

    category: str

    platform: str

    content_type: str

    score: int

    hook: Optional[str] = None

    caption: Optional[str] = None

    hashtags: List[str] = Field(
        default_factory=list
    )

    script: Optional[str] = None

    status: str = "draft"
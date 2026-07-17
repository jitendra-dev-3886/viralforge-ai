from pydantic import BaseModel


# class GenerateContentRequest(BaseModel):
#     niche: str
#     topic: str
#     package: str

from pydantic import BaseModel
from typing import List

class GenerateRequest(BaseModel):

    platforms: List[str]

    content_types: List[str]

    niche: str

    topic: str

    package: str
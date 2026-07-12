from pydantic import BaseModel


class GenerateContentRequest(BaseModel):
    niche: str
    topic: str
    package: str
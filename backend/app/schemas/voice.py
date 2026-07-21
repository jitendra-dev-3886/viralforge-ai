from pydantic import BaseModel, Field
from typing import Optional


# ==========================================================
# Voice Generation Request
# ==========================================================

class VoiceGenerateRequest(BaseModel):

    scene_id: int = Field(
        ...,
        gt=0,
        description="Scene ID"
    )

    voice: Optional[str] = Field(
        default="en-US-AriaNeural",
        description="Edge-TTS Voice"
    )

    provider: Optional[str] = Field(
        default="edge-tts",
        description="Voice Provider"
    )


# ==========================================================
# Voice Response
# ==========================================================

class VoiceGenerateResponse(BaseModel):

    success: bool

    scene_id: int

    media_id: int

    provider: str

    voice: str

    file_name: str

    file_path: str

    status: str
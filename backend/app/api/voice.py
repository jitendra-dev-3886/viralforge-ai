from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.voice import (
    VoiceGenerateRequest,
)

from app.services.voice_service import (
    VoiceService,
)

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
)


# ==========================================================
# Generate Voice
# ==========================================================

@router.post("/generate")
def generate_voice(
    request: VoiceGenerateRequest,
    db: Session = Depends(get_db),
):

    return VoiceService.generate(

        db=db,

        scene_id=request.scene_id,

        voice=request.voice,

    )


# ==========================================================
# Generate Voice By Scene Id
# ==========================================================

@router.get("/generate/{scene_id}")
def generate_voice_by_scene(
    scene_id: int,
    db: Session = Depends(get_db),
):

    return VoiceService.generate(

        db=db,

        scene_id=scene_id,

    )
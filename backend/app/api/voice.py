from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

from app.schemas.voice import (
    VoiceCreate,
    VoiceUpdate,
)

from app.services.voice_service import VoiceService


router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
)


# ==========================================================
# Generate Voice
# ==========================================================

@router.post("/generate")
async def generate_voice(
    request: VoiceCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await VoiceService.generate(
        db=db,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Get Voice By ID
# ==========================================================

@router.get("/{voice_id}")
def get_voice(
    voice_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    voice = VoiceService.get_by_id(
        db=db,
        voice_id=voice_id,
        user_id=user_id,
    )

    if not voice:
        return {
            "success": False,
            "message": "Voice not found.",
        }

    return {
        "success": True,
        "voice": voice,
    }


# ==========================================================
# Get All Voices
# ==========================================================

@router.get("/")
def get_all_voices(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    voices = VoiceService.get_all(
        db=db,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(voices),
        "voices": voices,
    }


# ==========================================================
# Get Project Voices
# ==========================================================

@router.get("/project/{project_id}")
def get_project_voices(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    voices = VoiceService.get_project(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(voices),
        "voices": voices,
    }


# ==========================================================
# Get Scene Voice
# ==========================================================

@router.get("/scene/{scene_id}")
def get_scene_voice(
    scene_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return VoiceService.get_scene(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )


# ==========================================================
# Update Voice
# ==========================================================

@router.put("/{voice_id}")
def update_voice(
    voice_id: int,
    request: VoiceUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return VoiceService.update(
        db=db,
        voice_id=voice_id,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Delete Voice
# ==========================================================

@router.delete("/{voice_id}")
def delete_voice(
    voice_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return VoiceService.delete(
        db=db,
        voice_id=voice_id,
        user_id=user_id,
    )


# ==========================================================
# Regenerate Voice
# ==========================================================

@router.post("/{voice_id}/regenerate")
async def regenerate_voice(
    voice_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await VoiceService.regenerate(
        db=db,
        voice_id=voice_id,
        user_id=user_id,
    )

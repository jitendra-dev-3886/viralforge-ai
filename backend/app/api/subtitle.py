from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.subtitle import (
    SubtitleRequest,
)

from app.services.subtitle_service import (
    SubtitleService,
)

router = APIRouter(
    prefix="/api/subtitle",
    tags=["Subtitle"],
)


# ==========================================================
# Generate Subtitle
# ==========================================================

@router.post("/generate")
def generate_subtitle(
    request: SubtitleRequest,
    db: Session = Depends(get_db),
):

    return SubtitleService.generate(

        db=db,

        scene_id=request.scene_id,

    )


# ==========================================================
# Generate Subtitle by Scene ID
# ==========================================================

@router.get("/generate/{scene_id}")
def generate_subtitle_by_scene(
    scene_id: int,
    db: Session = Depends(get_db),
):

    return SubtitleService.generate(

        db=db,

        scene_id=scene_id,

    )
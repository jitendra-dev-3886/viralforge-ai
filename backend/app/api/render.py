from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.render import (
    RenderRequest,
)

from app.services.render_service import (
    RenderService,
)

router = APIRouter(
    prefix="/api/render",
    tags=["Render"],
)


# ==========================================================
# Render Scene
# ==========================================================

@router.post("/generate")
def generate_render(
    request: RenderRequest,
    db: Session = Depends(get_db),
):

    return RenderService.generate(

        db=db,

        scene_id=request.scene_id,

    )


# ==========================================================
# Render Scene By ID
# ==========================================================

@router.get("/generate/{scene_id}")
def generate_render_by_scene(
    scene_id: int,
    db: Session = Depends(get_db),
):

    return RenderService.generate(

        db=db,

        scene_id=scene_id,

    )
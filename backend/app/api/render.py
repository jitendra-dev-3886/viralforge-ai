from fastapi import APIRouter, Header, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.core.security import get_current_user_id
from app.core.render_errors import run_render

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


class ImageBatchRequest(BaseModel):
    scene_ids: list[int] = Field(min_length=1, max_length=20)


def render_image_batch(db, user_id, scene_ids, as_image=True):
    results = [RenderService.generate(db=db, user_id=user_id, scene_id=scene_id, as_image=True) for scene_id in scene_ids]
    return {"success": True, "media_ids": [item["media_id"] for item in results]}


@router.post("/images")
def generate_images(request: ImageBatchRequest, idempotency_key: str | None = Header(default=None, max_length=128), db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return run_render(render_image_batch, db=db, user_id=user_id, scene_ids=request.scene_ids, as_image=True, request_key=idempotency_key)


# ==========================================================
# Render Scene
# ==========================================================

@router.post("/generate")
def generate_render(
    request: RenderRequest,
    idempotency_key: str | None = Header(default=None, max_length=128),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return run_render(RenderService.generate,
        request_key=idempotency_key,

        db=db,

        scene_id=request.scene_id,
        user_id=user_id,

    )


# ==========================================================
# Render Scene By ID
# ==========================================================

@router.post("/image")
def generate_image_render(
    request: RenderRequest,
    idempotency_key: str | None = Header(default=None, max_length=128),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return run_render(RenderService.generate, request_key=idempotency_key, db=db, scene_id=request.scene_id, user_id=user_id, as_image=True)


@router.get("/generate/{scene_id}")
def generate_render_by_scene(
    scene_id: int,
    idempotency_key: str | None = Header(default=None, max_length=128),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return run_render(RenderService.generate,
        request_key=idempotency_key,

        db=db,

        scene_id=scene_id,
        user_id=user_id,

    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.scene import (
    SceneCreate,
    SceneUpdate,
)

from app.services.scene_service import SceneService


router = APIRouter(
    prefix="/api/scenes",
    tags=["Scenes"],
)


# ==========================================================
# Create Scene
# ==========================================================

@router.post("/")
def create_scene(
    request: SceneCreate,
    db: Session = Depends(get_db),
):

    return SceneService.create(
        db=db,
        request=request,
    )


# ==========================================================
# Get All Scenes
# ==========================================================

@router.get("/")
def get_all_scenes(
    user_id: int,
    db: Session = Depends(get_db),
):

    return SceneService.get_all(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# Get Single Scene
# ==========================================================

@router.get("/{scene_id}")
def get_scene(
    scene_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):

    return SceneService.get_by_id(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )


# ==========================================================
# Get Project Scenes
# ==========================================================

@router.get("/project/{project_id}")
def get_project_scenes(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):

    return SceneService.get_project_scenes(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )


# ==========================================================
# Update Scene
# ==========================================================

@router.put("/{scene_id}")
def update_scene(
    scene_id: int,
    user_id: int,
    request: SceneUpdate,
    db: Session = Depends(get_db),
):

    return SceneService.update(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Delete Scene
# ==========================================================

@router.delete("/{scene_id}")
def delete_scene(
    scene_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):

    return SceneService.delete(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

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
    user_id: int = Depends(get_current_user_id),
):
    return SceneService.create(
        db=db,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Generate AI Scenes
# ==========================================================

@router.post("/generate")
def generate_scenes(
    project_id: int,
    content_id: int,
    ai_data: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    scenes = SceneService.generate(
        db=db,
        project_id=project_id,
        content_id=content_id,
        user_id=user_id,
        ai_data=ai_data,
    )

    db.commit()

    return {
        "success": True,
        "message": "Scenes generated successfully.",
        "total": len(scenes),
        "scenes": scenes,
    }


# ==========================================================
# Get All Scenes
# ==========================================================

@router.get("/")
def get_all_scenes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    scenes = SceneService.get_all(
        db=db,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(scenes),
        "scenes": scenes,
    }


# ==========================================================
# Get Scene By ID
# ==========================================================

@router.get("/{scene_id}")
def get_scene(
    scene_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    scene = SceneService.get_by_id(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )

    if not scene:
        return {
            "success": False,
            "message": "Scene not found.",
        }

    return {
        "success": True,
        "scene": scene,
    }


# ==========================================================
# Get Project Scenes
# ==========================================================

@router.get("/project/{project_id}")
def get_project_scenes(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    scenes = SceneService.get_project_scenes(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(scenes),
        "scenes": scenes,
    }


# ==========================================================
# Get Content Scenes
# ==========================================================

@router.get("/content/{content_id}")
def get_content_scenes(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    scenes = SceneService.get_content_scenes(
        db=db,
        content_id=content_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(scenes),
        "scenes": scenes,
    }


# ==========================================================
# Update Scene
# ==========================================================

@router.put("/{scene_id}")
def update_scene(
    scene_id: int,
    request: SceneUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return SceneService.delete(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )

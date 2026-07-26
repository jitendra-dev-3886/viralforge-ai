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
    tags=["Scene"],
)


# ==========================================================
# Create Scene
# ==========================================================

@router.post("/")
def create_scene(
    request: SceneCreate,
    db: Session = Depends(get_db),
    user_id: int = 1,  # <-- Added default value to prevent 422
):

    # NOTE: If your frontend is actually sending user_id inside the JSON body,
    # you can remove `user_id: int = 1` above and change the line below to:
    # user_id=request.user_id 
    
    return SceneService.create(
        db=db,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Get All Scenes
# ==========================================================

@router.get("/")
def get_all_scenes(
    db: Session = Depends(get_db),
    user_id: int = 1,  # <-- Added default
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
    user_id: int = 1,  # <-- Added default
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
    db: Session = Depends(get_db),
    user_id: int = 1,  # <-- Added default
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
    user_id: int = 1,  # <-- Added default
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
    user_id: int = 1,  # <-- Added default
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
    user_id: int = 1,  # <-- Added default
):

    return SceneService.delete(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )
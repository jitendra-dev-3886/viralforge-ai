from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pathlib import Path
from uuid import uuid4
from app.models.media import Media
from app.core.ffmpeg_client import FFmpegClient
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

from app.schemas.scene import (
    SceneCreate,
    SceneUpdate,
    SceneReorder,
)

from app.services.scene_service import SceneService
from app.models.scene import Scene


router = APIRouter(
    prefix="/api/scenes",
    tags=["Scenes"],
)


@router.post("/{scene_id:int}/media")
async def upload_scene_media(
    scene_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    scene = db.query(Scene).filter_by(id=scene_id, user_id=user_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found.")
    extension = Path(file.filename or "").suffix.lower()
    types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
             ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}
    if extension not in types:
        raise HTTPException(status_code=400, detail="Upload a JPG, PNG, WebP, MP4, MOV, or WebM file.")
    media_type = types[extension].split("/")[0]
    limit = (20 if media_type == "image" else 100) * 1024 * 1024
    folder = Path("storage/projects") / str(scene.project_id) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"scene_{scene.id}_{uuid4().hex}{extension}"
    path = folder / filename
    try:
        size = 0
        with path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > limit:
                    raise HTTPException(status_code=413, detail=f"File must be {limit // (1024 * 1024)} MB or smaller.")
                destination.write(chunk)
        if not size or not await run_in_threadpool(FFmpegClient.is_media_readable, str(path)):
            raise HTTPException(status_code=422, detail="This file has no readable image or video. Choose another file.")
        media = Media(user_id=user_id, project_id=scene.project_id, media_type=media_type,
                      provider="upload", title=Path(file.filename).name[:255], file_name=filename,
                      file_path=str(path), file_url=f"/storage/projects/{scene.project_id}/uploads/{filename}",
                      mime_type=types[extension], extension=extension, file_size=size, status="ready")
        db.add(media)
        db.flush()
        scene.media_id = media.id
        scene.media_type = media_type
        scene.status = "media_ready"
        result = {"success": True, "media_id": media.id, "media_url": media.file_url,
                  "media_type": media_type, "media_provider": "upload", "status": scene.status}
        db.commit()
        return result
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

@router.put("/content/{content_id}/reorder")
def reorder_scenes(content_id: int, request: SceneReorder, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    scenes = db.query(Scene).filter_by(content_id=content_id, user_id=user_id).all()
    if {scene.id for scene in scenes} != set(request.scene_ids):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Scene order must contain every scene exactly once.")
    by_id = {scene.id: scene for scene in scenes}
    for number, scene_id in enumerate(request.scene_ids, 1): by_id[scene_id].scene_number = number
    db.commit()
    return {"success": True}


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

@router.get("/{scene_id:int}")
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

@router.put("/{scene_id:int}")
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

@router.delete("/{scene_id:int}")
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

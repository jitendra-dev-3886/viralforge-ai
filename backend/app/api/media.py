from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.media import (
    MediaCreate,
    MediaUpdate,
)
from app.services.media_service import MediaService

router = APIRouter(
    prefix="/api/media",
    tags=["Media"],
)


# ==========================================================
# Create Media
# ==========================================================

@router.post("/")
def create_media(
    request: MediaCreate,
    db: Session = Depends(get_db),
):
    return MediaService.create(
        db=db,
        request=request,
    )


# ==========================================================
# Get All Media By User
# ==========================================================

@router.get("/")
def get_all_media(
    user_id: int,
    db: Session = Depends(get_db),
):
    return MediaService.get_all(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# Get Single Media
# ==========================================================

@router.get("/{media_id}")
def get_media(
    media_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    return MediaService.get_by_id(
        db=db,
        media_id=media_id,
        user_id=user_id,
    )


# ==========================================================
# Get All Media Of Project
# ==========================================================

@router.get("/project/{project_id}")
def get_project_media(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    return MediaService.get_project_media(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )


# ==========================================================
# Update Media
# ==========================================================

@router.put("/{media_id}")
def update_media(
    media_id: int,
    user_id: int,
    request: MediaUpdate,
    db: Session = Depends(get_db),
):
    return MediaService.update(
        db=db,
        media_id=media_id,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Delete Media
# ==========================================================

@router.delete("/{media_id}")
def delete_media(
    media_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    return MediaService.delete(
        db=db,
        media_id=media_id,
        user_id=user_id,
    )
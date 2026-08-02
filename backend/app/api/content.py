from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
)

from app.services.content_service import ContentService

router = APIRouter(
    prefix="/api/content",
    tags=["Content"],
)


# ==========================================================
# Create Content
# ==========================================================

@router.post("/")
def create_content(
    request: ContentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return ContentService.create(
        db=db,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Get All Contents
# ==========================================================

@router.get("/")
def get_all_contents(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return ContentService.get_all(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# Get Single Content
# ==========================================================

@router.get("/{content_id}")
def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return ContentService.get_by_id(
        db=db,
        content_id=content_id,
        user_id=user_id,
    )


# ==========================================================
# Get Contents By Project
# ==========================================================

@router.get("/project/{project_id}")
def get_project_contents(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return ContentService.get_project_contents(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )


# ==========================================================
# Update Content
# ==========================================================

@router.put("/{content_id}")
def update_content(
    content_id: int,
    request: ContentUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return ContentService.update(
        db=db,
        content_id=content_id,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Delete Content
# ==========================================================

@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return ContentService.delete(
        db=db,
        content_id=content_id,
        user_id=user_id,
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.content_service import ContentService
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
)

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
):
    return ContentService.create(
        db=db,
        request=request,
    )


# ==========================================================
# Get All Contents
# ==========================================================

@router.get("/")
def get_all_contents(
    user_id: int,
    db: Session = Depends(get_db),
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
    user_id: int,
    db: Session = Depends(get_db),
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
    user_id: int,
    db: Session = Depends(get_db),
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
    user_id: int,
    db: Session = Depends(get_db),
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
    user_id: int,
    db: Session = Depends(get_db),
):
    return ContentService.delete(
        db=db,
        content_id=content_id,
        user_id=user_id,
    )
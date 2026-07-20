from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.project import (
    CreateProjectRequest,
    UpdateProjectRequest,
)

from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
)

# =====================================================
# Create Project
# =====================================================

@router.post("/")
def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
):
    """
    Create New Project
    """

    user_id = 1      # TODO: Replace with JWT user id

    return ProjectService.create(
        db=db,
        user_id=user_id,
        request=request,
    )


# =====================================================
# Get All Projects
# =====================================================




@router.get("/")
def get_projects(
    db: Session = Depends(get_db),
):

    user_id = 1      # TODO: JWT

    return ProjectService.get_projects(
        db=db,
        user_id=user_id,
    )


# =====================================================
# Get Single Project
# =====================================================

@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1      # TODO: JWT

    project = ProjectService.get_project(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


# =====================================================
# Update Project
# =====================================================

@router.put("/{project_id}")
def update_project(
    project_id: int,
    request: UpdateProjectRequest,
    db: Session = Depends(get_db),
):

    user_id = 1

    project = ProjectService.update_project(
        db=db,
        project_id=project_id,
        user_id=user_id,
        request=request,
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


# =====================================================
# Delete Project
# =====================================================

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    deleted = ProjectService.delete_project(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return {
        "success": True,
        "message": "Project deleted successfully.",
    }
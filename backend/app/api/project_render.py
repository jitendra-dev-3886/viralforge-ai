from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.project_render import (
    ProjectRenderRequest,
)

from app.services.project_render_service import (
    ProjectRenderService,
)

router = APIRouter(
    prefix="/api/project-render",
    tags=["Project Render"],
)


# ==========================================================
# Generate Final Project Video
# ==========================================================

@router.post("/generate")
def generate_project_render(
    request: ProjectRenderRequest,
    db: Session = Depends(get_db),
):

    return ProjectRenderService.generate(

        db=db,

        project_id=request.project_id,

    )


# ==========================================================
# Generate By Project ID
# ==========================================================

@router.get("/generate/{project_id}")
def generate_project_render_by_id(
    project_id: int,
    db: Session = Depends(get_db),
):

    return ProjectRenderService.generate(

        db=db,

        project_id=project_id,

    )


# ==========================================================
# Get Final Video
# ==========================================================

@router.get("/{project_id}")
def get_final_video(
    project_id: int,
    db: Session = Depends(get_db),
):

    return ProjectRenderService.get_final_video(

        db=db,

        project_id=project_id,

    )
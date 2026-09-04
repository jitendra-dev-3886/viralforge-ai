from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pathlib import Path
import uuid
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

from app.schemas.project_render import (
    ProjectRenderRequest,
)

from app.services.project_render_service import (
    ProjectRenderService,
)
from app.models.project import Project
from app.models.media import Media

router = APIRouter(
    prefix="/api/project-render",
    tags=["Project Render"],
)

@router.post("/music/{project_id}")
async def upload_background_music(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".mp3", ".wav", ".m4a", ".aac", ".ogg"}:
        raise HTTPException(status_code=400, detail="Upload an MP3, WAV, M4A, AAC, or OGG audio file.")
    folder = Path("storage/projects") / str(project_id) / "music"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"music_{uuid.uuid4().hex[:10]}{extension}"
    path = folder / filename
    size = 0
    with path.open("wb") as destination:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > 25 * 1024 * 1024:
                destination.close()
                path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Music file must be 25 MB or smaller.")
            destination.write(chunk)
    media = Media(
        user_id=user_id, project_id=project_id, media_type="music", provider="upload",
        title="Background Music", file_name=filename, file_path=str(path),
        file_url=f"/storage/projects/{project_id}/music/{filename}",
        mime_type=file.content_type or "audio/mpeg", extension=extension,
        file_size=size, status="ready",
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"success": True, "music": media}


# ==========================================================
# Generate Final Project Video
# ==========================================================

@router.post("/generate")
def generate_project_render(
    request: ProjectRenderRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return ProjectRenderService.generate(

        db=db,

        project_id=request.project_id,
        content_id=request.content_id,
        user_id=user_id,

    )


# ==========================================================
# Generate By Project ID
# ==========================================================

@router.get("/generate/{project_id}")
def generate_project_render_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return ProjectRenderService.generate(

        db=db,

        project_id=project_id,
        user_id=user_id,

    )


# ==========================================================
# Get Final Video
# ==========================================================

@router.get("/{project_id}")
def get_final_video(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return ProjectRenderService.get_final_video(

        db=db,

        project_id=project_id,
        user_id=user_id,

    )

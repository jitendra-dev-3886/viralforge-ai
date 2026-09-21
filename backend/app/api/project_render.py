from fastapi import APIRouter, Header, Depends, File, Form, HTTPException, UploadFile
from pathlib import Path
import uuid
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id
from app.core.render_errors import run_render
from app.core.ffmpeg_client import FFmpegClient

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
    workspace: bool = Form(False),
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
    try:
        FFmpegClient.audio_duration(str(path))
    except ValueError:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="This file has no readable audio. Upload a valid music track.")
    media = Media(
        user_id=user_id, project_id=project_id, media_type="music", provider="workspace_upload" if workspace else "upload",
        title=Path(file.filename or "Background Music").name[:255], file_name=filename, file_path=str(path),
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
    idempotency_key: str | None = Header(default=None, max_length=128),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return run_render(ProjectRenderService.generate,
        request_key=idempotency_key,

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
    idempotency_key: str | None = Header(default=None, max_length=128),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return run_render(ProjectRenderService.generate,
        request_key=idempotency_key,

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

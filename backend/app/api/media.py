import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.media import Media
from app.schemas.media import (
    MediaCreate,
    MediaDownloadRequest,
    MediaUpdate,
)
from app.services.media_service import MediaService

router = APIRouter(
    prefix="/api/media",
    tags=["Media"],
)


def _safe_media_path(file_path: str) -> Path | None:
    """Accept only local files within the app's storage directory."""
    candidate = Path(file_path).resolve()
    backend_root = Path(__file__).resolve().parents[2]
    allowed_roots = {
        (backend_root / "storage").resolve(),
        (Path.cwd() / "storage").resolve(),
    }

    if any(candidate.is_relative_to(root) for root in allowed_roots):
        return candidate
    return None


# ==========================================================
# Create Media
# ==========================================================

@router.post("/")
def create_media(
    request: MediaCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    request.user_id = user_id
    return MediaService.create(
        db=db,
        request=request,
    )


# ==========================================================
# Get All Media By User
# ==========================================================

@router.get("/")
def get_all_media(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
    request: MediaUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return MediaService.delete(
        db=db,
        media_id=media_id,
        user_id=user_id,
    )


# ==========================================================
# Download One or More Saved Media Files
# ==========================================================

@router.post("/download")
def download_media(
    request: MediaDownloadRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    media_items = (
        db.query(Media)
        .filter(
            Media.user_id == user_id,
            Media.id.in_(request.media_ids),
        )
        .all()
    )

    files = []
    for media in media_items:
        path = _safe_media_path(media.file_path)
        if path and path.is_file():
            files.append((media, path))

    if not files:
        raise HTTPException(
            status_code=404,
            detail="The selected media files are not available for download.",
        )

    if len(files) == 1:
        media, path = files[0]
        return FileResponse(
            path=path,
            media_type=media.mime_type or "application/octet-stream",
            filename=Path(media.file_name).name,
        )

    archive_dir = Path(tempfile.mkdtemp(prefix="viralforge-media-"))
    archive_path = archive_dir / "viralforge-selected-media.zip"

    try:
        used_names = set()
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for media, path in files:
                filename = Path(media.file_name).name or f"media-{media.id}{path.suffix}"
                if filename in used_names:
                    filename = f"{media.id}-{filename}"
                used_names.add(filename)
                archive.write(path, arcname=filename)
    except Exception as exc:
        shutil.rmtree(archive_dir, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create media download: {exc}",
        ) from exc

    return FileResponse(
        path=archive_path,
        media_type="application/zip",
        filename="viralforge-selected-media.zip",
        background=BackgroundTask(shutil.rmtree, archive_dir, ignore_errors=True),
    )

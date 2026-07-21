from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.downloader import (
    DownloadRequest,
)

from app.services.downloader_service import (
    DownloaderService,
)

router = APIRouter(
    prefix="/api/downloader",
    tags=["Downloader"],
)


# ==========================================================
# Download Media For Scene
# ==========================================================

@router.post("/download")
def download_media(
    request: DownloadRequest,
    db: Session = Depends(get_db),
):

    return DownloaderService.download(
        db=db,
        scene_id=request.scene_id,
    )


# ==========================================================
# Download By Scene ID
# ==========================================================

@router.get("/download/{scene_id}")
def download_by_scene(
    scene_id: int,
    db: Session = Depends(get_db),
):

    return DownloaderService.download(
        db=db,
        scene_id=scene_id,
    )
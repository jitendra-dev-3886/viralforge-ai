from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id
from app.services.downloader_service import DownloaderService

router = APIRouter(
    prefix="/api/downloader",
    tags=["Downloader"],
)


# ==========================================================
# Download Scene Media
# ==========================================================

@router.post("/{scene_id}")
def download_scene_media(
    scene_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    return DownloaderService.download(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )

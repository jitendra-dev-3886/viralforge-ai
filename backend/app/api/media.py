from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.media import DownloadImageRequest

from app.services.image_service import ImageService

router = APIRouter(
    prefix="/api/media",
    tags=["Media"],
)


@router.post("/download-image")
def download_image(
    request: DownloadImageRequest,
    db: Session = Depends(get_db),
):

    user_id = 1      # TODO: JWT

    media = ImageService.download_image(
        db=db,
        project_id=request.project_id,
        keyword=request.keyword,
        user_id=user_id,
    )

    return {
        "success": True,
        "media_id": media.id,
        "file": media.file_path,
    }
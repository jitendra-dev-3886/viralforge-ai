import os
import uuid

from sqlalchemy.orm import Session

from app.core.pexels_client import PexelsClient

from app.models.project import Project
from app.models.media import Media


class ImageService:

    @staticmethod
    def download_image(
        db: Session,
        project_id: int,
        keyword: str,
        user_id: int,
    ):

        # ===========================
        # Find Project
        # ===========================

        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

        if not project:
            raise Exception("Project not found")

        # ===========================
        # Search Image
        # ===========================

        result = PexelsClient.search_images(
            query=keyword,
            per_page=1,
        )

        photos = result.get("photos", [])

        if not photos:
            raise Exception(f"No image found for '{keyword}'")

        photo = photos[0]

        image_url = photo["src"]["large2x"]

        width = photo["width"]

        height = photo["height"]

        title = photo.get("alt") or keyword

        # ===========================
        # Project Images Folder
        # ===========================

        image_folder = os.path.join(
            project.path,
            "images"
        )

        os.makedirs(
            image_folder,
            exist_ok=True,
        )

        # ===========================
        # File Name
        # ===========================

        filename = f"{uuid.uuid4().hex}.jpg"

        file_path = os.path.join(
            image_folder,
            filename,
        )

        # ===========================
        # Download
        # ===========================

        PexelsClient.download_file(
            image_url,
            file_path,
        )

        file_size = os.path.getsize(file_path)

        # ===========================
        # Save Media
        # ===========================

        media = Media(

            user_id=user_id,

            project_id=project.id,

            media_type="image",

            provider="pexels",

            title=title,

            file_name=filename,

            file_path=file_path,

            file_url=image_url,

            mime_type="image/jpeg",

            extension=".jpg",

            width=width,

            height=height,

            file_size=file_size,

            status="ready",

        )

        db.add(media)

        db.commit()

        db.refresh(media)

        return media
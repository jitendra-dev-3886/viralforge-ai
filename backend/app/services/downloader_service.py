import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media

from app.core.pexels_client import PexelsClient


class DownloaderService:

    @staticmethod
    def download(
        db: Session,
        scene_id: int,
    ):

        # ======================================================
        # Get Scene
        # ======================================================

        scene = (
            db.query(Scene)
            .filter(Scene.id == scene_id)
            .first()
        )

        if not scene:

            raise HTTPException(
                status_code=404,
                detail="Scene not found.",
            )

        if not scene.keyword:

            raise HTTPException(
                status_code=400,
                detail="Scene keyword is missing.",
            )

        # ======================================================
        # Storage Folder
        # ======================================================

        folder = os.path.join(
            "storage",
            "projects",
            str(scene.project_id),
        )

        if scene.media_type == "image":

            folder = os.path.join(folder, "images")

        else:

            folder = os.path.join(folder, "videos")

        os.makedirs(folder, exist_ok=True)

        # ======================================================
        # File Name
        # ======================================================

        extension = ".jpg" if scene.media_type == "image" else ".mp4"

        filename = f"scene_{scene.scene_number}{extension}"

        filepath = os.path.join(
            folder,
            filename,
        )

        # ======================================================
        # Download From Pexels
        # ======================================================

        media = PexelsClient.search_and_download(

            keyword=scene.keyword,

            media_type=scene.media_type,

            save_path=filepath,

        )

        if not media:

            raise HTTPException(
                status_code=404,
                detail="No media found from Pexels.",
            )

        # ======================================================
        # Save Media
        # ======================================================

        media_record = Media(

            user_id=scene.user_id,

            project_id=scene.project_id,

            media_type=scene.media_type,

            provider=media["provider"],

            title=media["title"],

            file_name=filename,

            file_path=media["file_path"],

            file_url=media["file_url"],

            mime_type=media["mime_type"],

            extension=media["extension"],

            duration=media["duration"],

            width=media["width"],

            height=media["height"],

            file_size=media["file_size"],

            status="ready",

        )

        db.add(media_record)

        db.flush()

        # ======================================================
        # Update Scene
        # ======================================================

        scene.media_id = media_record.id

        scene.status = "downloaded"

        db.commit()

        db.refresh(media_record)

        db.refresh(scene)

        # ======================================================
        # Response
        # ======================================================

        return {

            "success": True,

            "scene_id": scene.id,

            "media_id": media_record.id,

            "provider": media_record.provider,

            "title": media_record.title,

            "file_name": media_record.file_name,

            "file_path": media_record.file_path,

            "file_url": media_record.file_url,

            "status": media_record.status,

        }
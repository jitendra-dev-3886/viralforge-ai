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
        # Search Media
        # ======================================================

        media = PexelsClient.first_image(
            scene.keyword
        )

        if scene.media_type == "video":

            media = PexelsClient.first_video(
                scene.keyword
            )

        if not media:

            raise HTTPException(
                status_code=404,
                detail="No media found from Pexels.",
            )

        # ======================================================
        # Storage
        # ======================================================

        folder = os.path.join(
            "storage",
            "projects",
            str(scene.project_id),
        )

        if scene.media_type == "image":

            folder = os.path.join(
                folder,
                "images",
            )

        else:

            folder = os.path.join(
                folder,
                "videos",
            )

        filename = (
            f"scene_{scene.scene_number}"
            f"{media['extension']}"
        )

        filepath = os.path.join(
            folder,
            filename,
        )

        # ======================================================
        # Download
        # ======================================================

        file = PexelsClient.download_file(
            media["url"],
            filepath,
        )

        # ======================================================
        # Save Media
        # ======================================================

        media_record = Media(

            user_id=scene.user_id,

            project_id=scene.project_id,

            media_type=scene.media_type,

            provider="Pexels",

            title=media["title"],

            file_name=filename,

            file_path=file["path"],

            file_url=media["url"],

            mime_type=media["mime_type"],

            extension=media["extension"],

            width=media.get("width"),

            height=media.get("height"),

            duration=scene.duration,

            file_size=file["size"],

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

            "file_name": media_record.file_name,

            "file_path": media_record.file_path,

            "file_url": media_record.file_url,

            "status": scene.status,

        }
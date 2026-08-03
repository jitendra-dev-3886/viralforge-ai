import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media

from app.core.pexels_client import PexelsClient
from app.core.pixabay_client import PixabayClient


class DownloaderService:

    @staticmethod
    def _media_orientation(scene: Scene) -> str:
        """Choose source media that needs the least crop for the final post."""
        content = scene.content
        platform = (getattr(content, "platform", "") or "").lower()
        content_type = (getattr(content, "content_type", "") or "").lower()

        if any(value in content_type for value in ("reel", "short", "story")):
            return "portrait"
        if "long video" in content_type or content_type == "video":
            return "landscape"
        if "carousel" in content_type:
            return "portrait"
        if "youtube" in platform and "community" not in content_type:
            return "landscape"
        if "instagram" in platform or "facebook" in platform:
            return "portrait"
        return "square"

    # ==========================================================
    # Download Scene Media
    # ==========================================================

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

            .filter(
                Scene.id == scene_id,
            )

            .first()

        )

        if not scene:

            raise HTTPException(

                status_code=404,

                detail="Scene not found.",

            )

        # ======================================================
        # Resolve Search Keyword
        # ======================================================

        scene_media_type = (scene.media_type or "").lower()

        if scene_media_type == "image":
            search_keyword = (
                scene.image_prompt
                or scene.keyword
                or scene.video_prompt
            )
        elif scene_media_type == "video":
            search_keyword = (
                scene.video_prompt
                or scene.keyword
                or scene.image_prompt
            )
        else:
            search_keyword = (
                scene.image_prompt
                or scene.keyword
                or scene.video_prompt
            )

        if isinstance(search_keyword, (list, tuple)):
            search_keyword = " ".join(str(item) for item in search_keyword)

        search_keyword = str(search_keyword or "").strip()

        if not search_keyword:

            raise HTTPException(

                status_code=400,

                detail="Scene keyword or prompt is missing.",

            )

        # ======================================================
        # Already Downloaded?
        # ======================================================

        if scene.media_id:

            media = (

                db.query(Media)

                .filter(
                    Media.id == scene.media_id,
                )

                .first()

            )

            if media:

                return {

                    "success": True,

                    "scene_id": scene.id,

                    "media_id": media.id,

                    "provider": media.provider,

                    "title": media.title,

                    "file_name": media.file_name,

                    "file_path": media.file_path,

                    "file_url": media.file_url,

                    "status": media.status,

                }

        # ======================================================
        # Storage Folder
        # ======================================================

        folder = os.path.join(

            "storage",

            "projects",

            str(scene.project_id),

        )

        media_type = (scene.media_type or "").lower()

        if media_type == "image":

            folder = os.path.join(
                folder,
                "images",
            )

        else:

            folder = os.path.join(
                folder,
                "videos",
            )

        os.makedirs(

            folder,

            exist_ok=True,

        )

        # ======================================================
        # File Name
        # ======================================================

        extension = (
            ".jpg"
            if media_type == "image"
            else ".mp4"
        )

        # Scene numbers restart for each content item. Include the content id so
        # generating several selected formats cannot overwrite previous media.
        filename = f"content_{scene.content_id}_scene_{scene.scene_number}{extension}"

        filepath = os.path.join(

            folder,

            filename,

        )

                # ======================================================
        # Download From Pexels or Pixabay
        # ======================================================

        media = None
        orientation = DownloaderService._media_orientation(scene)

        try:
            media = PexelsClient.search_and_download(
                keyword=search_keyword,
                media_type=media_type,
                save_path=filepath,
                orientation=orientation,
            )
        except Exception:
            media = None

        if not media:
            try:
                media = PixabayClient.search_and_download(
                    keyword=search_keyword,
                    media_type=media_type,
                    save_path=filepath,
                    orientation=orientation,
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Media download failed : {str(e)}",
                )

        # ======================================================
        # Validate Download
        # ======================================================

        if not media:

            raise HTTPException(

                status_code=404,

                detail="No media found from Pexels or Pixabay.",

            )

        if not os.path.exists(media["file_path"]):

            raise HTTPException(

                status_code=500,

                detail="Downloaded file not found.",

            )

        # ======================================================
        # Create Media Record
        # ======================================================

        media_record = Media(

            user_id=scene.user_id,

            project_id=scene.project_id,

            media_type=scene.media_type,

            provider=media["provider"],

            title=f"Scene {scene.scene_number}",

            file_name=filename,

            file_path=media["file_path"],

            file_url=media.get("file_url", ""),

            mime_type=media["mime_type"],

            extension=media["extension"],

            duration=media.get("duration"),

            width=media.get("width"),

            height=media.get("height"),

            file_size=media.get("file_size"),

            status="ready",

        )

                # ======================================================
        # Save Media + Update Scene
        # ======================================================

        try:

            db.add(media_record)

            db.flush()

            # Update Scene

            scene.media_id = media_record.id

            scene.status = "downloaded"

            db.commit()

            db.refresh(media_record)

            db.refresh(scene)

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=500,

                detail=f"Database error : {str(e)}",

            )

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

            "media_type": media_record.media_type,

            "status": media_record.status,

        }

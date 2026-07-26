import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media

from app.core.subtitle_client import SubtitleClient


class SubtitleService:

    @staticmethod
    def generate(
        db: Session,
        scene_id: int,
    ):

        # ===========================================
        # Load Scene
        # ===========================================

        scene = (
            db.query(Scene)
            .filter(Scene.id == scene_id)
            .first()
        )

        if not scene:

            raise HTTPException(
                status_code=404,
                detail="Scene not found."
            )

        # ===========================================
        # Subtitle Folder
        # ===========================================

        subtitle_folder = os.path.join(
            "storage",
            "projects",
            str(scene.project_id),
            "subtitles",
        )

        os.makedirs(
            subtitle_folder,
            exist_ok=True,
        )

        filename = f"scene_{scene.scene_number}.srt"

        output_path = os.path.join(
            subtitle_folder,
            filename,
        )

        # ===========================================
        # Generate Subtitle
        # ===========================================

        SubtitleClient.generate_srt(

            text=scene.text,

            duration=scene.duration,

            output_path=output_path,

        )

        # ===========================================
        # Check Existing Subtitle
        # ===========================================

        media = (
            db.query(Media)
            .filter(
                Media.project_id == scene.project_id,
                Media.media_type == "subtitle",
                Media.file_name == filename,
            )
            .first()
        )

        if media:

            media.file_path = output_path

            media.status = "ready"

        else:

            media = Media(

                user_id=scene.user_id,

                project_id=scene.project_id,

                media_type="subtitle",

                provider="Subtitle",

                title=f"Scene {scene.scene_number} Subtitle",

                file_name=filename,

                file_path=output_path,

                file_url="",

                mime_type="text/plain",

                extension=".srt",

                duration=scene.duration,

                width=0,

                height=0,

                file_size=os.path.getsize(output_path),

                status="ready",

            )

            db.add(media)

        db.commit()

        db.refresh(media)

        return {

            "success": True,

            "scene_id": scene.id,

            "media_id": media.id,

            "provider": "Subtitle",

            "file_name": filename,

            "file_path": output_path,

            "status": media.status,

        }
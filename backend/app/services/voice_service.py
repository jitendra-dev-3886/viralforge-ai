import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media

from app.core.edge_tts_client import EdgeTTSClient


class VoiceService:

    @staticmethod
    def generate(
        db: Session,
        scene_id: int,
        voice: str = "en-US-AriaNeural",
    ):

        # =====================================================
        # Get Scene
        # =====================================================

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

        if not scene.text:

            raise HTTPException(
                status_code=400,
                detail="Scene text is empty.",
            )

        # =====================================================
        # Storage Folder
        # =====================================================

        folder = os.path.join(
            "storage",
            "projects",
            str(scene.project_id),
            "audio",
        )

        os.makedirs(
            folder,
            exist_ok=True,
        )

        filename = f"scene_{scene.scene_number}.mp3"

        filepath = os.path.join(
            folder,
            filename,
        )

        # =====================================================
        # Generate Voice
        # =====================================================

        result = EdgeTTSClient.generate(
            text=scene.text,
            output_file=filepath,
            voice=voice,
        )

        # =====================================================
        # Save Media
        # =====================================================

        media = Media(

            user_id=scene.user_id,

            project_id=scene.project_id,

            media_type="audio",

            provider="Edge-TTS",

            title=f"Scene {scene.scene_number} Voice",

            file_name=filename,

            file_path=result["path"],

            file_url="",

            mime_type="audio/mpeg",

            extension=".mp3",

            duration=scene.duration,

            width=0,

            height=0,

            file_size=result["size"],

            status="ready",

        )

        db.add(media)

        db.commit()

        db.refresh(media)

        # =====================================================
        # Response
        # =====================================================

        return {

            "success": True,

            "scene_id": scene.id,

            "media_id": media.id,

            "provider": "Edge-TTS",

            "voice": voice,

            "file_name": filename,

            "file_path": filepath,

            "status": media.status,

        }
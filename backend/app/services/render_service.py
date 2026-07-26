import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media

from app.core.ffmpeg_client import FFmpegClient
from app.core.subtitle_burner import SubtitleBurner


class RenderService:

    @staticmethod
    def generate(
        db: Session,
        scene_id: int,
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
                detail="Scene not found."
            )

        # =====================================================
        # Get Video (or Image saved as Video)
        # =====================================================

        video = (
            db.query(Media)
            .filter(
                Media.id == scene.media_id,
                # Allowing both just in case it was saved as image
                Media.media_type.in_(["video", "image"]) 
            )
            .first()
        )

        if not video:
            raise HTTPException(
                status_code=404,
                detail="Video not found."
            )

        # =====================================================
        # Get Audio
        # =====================================================

        audio = (
            db.query(Media)
            .filter(
                Media.project_id == scene.project_id,
                Media.media_type == "audio",
                Media.title == f"Scene {scene.scene_number} Voice"
            )
            .first()
        )

        if not audio:
            raise HTTPException(
                status_code=404,
                detail="Audio not found."
            )

        # =====================================================
        # Output Folder
        # =====================================================

        render_folder = os.path.join(
            "storage",
            "projects",
            str(scene.project_id),
            "render",
        )

        os.makedirs(
            render_folder,
            exist_ok=True,
        )

        filename = f"scene_{scene.scene_number}_final.mp4"

        output_path = os.path.join(
            render_folder,
            filename,
        )

        # =====================================================
        # Convert to Absolute Paths for FFmpeg
        # =====================================================
        
        abs_video_path = os.path.abspath(video.file_path)
        abs_audio_path = os.path.abspath(audio.file_path)
        abs_output_path = os.path.abspath(output_path)

        # =====================================================
        # Render
        # =====================================================

        FFmpegClient.merge_video_audio(
            video_path=abs_video_path,
            audio_path=abs_audio_path,
            output_path=abs_output_path,
        )

        # =====================================================
        # Save Media
        # =====================================================

        media = Media(
            user_id=scene.user_id,
            project_id=scene.project_id,
            media_type="render",
            provider="FFmpeg",
            title=f"Scene {scene.scene_number} Final",
            file_name=filename,
            file_path=output_path,  # Keep relative path for DB
            file_url="",
            mime_type="video/mp4",
            extension=".mp4",
            duration=scene.duration,
            width=video.width,
            height=video.height,
            file_size=os.path.getsize(abs_output_path),
            status="ready",
        )

        db.add(media)
        db.commit()
        db.refresh(media)

        return {
            "success": True,
            "scene_id": scene.id,
            "media_id": media.id,
            "file_name": filename,
            "file_path": output_path,
            "status": media.status,
        }
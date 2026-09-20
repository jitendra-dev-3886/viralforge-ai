import os
import hashlib
from pathlib import Path
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media
from app.models.voice import Voice

from app.core.ffmpeg_client import FFmpegClient
from app.core.subtitle_burner import SubtitleBurner


BACKEND_DIR = Path(__file__).resolve().parents[2]


def _stored_path(value: str | None) -> Path | None:
    """Resolve old cwd-relative database paths against the backend directory."""
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = path.resolve()
    backend_path = (BACKEND_DIR / path).resolve()
    return cwd_path if cwd_path.exists() else backend_path


class RenderService:

    @staticmethod
    def generate(
        db: Session,
        scene_id: int,
        user_id: int,
    ):

        # =====================================================
        # Get Scene
        # =====================================================

        scene = (
            db.query(Scene)
            .filter(Scene.id == scene_id, Scene.user_id == user_id)
            .first()
        )

        if not scene:
            raise HTTPException(
                status_code=404,
                detail="Scene not found."
            )

        # =====================================================
        # Get the scene source. Carousel scenes use images; reel/video scenes
        # use clips. Both are normalized to MP4 only for the combined render.
        # =====================================================

        source_media = (
            db.query(Media)
            .filter(
                Media.id == scene.media_id,
                # Allowing both just in case it was saved as image
                Media.media_type.in_(["video", "image"]) 
            )
            .first()
        )

        if not source_media:
            raise HTTPException(
                status_code=404,
                detail="Scene image or video media was not found. Regenerate the missing scene media and try again."
            )

        # =====================================================
        # Get Audio
        # =====================================================

        voice = (
            db.query(Voice)
            .filter(
                Voice.scene_id == scene.id,
                Voice.content_id == scene.content_id,
                Voice.user_id == user_id,
                Voice.status == "generated",
            )
            .order_by(Voice.updated_at.desc(), Voice.created_at.desc(), Voice.id.desc())
            .first()
        )

        # =====================================================
        # Output Folder
        # =====================================================

        render_folder = BACKEND_DIR / "storage" / "projects" / str(scene.project_id) / "render"

        os.makedirs(
            render_folder,
            exist_ok=True,
        )

        filename = f"content_{scene.content_id}_scene_{scene.scene_number}_final.mp4"

        output_path = render_folder / filename

        # =====================================================
        # Convert to Absolute Paths for FFmpeg
        # =====================================================
        
        source_path = _stored_path(source_media.file_path)
        abs_video_path = str(source_path) if source_path else ""
        if not source_path or not source_path.exists():
            raise HTTPException(status_code=404, detail="The saved scene media file is missing from storage.")
        voice_path = _stored_path(voice.audio_path) if voice else None
        if voice and (not voice_path or not voice_path.is_file()):
            raise HTTPException(status_code=422, detail=f"Scene {scene.scene_number}'s voice file is missing. Generate its voice again before merging.")
        abs_audio_path = str(voice_path) if voice_path and voice_path.exists() else None
        abs_output_path = str(output_path.resolve())

        platform = (scene.content.platform or "").lower()
        content_type = (scene.content.content_type or "").lower()
        if "reel" in content_type or "short" in content_type or "story" in content_type:
            output_width, output_height = 1080, 1920
        elif "carousel" in content_type and "instagram" in platform:
            output_width, output_height = 1080, 1350
        elif "carousel" in content_type:
            output_width, output_height = 1080, 1080
        elif "youtube" in platform and ("video" in content_type):
            output_width, output_height = 1920, 1080
        elif "instagram" in platform:
            output_width, output_height = 1080, 1350
        else:
            output_width, output_height = 1080, 1080

        generation_config = scene.content.generation_config or {}
        branding = generation_config.get("branding", {})
        overlay_layout = generation_config.get("overlay_layout", {})
        text_position = overlay_layout.get("text", {})
        logo_position = overlay_layout.get("logo", {})
        username_position = overlay_layout.get("username", {})
        username = branding.get("username") or branding.get("brand_name") or ""
        overlay_text = str(scene.text or "").strip()
        logo_path = None
        logo_url = branding.get("logo")
        if logo_url:
            try:
                logo_folder = Path(render_folder) / "branding"
                logo_folder.mkdir(parents=True, exist_ok=True)
                logo_key = hashlib.sha256(str(logo_url).encode("utf-8")).hexdigest()[:12]
                candidate = logo_folder / f"content_{scene.content_id}_{logo_key}.logo"
                local_logo = None
                if str(logo_url).startswith("/storage/"):
                    local_logo = BACKEND_DIR / str(logo_url).lstrip("/")
                elif not str(logo_url).lower().startswith(("http://", "https://")):
                    local_logo = _stored_path(str(logo_url))
                if local_logo and local_logo.exists():
                    logo_path = str(local_logo.resolve())
                else:
                    if not candidate.exists():
                        response = requests.get(str(logo_url), timeout=15)
                        response.raise_for_status()
                        candidate.write_bytes(response.content)
                    logo_path = str(candidate.resolve())
            except Exception:
                logo_path = None

        # =====================================================
        # Render
        # =====================================================

        render_result = FFmpegClient.render_media(
            video_path=abs_video_path,
            audio_path=abs_audio_path,
            output_path=abs_output_path,
            duration=scene.duration or 5,
            width=output_width,
            height=output_height,
            overlay_text=overlay_text,
            username=username,
            logo_path=logo_path,
            text_x_pct=text_position.get("x", 50),
            text_y_pct=text_position.get("y", 68),
            logo_x_pct=logo_position.get("x", 10),
            logo_y_pct=logo_position.get("y", 8),
            username_x_pct=username_position.get("x", 82),
            username_y_pct=username_position.get("y", 92),
            transition=scene.transition or "fade",
        )

        # =====================================================
        # Save Media
        # =====================================================

        media = Media(
            user_id=scene.user_id,
            project_id=scene.project_id,
            media_type="render",
            provider="FFmpeg",
            title=f"Content {scene.content_id} Scene {scene.scene_number} Branded Final",
            file_name=filename,
            file_path=str(output_path),
            file_url=f"/storage/projects/{scene.project_id}/render/{filename}",
            mime_type="video/mp4",
            extension=".mp4",
            duration=round(render_result["duration"]),
            width=output_width,
            height=output_height,
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

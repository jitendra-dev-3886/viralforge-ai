from pathlib import Path
import os

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project
from app.models.scene import Scene
from app.models.media import Media

from app.services.render_service import RenderService
from app.services.downloader_service import DownloaderService
from app.core.ffmpeg_client import FFmpegClient


class ProjectRenderService:

    BASE_DIR = Path(__file__).resolve().parents[2] / "storage" / "projects"

    @staticmethod
    def _media_path(value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        cwd_path = path.resolve()
        backend_path = (Path(__file__).resolve().parents[2] / path).resolve()
        return cwd_path if cwd_path.exists() else backend_path

    # ==========================================================
    # Generate Final Project Video
    # ==========================================================

    @staticmethod
    def generate(
        db: Session,
        project_id: int,
        user_id: int,
        content_id: int | None = None,
    ):

        # ======================================================
        # Get Project
        # ======================================================

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == user_id,
            )
            .first()
        )

        if not project:

            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        # ======================================================
        # Get Scenes
        # ======================================================

        if content_id is None:
            latest_scene = db.query(Scene).filter(
                Scene.project_id == project_id,
                Scene.user_id == user_id,
            ).order_by(Scene.created_at.desc()).first()
            content_id = latest_scene.content_id if latest_scene else None

        scenes = (
            db.query(Scene)
            .filter(
                Scene.project_id == project_id,
                Scene.user_id == user_id,
                Scene.content_id == content_id,
            )
            .order_by(
                Scene.scene_number.asc(),
            )
            .all()
        )

        if not scenes:

            raise HTTPException(
                status_code=404,
                detail="No scenes found.",
            )

        # ======================================================
        # Output Folder
        # ======================================================

        output_folder = (
            ProjectRenderService.BASE_DIR
            / str(project_id)
            / "output"
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ======================================================
        # Render Folder
        # ======================================================

        render_folder = (
            ProjectRenderService.BASE_DIR
            / str(project_id)
            / "render"
        )

        render_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ======================================================
        # Render All Scenes
        # ======================================================

        rendered_files = []

        total_duration = 0

        first_scene_render = None

        for scene in scenes:

            source_media = db.query(Media).filter(
                Media.id == scene.media_id,
                Media.media_type.in_(["image", "video"]),
            ).first() if scene.media_id else None
            source_exists = bool(source_media and ProjectRenderService._media_path(source_media.file_path).exists())

            if not source_exists:
                scene.media_id = None
                db.flush()
                try:
                    DownloaderService.download(db=db, scene_id=scene.id, user_id=user_id)
                    db.refresh(scene)
                except Exception as exc:
                    fallback_scene = next((item for item in reversed(scenes) if item.scene_number < scene.scene_number and item.media_id and item.media and ProjectRenderService._media_path(item.media.file_path).exists()), None)
                    if fallback_scene is None:
                        fallback_scene = next((item for item in scenes if item.media_id and item.media and ProjectRenderService._media_path(item.media.file_path).exists()), None)
                    if fallback_scene is None:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Scene {scene.scene_number} has no media and automatic download failed: {exc}",
                        ) from exc
                    scene.media_id = fallback_scene.media_id
                    scene.status = "media_fallback"
                    db.commit()
                    db.refresh(scene)

            # --------------------------------------------------
            # Find Existing Render
            # --------------------------------------------------

            render_media = (
                db.query(Media)
                .filter(
                    Media.project_id == project_id,
                    Media.media_type == "render",
                    Media.title == (
                        f"Content {scene.content_id} Scene {scene.scene_number} Branded Final"
                    ),
                )
                .order_by(Media.created_at.desc())
                .first()
            )

            # --------------------------------------------------
            # Check Existing File
            # --------------------------------------------------

            if render_media:

                render_path = ProjectRenderService._media_path(render_media.file_path)

                latest_voice = max(
                    (voice.updated_at or voice.created_at for voice in scene.voices),
                    default=None,
                )
                latest_audio = (
                    db.query(Media)
                    .filter(
                        Media.project_id == project_id,
                        Media.user_id == user_id,
                        Media.media_type == "audio",
                        Media.title == f"Scene {scene.scene_number} Voice",
                    )
                    .order_by(Media.updated_at.desc())
                    .first()
                )
                dependency_dates = [
                    value for value in (
                        scene.content.updated_at,
                        scene.updated_at,
                        source_media.updated_at if source_media else None,
                        latest_voice,
                        (latest_audio.updated_at or latest_audio.created_at) if latest_audio else None,
                    ) if value is not None
                ]
                render_is_current = (
                    not dependency_dates
                    or not render_media.created_at
                    or all(render_media.created_at >= value for value in dependency_dates)
                )

                if (
                    render_path.exists()
                    and render_is_current
                    and FFmpegClient.is_media_readable(str(render_path))
                ):

                    rendered_files.append(
                        str(
                            render_path.resolve()
                        )
                    )

                    if first_scene_render is None:
                        first_scene_render = render_media

                    if render_media.duration:
                        total_duration += (
                            render_media.duration
                        )

                    continue

            # --------------------------------------------------
            # Render Scene
            # --------------------------------------------------

            RenderService.generate(
                db=db,
                scene_id=scene.id,
                user_id=user_id,
            )

            # --------------------------------------------------
            # Get Newly Rendered Media
            # --------------------------------------------------

            render_media = (
                db.query(Media)
                .filter(
                    Media.project_id == project_id,
                    Media.media_type == "render",
                    Media.title == (
                        f"Content {scene.content_id} Scene {scene.scene_number} Branded Final"
                    ),
                )
                .order_by(Media.created_at.desc())
                .first()
            )

            if not render_media:

                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Scene {scene.scene_number} "
                        f"render failed."
                    ),
                )

            render_path = ProjectRenderService._media_path(render_media.file_path)

            if not render_path.exists():

                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Rendered file not found for "
                        f"scene {scene.scene_number}."
                    ),
                )

            rendered_files.append(
                str(
                    render_path.resolve()
                )
            )

            if first_scene_render is None:
                first_scene_render = render_media

            if render_media.duration:
                total_duration += (
                    render_media.duration
                )

        # ======================================================
        # Validate Render Files
        # ======================================================

        if not rendered_files:

            raise HTTPException(
                status_code=400,
                detail="No rendered scene found.",
            )

        # ======================================================
        # Create FFmpeg Concat File
        # ======================================================

        concat_file = (
            render_folder / "concat.txt"
        )

        with open(
            concat_file,
            "w",
            encoding="utf-8",
        ) as f:

            for file_path in rendered_files:

                # FFmpeg concat format
                normalized_path = (
                    file_path
                    .replace("\\", "/")
                )

                f.write(
                    f"file '{normalized_path}'\n"
                )

        # ======================================================
        # Final Output
        # ======================================================

        final_filename = f"content_{content_id}_final.mp4"

        final_output = (
            output_folder / final_filename
        )

        # ======================================================
        # Merge Videos
        # ======================================================

        FFmpegClient.concat_videos(
            concat_file=str(
                concat_file.resolve()
            ),
            output_path=str(
                final_output.resolve()
            ),
        )

        music = db.query(Media).filter(
            Media.project_id == project_id,
            Media.user_id == user_id,
            Media.media_type == "music",
            Media.status == "ready",
        ).order_by(Media.created_at.desc()).first()
        music_path = ProjectRenderService._media_path(music.file_path) if music else None
        if music_path and music_path.exists():
            mixed_output = output_folder / f"content_{content_id}_mixed.mp4"
            FFmpegClient.add_background_music(
                video_path=str(final_output.resolve()),
                music_path=str(music_path.resolve()),
                output_path=str(mixed_output.resolve()),
            )
            os.replace(mixed_output, final_output)

        # ======================================================
        # Validate Output
        # ======================================================

        if not final_output.exists():

            raise HTTPException(
                status_code=500,
                detail="Final render failed.",
            )

        file_size = (
            final_output.stat().st_size
        )

        if file_size <= 0:

            raise HTTPException(
                status_code=500,
                detail="Final video is empty.",
            )

        # ======================================================
        # Remove Old Final Media
        # ======================================================

        old_media = (
            db.query(Media)
            .filter(
                Media.project_id == project_id,
                Media.media_type == "final",
                Media.title == f"Content {content_id} Final",
            )
            .first()
        )

        if old_media:

            db.delete(old_media)

            db.flush()

        # ======================================================
        # Save Final Media
        # ======================================================

        media = Media(

            user_id=project.user_id,

            project_id=project.id,

            media_type="final",

            provider="FFmpeg",

            title=f"Content {content_id} Final",

            file_name=final_filename,

            file_path=str(
                final_output
            ),

            file_url=f"/storage/projects/{project_id}/output/{final_filename}",

            mime_type="video/mp4",

            extension=".mp4",

            duration=(
                total_duration
                if total_duration > 0
                else None
            ),

            width=(
                first_scene_render.width
                if first_scene_render
                else None
            ),

            height=(
                first_scene_render.height
                if first_scene_render
                else None
            ),

            file_size=file_size,

            status="ready",
        )

        db.add(media)

        db.commit()

        db.refresh(media)

        # ======================================================
        # Cleanup Concat File
        # ======================================================

        if concat_file.exists():

            concat_file.unlink()

        # ======================================================
        # Response
        # ======================================================

        return {

            "success": True,

            "project_id": project.id,

            "content_id": content_id,

            "media_id": media.id,

            "file_name": media.file_name,

            "file_path": media.file_path,

            "file_url": media.file_url,

            "duration": media.duration,

            "status": media.status,

        }

    # ==========================================================
    # Get Final Video
    # ==========================================================

    @staticmethod
    def get_final_video(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        media = (
            db.query(Media).join(Project, Project.id == Media.project_id)
            .filter(
                Media.project_id == project_id,
                Media.media_type == "final",
                Project.user_id == user_id,
            )
            .order_by(Media.created_at.desc())
            .first()
        )

        if not media:

            raise HTTPException(
                status_code=404,
                detail="Final video not found.",
            )

        return {

            "success": True,

            "video": media,

        }

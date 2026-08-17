from pathlib import Path
import os

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project
from app.models.scene import Scene
from app.models.media import Media

from app.services.render_service import RenderService
from app.core.ffmpeg_client import FFmpegClient


class ProjectRenderService:

    BASE_DIR = Path("storage/projects")

    # ==========================================================
    # Generate Final Project Video
    # ==========================================================

    @staticmethod
    def generate(
        db: Session,
        project_id: int,
    ):

        # ======================================================
        # Get Project
        # ======================================================

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
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

        scenes = (
            db.query(Scene)
            .filter(
                Scene.project_id == project_id,
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

            # --------------------------------------------------
            # Find Existing Render
            # --------------------------------------------------

            render_media = (
                db.query(Media)
                .filter(
                    Media.project_id == project_id,
                    Media.media_type == "render",
                    Media.title == (
                        f"Scene {scene.scene_number} Final"
                    ),
                )
                .first()
            )

            # --------------------------------------------------
            # Check Existing File
            # --------------------------------------------------

            if render_media:

                render_path = Path(
                    render_media.file_path
                )

                if render_path.exists():

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
                        f"Scene {scene.scene_number} Final"
                    ),
                )
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

            render_path = Path(
                render_media.file_path
            )

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

        final_filename = "final.mp4"

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

            title="Final Project Video",

            file_name=final_filename,

            file_path=str(
                final_output
            ),

            file_url="",

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

            "media_id": media.id,

            "file_name": media.file_name,

            "file_path": media.file_path,

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
    ):

        media = (
            db.query(Media)
            .filter(
                Media.project_id == project_id,
                Media.media_type == "final",
            )
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
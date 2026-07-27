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
        # Render Missing Scenes
        # ======================================================

        rendered_files = []

        for scene in scenes:

            render_media = (

                db.query(Media)

                .filter(

                    Media.project_id == project_id,

                    Media.media_type == "render",

                    Media.title == f"Scene {scene.scene_number} Final",

                )

                .first()

            )

            # Already rendered

            if render_media and os.path.exists(render_media.file_path):

                rendered_files.append(

                    os.path.abspath(render_media.file_path)

                )

                continue

            # Render Scene

            RenderService.generate(

                db=db,

                scene_id=scene.id,

            )

            render_media = (

                db.query(Media)

                .filter(

                    Media.project_id == project_id,

                    Media.media_type == "render",

                    Media.title == f"Scene {scene.scene_number} Final",

                )

                .first()

            )

            if render_media:

                rendered_files.append(

                    os.path.abspath(render_media.file_path)

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
        # Concat File
        # ======================================================

        concat_file = render_folder / "concat.txt"

        with open(concat_file, "w", encoding="utf-8") as f:

            for file in rendered_files:

                f.write(
                    f"file '{file}'\n"
                )

        # ======================================================
        # Final Output
        # ======================================================

        final_filename = "final.mp4"

        final_output = (

            output_folder

            / final_filename

        )

        # ======================================================
        # Merge Videos
        # ======================================================

        FFmpegClient.concat_videos(

            concat_file=str(
                concat_file.absolute()
            ),

            output_path=str(
                final_output.absolute()
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

        file_size = final_output.stat().st_size

        # ======================================================
        # Remove Old Final Record
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

            db.commit()

        # ======================================================
        # Prepare Media Object
        # ======================================================

        first_scene_render = (

            db.query(Media)

            .filter(

                Media.project_id == project_id,

                Media.media_type == "render",

            )

            .first()

        )
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

            file_path=str(final_output),

            file_url="",

            mime_type="video/mp4",

            extension=".mp4",

            duration=first_scene_render.duration if first_scene_render else None,

            width=first_scene_render.width if first_scene_render else None,

            height=first_scene_render.height if first_scene_render else None,

            file_size=file_size,

            status="ready",

        )

        db.add(media)

        db.commit()

        db.refresh(media)

        # ======================================================
        # Cleanup
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
from pathlib import Path
from datetime import datetime
import uuid

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectService:

    BASE_DIR = Path("storage/projects")

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        request: ProjectCreate,
    ):

        # ==========================================
        # Generate Unique Folder Name
        # ==========================================

        folder_name = (
            datetime.now().strftime("%Y%m%d_%H%M%S")
            + "_"
            + uuid.uuid4().hex[:6]
        )

        project_path = ProjectService.BASE_DIR / folder_name

        folders = [
            "content",
            "audio",
            "images",
            "videos",
            "subtitle",
            "thumbnail",
            "output",
            "logs",
        ]

        for folder in folders:
            (project_path / folder).mkdir(
                parents=True,
                exist_ok=True,
            )

        # ==========================================
        # Save Project in Database
        # ==========================================

        project = Project(

        user_id=user_id,

        brand_id=request.brand_id,

        title=request.title,

        topic=request.topic,

        niche=request.niche,

        category=request.category,

        platform=request.platform,

        content_type=request.content_type,

        language=request.language,

        ai_provider=request.ai_provider,

        prompt=request.prompt,

        status="draft",

        folder=folder_name,

        path=str(project_path),

    )

        db.add(project)
        db.commit()
        db.refresh(project)

        # ==========================================
        # Response
        # ==========================================

        return {

            "success": True,

            "message": "Project created successfully.",

            "project": {

                "id": project.id,

                "title": project.title,

                "topic": project.topic,

                "platform": project.platform,

                "content_type": project.content_type,

                "status": project.status,

                "folder": folder_name,

                "path": str(project_path),

                "directories": {

                    "content": str(project_path / "content"),

                    "audio": str(project_path / "audio"),

                    "images": str(project_path / "images"),

                    "videos": str(project_path / "videos"),

                    "subtitle": str(project_path / "subtitle"),

                    "thumbnail": str(project_path / "thumbnail"),

                    "output": str(project_path / "output"),

                    "logs": str(project_path / "logs"),

                },

            },

        }

    # =========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        return (

            db.query(Project)

            .filter(Project.user_id == user_id)

            .order_by(Project.created_at.desc())

            .all()

        )

    # =========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        return (

            db.query(Project)

            .filter(

                Project.id == project_id,

                Project.user_id == user_id,

            )

            .first()

        )

    # =========================================================

    @staticmethod
    def delete(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        project = (

            db.query(Project)

            .filter(

                Project.id == project_id,

                Project.user_id == user_id,

            )

            .first()

        )

        if not project:

            return {

                "success": False,

                "message": "Project not found.",

            }

        db.delete(project)
        db.commit()

        return {

            "success": True,

            "message": "Project deleted successfully.",

        }
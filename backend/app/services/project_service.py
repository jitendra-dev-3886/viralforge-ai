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
    def serialize_project(project: Project):
        if not project:
            return None

        return {
            "id": project.id,
            "user_id": project.user_id,
            "brand_id": project.brand_id,
            "title": project.title,
            "topic": project.topic,
            "niche": project.niche,
            "category": project.category,
            "platform": project.platform,
            "content_type": project.content_type,
            "language": project.language,
            "status": project.status,
            "ai_provider": project.ai_provider,
            "prompt": project.prompt,
            "folder": project.folder,
            "path": project.path,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }

    # =========================================================

    @staticmethod
    def get_projects(
        db: Session,
        user_id: int,
    ):

        projects = ProjectService.get_all(db=db, user_id=user_id)
        serialized = [ProjectService.serialize_project(project) for project in projects]

        return {
            "success": True,
            "total": len(serialized),
            "projects": serialized,
        }

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
    def get_project(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        project = ProjectService.get_by_id(
            db=db,
            project_id=project_id,
            user_id=user_id,
        )

        if not project:
            return None

        return {
            "success": True,
            "project": ProjectService.serialize_project(project),
        }

    # =========================================================

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        user_id: int,
        request,
    ):

        project = ProjectService.get_by_id(
            db=db,
            project_id=project_id,
            user_id=user_id,
        )

        if not project:
            return None

        project.title = request.title or project.title
        project.topic = request.topic or project.topic
        project.platform = request.platform or project.platform
        project.content_type = request.content_type or project.content_type
        project.niche = request.niche if request.niche is not None else project.niche
        project.category = request.category if request.category is not None else project.category
        project.language = request.language or project.language
        project.brand_id = request.brand_id if request.brand_id is not None else project.brand_id
        project.ai_provider = request.ai_provider if request.ai_provider is not None else project.ai_provider
        project.prompt = request.prompt if request.prompt is not None else project.prompt
        project.status = request.status or project.status

        db.commit()
        db.refresh(project)

        return {
            "success": True,
            "message": "Project updated successfully.",
            "project": ProjectService.serialize_project(project),
        }

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
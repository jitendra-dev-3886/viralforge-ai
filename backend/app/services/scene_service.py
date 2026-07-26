from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.schemas.scene import (
    SceneCreate,
    SceneUpdate,
)


class SceneService:

    # ==========================================================
    # Create Scene
    # ==========================================================

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        request: SceneCreate,
    ):

        scene = Scene(

            user_id=user_id,

            project_id=request.project_id,

            content_id=request.content_id,

            scene_number=request.scene_number,

            text=request.text,

            keyword=request.keyword,

            media_type=request.media_type,

            duration=request.duration,

            media_id=request.media_id,

            status=request.status,

        )

        db.add(scene)

        db.commit()

        db.refresh(scene)

        return {
            "success": True,
            "message": "Scene created successfully.",
            "scene": scene,
        }

    # ==========================================================
    # Generate Scenes From AI
    # ==========================================================

    @staticmethod
    def generate(
        db: Session,
        project_id: int,
        content_id: int,
        user_id: int,
        ai_data: dict,
    ):

        scenes = ai_data.get("scenes", [])

        created = []

        for index, item in enumerate(scenes, start=1):

            scene = Scene(

                user_id=user_id,

                project_id=project_id,

                content_id=content_id,

                scene_number=item.get(
                    "scene_number",
                    item.get("scene", index),
                ),

                text=item.get("text", ""),

                keyword=item.get("keyword"),

                media_type=item.get(
                    "media_type",
                    "image",
                ),

                duration=item.get(
                    "duration",
                    5,
                ),

                status="pending",

            )

            db.add(scene)

            created.append(scene)

        db.flush()

        return created

    # ==========================================================
    # Get All Scenes
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        return (
            db.query(Scene)
            .filter(Scene.user_id == user_id)
            .order_by(Scene.scene_number.asc())
            .all()
        )

    # ==========================================================
    # Get By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        scene_id: int,
        user_id: int,
    ):

        return (
            db.query(Scene)
            .filter(
                Scene.id == scene_id,
                Scene.user_id == user_id,
            )
            .first()
        )

    # ==========================================================
    # Get Project Scenes
    # ==========================================================

    @staticmethod
    def get_project_scenes(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        return (
            db.query(Scene)
            .filter(
                Scene.project_id == project_id,
                Scene.user_id == user_id,
            )
            .order_by(Scene.scene_number.asc())
            .all()
        )

    # ==========================================================
    # Get Content Scenes
    # ==========================================================

    @staticmethod
    def get_content_scenes(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        return (
            db.query(Scene)
            .filter(
                Scene.content_id == content_id,
                Scene.user_id == user_id,
            )
            .order_by(Scene.scene_number.asc())
            .all()
        )

    # ==========================================================
    # Update Scene
    # ==========================================================

    @staticmethod
    def update(
        db: Session,
        scene_id: int,
        user_id: int,
        request: SceneUpdate,
    ):

        scene = (
            db.query(Scene)
            .filter(
                Scene.id == scene_id,
                Scene.user_id == user_id,
            )
            .first()
        )

        if not scene:

            return {
                "success": False,
                "message": "Scene not found.",
            }

        data = request.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(scene, key, value)

        db.commit()

        db.refresh(scene)

        return {
            "success": True,
            "message": "Scene updated successfully.",
            "scene": scene,
        }

    # ==========================================================
    # Delete Scene
    # ==========================================================

    @staticmethod
    def delete(
        db: Session,
        scene_id: int,
        user_id: int,
    ):

        scene = (
            db.query(Scene)
            .filter(
                Scene.id == scene_id,
                Scene.user_id == user_id,
            )
            .first()
        )

        if not scene:

            return {
                "success": False,
                "message": "Scene not found.",
            }

        db.delete(scene)

        db.commit()

        return {
            "success": True,
            "message": "Scene deleted successfully.",
        }
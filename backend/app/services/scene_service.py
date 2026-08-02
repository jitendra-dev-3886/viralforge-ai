from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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

        try:

            scene = Scene(

                user_id=user_id,

                project_id=request.project_id,

                content_id=request.content_id,

                scene_number=request.scene_number,

                title=request.title,

                text=request.text,

                keyword=request.keyword,

                image_prompt=request.image_prompt,

                video_prompt=request.video_prompt,

                voice_text=request.voice_text,

                subtitle=request.subtitle,

                media_type=request.media_type,

                duration=request.duration,

                camera_angle=request.camera_angle,

                transition=request.transition,

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

        except SQLAlchemyError as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

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
        package: str = "",
    ):

        try:

            created_scenes = []

            scenes = ai_data.get("scenes", [])

            for index, item in enumerate(scenes, start=1):

                scene = Scene(

                    user_id=user_id,

                    project_id=project_id,

                    content_id=content_id,

                    scene_number=item.get(
                        "scene_number",
                        index,
                    ),

                    title=item.get("title"),

                    text=item.get("text", ""),

                    keyword=item.get("keyword"),

                    image_prompt=item.get("image_prompt"),

                    video_prompt=item.get("video_prompt"),

                    voice_text=item.get("voice_text"),

                    subtitle=item.get("subtitle"),

                    media_type=item.get(
                        "media_type",
                        "image",
                    ),

                    duration=item.get(
                        "duration",
                        5,
                    ),

                    camera_angle=item.get(
                        "camera_angle",
                    ),

                    transition=item.get(
                        "transition",
                    ),

                    status="pending",

                )

                # Force carousel package scenes to image only during persistence
                if (package or "").lower() == "carousel":
                    scene.media_type = "image"

                db.add(scene)

                created_scenes.append(scene)

            db.commit()

            for scene in created_scenes:

                db.refresh(scene)

            return {

                "success": True,

                "message": "Scenes generated successfully.",

                "total": len(created_scenes),

                "scenes": created_scenes,

            }

        except SQLAlchemyError as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

            }
            # ==========================================================
    # Get All Scenes
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        try:

            scenes = (
                db.query(Scene)
                .filter(Scene.user_id == user_id)
                .order_by(Scene.scene_number.asc())
                .all()
            )

            return scenes

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Scene By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        scene_id: int,
        user_id: int,
    ):

        try:

            scene = (
                db.query(Scene)
                .filter(
                    Scene.id == scene_id,
                    Scene.user_id == user_id,
                )
                .first()
            )

            return scene

        except SQLAlchemyError:

            return None

    # ==========================================================
    # Get Scenes By Project
    # ==========================================================

    @staticmethod
    def get_project_scenes(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        try:

            scenes = (
                db.query(Scene)
                .filter(
                    Scene.project_id == project_id,
                    Scene.user_id == user_id,
                )
                .order_by(Scene.scene_number.asc())
                .all()
            )

            return scenes

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Scenes By Content
    # ==========================================================

    @staticmethod
    def get_content_scenes(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        try:

            scenes = (
                db.query(Scene)
                .filter(
                    Scene.content_id == content_id,
                    Scene.user_id == user_id,
                )
                .order_by(Scene.scene_number.asc())
                .all()
            )

            return scenes

        except SQLAlchemyError:

            return []
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

        try:

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

        except SQLAlchemyError as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

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

        try:

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

        except SQLAlchemyError as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

            }

    # ==========================================================
    # Delete All Scenes of Project
    # ==========================================================

    @staticmethod
    def delete_project_scenes(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        try:

            scenes = (
                db.query(Scene)
                .filter(
                    Scene.project_id == project_id,
                    Scene.user_id == user_id,
                )
                .all()
            )

            for scene in scenes:

                db.delete(scene)

            db.commit()

            return {

                "success": True,

                "message": "All project scenes deleted successfully.",

                "deleted": len(scenes),

            }

        except SQLAlchemyError as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

            }

    # ==========================================================
    # Update Scene Status
    # ==========================================================

    @staticmethod
    def update_status(
        db: Session,
        scene_id: int,
        status: str,
    ):

        try:

            scene = (
                db.query(Scene)
                .filter(Scene.id == scene_id)
                .first()
            )

            if not scene:

                return None

            scene.status = status

            db.commit()

            db.refresh(scene)

            return scene

        except SQLAlchemyError:

            db.rollback()

            return None
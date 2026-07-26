from sqlalchemy.orm import Session

from app.models.content import Content
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
)


class ContentService:

    # =====================================================
    # Create Content
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        request: ContentCreate,
    ):

        content = Content(

            user_id=user_id,

            project_id=request.project_id,

            title=request.title,

            hook=request.hook,

            script=request.script,

            caption=request.caption,

            hashtags=request.hashtags,

            keywords=request.keywords,

            cta=request.cta,

            platform=request.platform,

            content_type=request.content_type,

            language=request.language,

            ai_provider=request.ai_provider,

            ai_model=request.ai_model,

            prompt=request.prompt,

            status="generated",

        )

        db.add(content)

        db.commit()

        db.refresh(content)

        return {
            "success": True,
            "message": "Content created successfully.",
            "content": content,
        }

    # =====================================================
    # Get All Contents
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        contents = (

            db.query(Content)

            .filter(Content.user_id == user_id)

            .order_by(Content.created_at.desc())

            .all()

        )

        return {
            "success": True,
            "total": len(contents),
            "contents": contents,
        }

    # =====================================================
    # Get Single Content
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        content = (

            db.query(Content)

            .filter(

                Content.id == content_id,

                Content.user_id == user_id,

            )

            .first()

        )

        if not content:

            return {
                "success": False,
                "message": "Content not found.",
            }

        return {
            "success": True,
            "content": content,
        }

    # =====================================================
    # Get Contents By Project
    # =====================================================

    @staticmethod
    def get_project_contents(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        contents = (

            db.query(Content)

            .filter(

                Content.project_id == project_id,

                Content.user_id == user_id,

            )

            .order_by(Content.created_at.desc())

            .all()

        )

        return {
            "success": True,
            "total": len(contents),
            "contents": contents,
        }

    # =====================================================
    # Update Content
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        content_id: int,
        user_id: int,
        request: ContentUpdate,
    ):

        content = (

            db.query(Content)

            .filter(

                Content.id == content_id,

                Content.user_id == user_id,

            )

            .first()

        )

        if not content:

            return {
                "success": False,
                "message": "Content not found.",
            }

        update_data = request.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        for key, value in update_data.items():
            setattr(content, key, value)

        db.commit()

        db.refresh(content)

        return {
            "success": True,
            "message": "Content updated successfully.",
            "content": content,
        }

    # =====================================================
    # Delete Content
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        content = (

            db.query(Content)

            .filter(

                Content.id == content_id,

                Content.user_id == user_id,

            )

            .first()

        )

        if not content:

            return {
                "success": False,
                "message": "Content not found.",
            }

        db.delete(content)

        db.commit()

        return {
            "success": True,
            "message": "Content deleted successfully.",
        }

    # =====================================================
    # Generate Caption
    # =====================================================

    @staticmethod
    def generate_caption(
        trend: dict,
        script: dict,
    ):

        return (
            f"{trend.get('title', '')}\n\n"
            f"{script.get('hook', '')}\n\n"
            "#ViralForgeAI"
        )

    # =====================================================
    # Generate Hashtags
    # =====================================================

    @staticmethod
    def generate_hashtags(
        category: str,
    ):

        mapping = {

            "AI": [
                "#AI",
                "#ArtificialIntelligence",
                "#FutureTech",
            ],

            "Finance": [
                "#Finance",
                "#Investment",
                "#Money",
            ],

            "Psychology": [
                "#Psychology",
                "#HumanBehavior",
            ],

            "Technology": [
                "#Technology",
                "#Innovation",
            ],

            "Entertainment": [
                "#Entertainment",
                "#Trending",
            ],

        }

        return mapping.get(

            category,

            [
                "#Trending",
                "#Viral",
            ],

        )
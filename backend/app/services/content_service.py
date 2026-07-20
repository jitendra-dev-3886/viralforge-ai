from sqlalchemy.orm import Session

from app.models.content import Content
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
)


class ContentService:

    # ==========================================================
    # Create Content
    # ==========================================================

    @staticmethod
    def create(
        db: Session,
        request: ContentCreate,
    ):

        content = Content(

            user_id=request.user_id,

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

    # ==========================================================
    # Get All Contents
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        return (
            db.query(Content)
            .filter(Content.user_id == user_id)
            .order_by(Content.created_at.desc())
            .all()
        )

    # ==========================================================
    # Get By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        return (
            db.query(Content)
            .filter(
                Content.id == content_id,
                Content.user_id == user_id,
            )
            .first()
        )

    # ==========================================================
    # Get Project Contents
    # ==========================================================

    @staticmethod
    def get_project_contents(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        return (
            db.query(Content)
            .filter(
                Content.project_id == project_id,
                Content.user_id == user_id,
            )
            .order_by(Content.created_at.desc())
            .all()
        )

    # ==========================================================
    # Update Content
    # ==========================================================

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

        if request.title is not None:
            content.title = request.title

        if request.hook is not None:
            content.hook = request.hook

        if request.script is not None:
            content.script = request.script

        if request.caption is not None:
            content.caption = request.caption

        if request.hashtags is not None:
            content.hashtags = request.hashtags

        if request.keywords is not None:
            content.keywords = request.keywords

        if request.cta is not None:
            content.cta = request.cta

        if request.status is not None:
            content.status = request.status

        db.commit()

        db.refresh(content)

        return {
            "success": True,
            "message": "Content updated successfully.",
            "content": content,
        }

    # ==========================================================
    # Delete Content
    # ==========================================================

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

    # ==========================================================
    # Caption Generator
    # ==========================================================

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

    # ==========================================================
    # Hashtag Generator
    # ==========================================================

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
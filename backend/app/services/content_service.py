from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.content import Content
from app.models.scene import Scene
from app.core.brand_credit import output_brand_name
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
)


class ContentService:

    @staticmethod
    def _serialize(content: Content):
        config = content.generation_config or {}
        return {
            "id": content.id, "content_id": content.id,
            "user_id": content.user_id, "project_id": content.project_id,
            "project_title": content.project.title if content.project else "",
            "title": content.title, "hook": content.hook,
            "description": config.get("description", ""),
            "prompt": content.prompt, "script": content.script,
            "caption": content.caption,
            "hashtags": content.hashtags.split(",") if content.hashtags else [],
            "keywords": content.keywords.split(",") if content.keywords else [],
            "cta": content.cta, "platform": content.platform,
            "content_type": content.content_type, "language": content.language,
            "ai_provider": content.ai_provider, "ai_model": content.ai_model,
            "status": content.status, "generation_config": config,
            "branding": {**(config.get("branding") or {}), "brand_name": output_brand_name(content)},
            "story": config.get("story") or (content.script if "carousel" in (content.content_type or "").lower() else ""),
            "created_at": content.created_at, "updated_at": content.updated_at,
            "scenes": [{
                "id": scene.id, "scene": scene.scene_number, "title": scene.title,
                "text": scene.text, "voice_text": scene.voice_text, "keyword": scene.keyword,
                "image_prompt": scene.image_prompt, "video_prompt": scene.video_prompt,
                "media_type": scene.media_type, "duration": scene.duration,
                "status": scene.status, "media_id": scene.media_id,
                "media_url": scene.media.file_url if scene.media else None,
                "media_provider": scene.media.provider if scene.media else None,
            } for scene in sorted(content.scenes, key=lambda item: item.scene_number)],
        }

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
        project_id: int | None = None,
        platform: str | None = None,
        content_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ):
        query = db.query(Content).options(
            selectinload(Content.scenes).selectinload(Scene.media),
            selectinload(Content.project),
        ).filter(Content.user_id == user_id)
        if project_id is not None:
            query = query.filter(Content.project_id == project_id)
        if platform:
            query = query.filter(Content.platform.ilike(f"%{platform}%"))
        if content_type:
            query = query.filter(Content.content_type.ilike(f"%{content_type}%"))
        if status:
            query = query.filter(Content.status == status)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(or_(Content.title.ilike(term), Content.caption.ilike(term)))
        contents = query.order_by(Content.created_at.desc()).all()

        return {
            "success": True,
            "total": len(contents),
            "contents": [ContentService._serialize(content) for content in contents],
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

            db.query(Content).options(
                selectinload(Content.scenes).selectinload(Scene.media),
                selectinload(Content.project),
            )

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
            "content": ContentService._serialize(content),
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

            db.query(Content).options(
                selectinload(Content.scenes).selectinload(Scene.media),
                selectinload(Content.project),
            )

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
            "contents": [ContentService._serialize(content) for content in contents],
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

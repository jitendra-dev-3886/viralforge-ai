import json
import logging
import traceback

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.ai import GenerateRequest

from app.models.project import Project
from app.models.content import Content

from app.services.prompt_engine import PromptEngine
from app.services.scene_service import SceneService

from app.core.gemini_client import GeminiClient
from app.core.groq_client import groq_client


logger = logging.getLogger(__name__)


class AIService:

    @staticmethod
    def generate(
        request: GenerateRequest,
        db: Session,
    ):

        try:

            # =====================================================
            # Find Project
            # =====================================================

            project = (
                db.query(Project)
                .filter(Project.id == request.project_id)
                .first()
            )

            if not project:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found."
                )

            # =====================================================
            # Build Prompt
            # =====================================================

            prompt = PromptEngine.build(request)

            logger.info("=" * 80)
            logger.info(prompt)
            logger.info("=" * 80)

            # =====================================================
            # Select AI Provider
            # =====================================================

            provider = request.provider.lower()

            if provider == "gemini":

                try:

                    ai_text = GeminiClient.generate(prompt)

                    model = "gemini-2.5-flash"

                except Exception as e:

                    logger.warning(
                        f"Gemini failed : {e}"
                    )

                    logger.info(
                        "Switching to Groq..."
                    )

                    ai_text = groq_client.generate(prompt)

                    provider = "groq"

                    model = "llama-3.3-70b-versatile"

            elif provider == "groq":

                ai_text = groq_client.generate(prompt)

                model = "llama-3.3-70b-versatile"

            else:

                raise HTTPException(
                    status_code=400,
                    detail="Unsupported AI Provider."
                )

            logger.info("AI Response Received")

            # =====================================================
            # Parse JSON
            # =====================================================

            try:

                ai_data = json.loads(ai_text)

                # ==========================================
                # Normalize AI Response
                # ==========================================

                if "script" not in ai_data:
                    ai_data["script"] = ai_data.get("description", "")

                if "keywords" not in ai_data:
                    ai_data["keywords"] = ai_data.get("seo_keywords", [])

                if "hashtags" not in ai_data:
                    ai_data["hashtags"] = []

                if "hook" not in ai_data:
                    ai_data["hook"] = ""

                if "caption" not in ai_data:
                    ai_data["caption"] = ""

                if "cta" not in ai_data:
                    ai_data["cta"] = ""

            except Exception:

                logger.error("Invalid JSON returned by AI")

                raise HTTPException(
                    status_code=500,
                    detail="AI returned invalid JSON."
                )

            # =====================================================
            # Validate Required Fields
            # =====================================================

            required_fields = [

                "title",

                "script",

                "caption",

            ]

            for field in required_fields:

                if not ai_data.get(field):

                    raise HTTPException(
                        status_code=500,
                        detail=f"AI response missing '{field}'"
                    )
                # =====================================================
            # Normalize AI Response
            # =====================================================

            hashtags = ai_data.get("hashtags", [])

            if isinstance(hashtags, list):
                hashtags = ",".join(hashtags)

            elif hashtags is None:
                hashtags = ""

            keywords = ai_data.get("keywords", [])

            if isinstance(keywords, list):
                keywords = ",".join(keywords)

            elif keywords is None:
                keywords = ""

            # =====================================================
            # Save Content
            # =====================================================

            content = Content(

                user_id=project.user_id,

                project_id=project.id,

                title=ai_data.get(
                    "title",
                    request.topic,
                ),

                hook=ai_data.get(
                    "hook",
                ),

                script=ai_data.get(
                    "script",
                ),

                caption=ai_data.get(
                    "caption",
                ),

                hashtags=hashtags,

                keywords=keywords,

                cta=ai_data.get(
                    "cta",
                ),

                platform=",".join(
                    request.platforms
                ),

                content_type=",".join(
                    request.content_types
                ),

                language=request.language,

                ai_provider=provider,

                ai_model=model,

                prompt=prompt,

                status="generated",

            )

            db.add(content)

            # Get content.id before scene generation
            db.flush()

            logger.info(
                f"Content Created : {content.id}"
            )

            # =====================================================
            # Generate Scenes
            # =====================================================

            SceneService.generate(

                db=db,

                project_id=project.id,

                content_id=content.id,

                ai_data=ai_data,

            )

            db.commit()

            db.refresh(content)
                # =====================================================
            # Success Response
            # =====================================================

            return {

                "success": True,

                "provider": provider,

                "content_id": content.id,

                "data": {

                    "title": content.title,

                    "hook": content.hook,

                    "script": content.script,

                    "caption": content.caption,

                    "hashtags": (
                        content.hashtags.split(",")
                        if content.hashtags
                        else []
                    ),

                    "keywords": (
                        content.keywords.split(",")
                        if content.keywords
                        else []
                    ),

                    "cta": content.cta,

                },

            }

        # =====================================================
        # HTTP Exceptions
        # =====================================================

        except HTTPException:

            db.rollback()

            raise

        # =====================================================
        # Unexpected Exceptions
        # =====================================================

        except Exception as e:

            db.rollback()

            logger.exception(
                "AI Generation Failed"
            )

            traceback.print_exc()

            raise HTTPException(

                status_code=500,

                detail=str(e),

            )
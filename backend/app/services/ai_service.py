import json
import os
import logging
import re
import traceback

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.ai import GenerateRequest

from app.models.project import Project
from app.models.content import Content

from app.services.prompt_engine import PromptEngine
from app.services.scene_service import SceneService
from app.services.downloader_service import DownloaderService

from app.core.gemini_client import GeminiClient
from app.core.groq_client import groq_client
from app.core.localai_client import localai_client
from app.core.llama_cpp_client import llama_cpp_client


logger = logging.getLogger(__name__)


class AIService:

    @staticmethod
    def _parse_json_response(ai_text: str) -> dict:
        """Parse a JSON object even when a model adds harmless surrounding text."""
        if not isinstance(ai_text, str) or not ai_text.strip():
            raise ValueError("AI response was empty")

        response_text = ai_text.strip().lstrip("\ufeff")
        candidates = [response_text]

        # Smaller/local models often return a fenced JSON block despite the
        # prompt's instruction not to. Prefer the fenced body when present.
        candidates.extend(
            match.strip()
            for match in re.findall(
                r"```(?:json)?\s*(.*?)```",
                response_text,
                flags=re.IGNORECASE | re.DOTALL,
            )
        )

        decoder = json.JSONDecoder()
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

            # Accept an otherwise-valid JSON object preceded or followed by a
            # short model explanation, without attempting unsafe JSON repair.
            for start in (match.start() for match in re.finditer(r"\{", candidate)):
                try:
                    parsed, _ = decoder.raw_decode(candidate[start:])
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue

        raise ValueError("No valid JSON object found in AI response")

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
            # Select AI Provider(s) in priority order
            # =====================================================

            # Build providers priority list: explicit request.providers > request.provider (or auto).
            # Local providers are only attempted in auto mode when explicitly
            # configured, avoiding misleading connection/model errors.
            if request.providers:
                providers_list = [str(p).lower() for p in request.providers if p]
            else:
                reqp = (request.provider or "auto").lower()
                if reqp == "auto":
                    providers_list = []
                    if os.getenv("GEMINI_API_KEY"):
                        providers_list.append("gemini")
                    if os.getenv("GROQ_API_KEY"):
                        providers_list.append("groq")
                    if os.getenv("LOCALAI_URL"):
                        providers_list.append("localai")
                    if os.getenv("LLAMA_CPP_MODEL_PATH"):
                        providers_list.append("llama_cpp")
                else:
                    providers_list = [reqp]

            ai_text = None
            model = None
            used_provider = None
            errors = []

            for p in providers_list:
                try:
                    if p == "gemini":
                        ai_text = GeminiClient.generate(prompt)
                        model = "gemini-2.5-flash"

                    elif p == "groq":
                        ai_text = groq_client.generate(prompt)
                        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

                    elif p == "localai":
                        ai_text = localai_client.generate(prompt)
                        model = os.getenv("LOCALAI_MODEL", "local-model")

                    elif p in ("llama_cpp", "llamacpp"):
                        ai_text = llama_cpp_client.generate(prompt)
                        model = os.getenv("LLAMA_CPP_MODEL_PATH", "local-llama-cpp")

                    else:
                        raise Exception(f"Unsupported provider: {p}")

                    used_provider = p
                    provider = p
                    break

                except Exception as e:
                    logger.warning(f"Provider {p} failed: {e}")
                    errors.append(f"{p}: {str(e)}")
                    continue

            if not ai_text:
                logger.error(f"All providers failed: {errors}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "code": "ai_providers_unavailable",
                        "message": (
                            "No configured AI provider is currently available. "
                            "Groq may be rate-limited; try again shortly or select Gemini."
                        ),
                    },
                )

            logger.info("AI Response Received")

            # =====================================================
            # Parse JSON
            # =====================================================

            try:

                ai_data = AIService._parse_json_response(ai_text)

                # ==========================================
                # Normalize AI Response
                # ==========================================

                if "script" not in ai_data:
                    ai_data["script"] = ai_data.get("description", "")

                if "keywords" not in ai_data or ai_data["keywords"] is None:
                    ai_data["keywords"] = ai_data.get("seo_keywords", [])

                if "hashtags" not in ai_data or ai_data["hashtags"] is None:
                    ai_data["hashtags"] = []

                if "hook" not in ai_data:
                    ai_data["hook"] = ""

                if "description" not in ai_data:
                    ai_data["description"] = ""

                if "caption" not in ai_data:
                    ai_data["caption"] = ""

                if "cta" not in ai_data:
                    ai_data["cta"] = ""

                if "story" not in ai_data:
                    ai_data["story"] = ai_data.get("description", "")

                if isinstance(ai_data.get("keywords"), str):
                    ai_data["keywords"] = [
                        tag.strip()
                        for tag in re.split(r"[\s,\n]+", ai_data["keywords"])
                        if tag.strip()
                    ]

                if isinstance(ai_data.get("hashtags"), str):
                    ai_data["hashtags"] = [
                        tag.strip()
                        for tag in re.split(r"[\s,\n]+", ai_data["hashtags"])
                        if tag.strip()
                    ]

                elif isinstance(ai_data["hashtags"], list):
                    ai_data["hashtags"] = [
                        str(tag).strip()
                        for tag in ai_data["hashtags"]
                        if str(tag).strip()
                    ]

            except Exception as exc:

                logger.warning("Invalid JSON returned by AI: %s", exc)

                raise HTTPException(
                    status_code=500,
                    detail="AI returned invalid JSON."
                )

            # =====================================================
            # =====================================================
            # Detect nested multi-output responses and normalize scenes for the selected output.

            def extract_first_output(data):
                if not isinstance(data, dict):
                    return {}

                if data.get("title") or data.get("script") or data.get("caption") or data.get("voiceover"):
                    return data

                for platform_value in data.values():
                    if isinstance(platform_value, dict):
                        for output_item in platform_value.values():
                            if isinstance(output_item, dict):
                                if output_item.get("title") or output_item.get("script") or output_item.get("caption"):
                                    return output_item

                return {}

            output_data = extract_first_output(ai_data)
            scenes = (output_data.get("scenes") or []) if output_data else []

            def ensure_search_fields(scene_item):

                # Normalize keys
                media_type = (scene_item.get("media_type") or "image").lower()

                # If the whole request package is carousel or content types include Carousel, force image
                try:
                    requested_package = (request.package or "").lower()
                except Exception:
                    requested_package = ""

                if requested_package == "carousel":
                    media_type = "image"

                # image_prompt fallback
                image_prompt = scene_item.get("image_prompt") or ""
                video_prompt = scene_item.get("video_prompt") or ""
                keyword = scene_item.get("keyword") or ""

                # If keyword missing, prefer image_prompt then video_prompt then derive from text
                if not keyword:
                    if image_prompt:
                        keyword = image_prompt
                    elif video_prompt:
                        keyword = video_prompt
                    else:
                        # derive a short keyword from scene text
                        txt = scene_item.get("text") or ""
                        keyword = " ".join(txt.split()[:5]).strip() or "stock photo"

                if requested_package == "carousel":
                    media_type = "image"

                if not image_prompt:
                    image_prompt = keyword

                if not video_prompt:
                    video_prompt = image_prompt

                # If image_prompt missing, set to keyword
                if not image_prompt:
                    image_prompt = keyword

                scene_item["media_type"] = media_type
                scene_item["keyword"] = keyword
                scene_item["image_prompt"] = image_prompt
                scene_item["video_prompt"] = video_prompt

                return scene_item

            normalized_scenes = [ensure_search_fields(s) for s in scenes]

            if output_data is ai_data:
                ai_data["scenes"] = normalized_scenes
            else:
                output_data["scenes"] = normalized_scenes

            # Enforce carousel formatting rules after AI normalization
            if request.package and request.package.lower() == "carousel":
                carousel_scenes = [
                    scene
                    for scene in normalized_scenes
                    if (scene.get("media_type") or "image").lower() == "image"
                ]

                if len(carousel_scenes) > 8:
                    carousel_scenes = carousel_scenes[:8]

                if output_data is ai_data:
                    ai_data["scenes"] = carousel_scenes
                else:
                    output_data["scenes"] = carousel_scenes

            # Generate a short carousel story if missing
            if request.package and request.package.lower() == "carousel":
                target_story = ai_data if output_data is ai_data else output_data
                if not target_story.get("story"):
                    scene_texts = [
                        str(scene.get("text", "")).strip()
                        for scene in (target_story.get("scenes") or [])
                        if scene.get("text")
                    ]
                    if scene_texts:
                        target_story["story"] = " ".join(scene_texts[:8])
                    else:
                        target_story["story"] = target_story.get("description", "")

                if len(target_story.get("scenes") or []) < 3:
                    raise HTTPException(
                        status_code=500,
                        detail="Carousel output must contain at least 3 image scenes."
                    )

            # =====================================================
            # Validate Required Fields
            # =====================================================

            validation_source = output_data if output_data else ai_data

            if validation_source is ai_data:
                required_fields = [
                    "title",
                    "script",
                    "caption",
                ]

                for field in required_fields:
                    if not validation_source.get(field):
                        raise HTTPException(
                            status_code=500,
                            detail=f"AI response missing '{field}'"
                        )

            # =====================================================
            # Normalize AI Response
            # =====================================================

            hashtags = output_data.get("hashtags", []) if output_data else ai_data.get("hashtags", [])

            if isinstance(hashtags, list):
                hashtags = ",".join(hashtags)

            elif hashtags is None:
                hashtags = ""

            keywords = output_data.get("keywords", []) if output_data else ai_data.get("keywords", [])

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

                title=(output_data or ai_data).get(
                    "title",
                    request.topic,
                ),

                hook=(output_data or ai_data).get(
                    "hook",
                ),

                script=(output_data or ai_data).get(
                    "script",
                    request.topic,
                ) or request.topic,

                caption=(output_data or ai_data).get(
                    "caption",
                ),

                hashtags=hashtags,

                keywords=keywords,

                cta=(output_data or ai_data).get(
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

            scenes_result = SceneService.generate(

                db=db,

                project_id=project.id,

                content_id=content.id,

                user_id=project.user_id,

                ai_data={"scenes": output_data.get("scenes", [])},
                package=request.package,

            )

            # Attempt to download image media for generated scenes automatically.
            for scene in scenes_result.get("scenes", []):
                try:
                    if (scene.media_type or "").lower() == "image":
                        DownloaderService.download(
                            db=db,
                            scene_id=scene.id,
                        )
                except Exception as e:
                    logger.warning(
                        f"Image download failed for scene {scene.id}: {str(e)}"
                    )
                    continue

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

                    "description": ai_data.get("description", ""),

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

                    "scenes": [
                        {
                            "scene": item.get("scene_number") or item.get("scene"),
                            "title": item.get("title"),
                            "text": item.get("text"),
                            "keyword": item.get("keyword"),
                            "image_prompt": item.get("image_prompt"),
                            "video_prompt": item.get("video_prompt"),
                            "media_type": item.get("media_type"),
                            "duration": item.get("duration"),
                            "platform": item.get("platform"),
                        }
                        for item in ai_data.get("scenes", [])
                    ],

                },

            }

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

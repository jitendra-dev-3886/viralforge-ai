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

from app.services.user_ai_settings import credentials_for
from app.core.user_ai_client import generate_user_content




logger = logging.getLogger(__name__)


class AIService:

    @staticmethod
    def _provider_failure(errors):
        """Expose actionable categories without leaking provider credentials/bodies."""
        if not errors:
            return HTTPException(status_code=503, detail={"code": "ai_not_configured", "message": "No AI provider is configured. Configure a provider or select one in the Brief step."})
        if len(errors) > 1:
            failures = [AIService._provider_failure([item]) for item in errors]
            return HTTPException(status_code=502, detail={
                "code": "ai_all_providers_failed",
                "message": "No configured provider completed generation. " + " ".join(item.detail["message"] for item in failures),
                "providers": [item.detail for item in failures],
            })
        provider, error = errors[-1]
        status = getattr(error, "status_code", None) or getattr(getattr(error, "response", None), "status_code", None)
        message = str(error).lower()
        if getattr(error, "access_reason", None) == "project_model_blocked":
            code, text, http = "ai_project_model_blocked", "has this model blocked in your Groq project. A project admin must enable it at https://console.groq.com/settings/project/limits before generation can work.", 503
        elif getattr(error, "access_reason", None) == "model_unavailable_new_users":
            code, text, http = "ai_model_unavailable", "no longer offers this model to new users. Select a current text model in Settings > My AI providers and test it before generating.", 503
        elif getattr(error, "credential_role", None) == "management":
            code, text, http = "ai_wrong_key_type", "uses a management/provisioning key, which cannot generate content. Create a regular API key at https://openrouter.ai/settings/keys, save it in Settings > My AI providers, then test again.", 503
        elif status == 429 or any(word in message for word in ("429", "quota", "rate limit", "resource_exhausted")):
            code, text, http = "ai_rate_limit", "has reached its rate or usage limit. Wait and retry, or select another configured provider.", 429
        elif status == 403:
            code, text, http = "ai_access_denied", "denied this request (HTTP 403). Check model permissions, account or region restrictions, and provider access policies. This does not necessarily mean your key is invalid.", 503
        elif status == 402:
            code, text, http = "ai_credits_required", "requires credits or billing access (HTTP 402). Check your provider balance and selected model.", 503
        elif status == 401 or any(word in message for word in ("api key", "api_key", "unauthorized", "authentication")):
            code, text, http = "ai_credentials", "rejected authentication. In Settings > My AI providers, replace its key with an API key issued by this provider, save, then test again.", 503
        elif status in (400, 422):
            code, text, http = "ai_request_rejected", "rejected the model or request options. Check the exact model ID and whether it supports chat completions with JSON output.", 502
        elif status == 404 or any(word in message for word in ("model_not_found", "model not found", "decommissioned", "does not exist")):
            code, text, http = "ai_model_unavailable", "could not access its configured model. Check the model name and account access.", 503
        elif any(word in message for word in ("timeout", "timed out", "connection", "connect", "unreachable")):
            code, text, http = "ai_unavailable", "could not be reached. Check the connection or choose another configured provider.", 503
            if provider == "ollama":
                text = "could not be reached. Start Ollama on the backend machine and check OLLAMA_URL, or select a configured cloud provider in Brief."
        elif isinstance(error, ValueError):
            code, text, http = "ai_invalid_response", "returned invalid or incomplete JSON after an automatic retry. Try fewer scenes or another configured provider.", 502
        else:
            code, text, http = "ai_provider_failed", "could not complete generation. Try another configured provider or check the backend provider logs.", 502
        return HTTPException(status_code=http, detail={"code": code, "message": f"{provider}: {text}", "provider_status": status})

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

        # A trailing comma is a common harmless JSON-mode failure. Remove it
        # before a closing object/array without touching the generated text.
        candidates.extend(
            re.sub(r",\s*([}\]])", r"\1", candidate)
            for candidate in list(candidates)
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
            start = candidate.find("{")
            if start >= 0:
                try:
                    parsed, _ = decoder.raw_decode(candidate[start:])
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue

        raise ValueError("No valid JSON object found in AI response")

    @staticmethod
    def _generate_validated_response(provider, request, prompt, credentials=None):
        for attempt in range(2):
            try:
                text, model = AIService._generate_from_provider(provider, prompt if attempt == 0 else PromptEngine.build_json_retry(request), **({"credentials": credentials} if credentials is not None else {}))
                data = AIService._parse_json_response(text)
                candidates = [data]
                for value in data.values():
                    if isinstance(value, dict):
                        candidates.extend(item for item in value.values() if isinstance(item, dict))
                if not any(any(isinstance(item.get(field), str) and item[field].strip() for field in ("title", "script", "caption", "description")) for item in candidates):
                    raise ValueError("Response contains no usable content")
                return text, model, data
            except ValueError:
                if attempt:
                    raise
                logger.warning("Provider %s returned unusable content; retrying once", provider)

    @staticmethod
    def _requested_outputs(request: GenerateRequest) -> list[dict[str, str]]:
        """Return the exact platform/format pairs chosen in the UI."""
        pairs: list[dict[str, str]] = []

        for output in request.outputs or []:
            platform, separator, content_type = str(output).partition(":")
            if separator and platform.strip() and content_type.strip():
                pairs.append(
                    {
                        "platform": platform.strip(),
                        "content_type": content_type.strip(),
                    }
                )

        if not pairs:
            pairs = [
                {"platform": platform, "content_type": content_type}
                for platform in request.platforms
                for content_type in request.content_types
            ]

        unique_pairs = []
        seen = set()
        for pair in pairs:
            key = (pair["platform"].lower(), pair["content_type"].lower())
            if key not in seen:
                seen.add(key)
                unique_pairs.append(pair)
        return unique_pairs

    @staticmethod
    def _response_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

    @staticmethod
    def _format_media_type(content_types: list[str], fallback: str) -> str:
        format_name = " ".join(content_types).lower()
        if any(value in format_name for value in ("reel", "short", "story", "long video")):
            return "video"
        if any(value in format_name for value in ("carousel", "post", "quote", "community")):
            return "image"
        return "video" if fallback == "video" else "image"

    @staticmethod
    def _generate_from_provider(provider: str, prompt: str, credentials=None) -> tuple[str, str]:
        if credentials is None:
            raise ValueError("User API credentials are required")
        return generate_user_content(provider, prompt, credentials)

    @staticmethod
    def generate(
        request: GenerateRequest,
        db: Session,
        user_id: int,
    ):

        try:

            requested_outputs = AIService._requested_outputs(request)

            # Each selected platform/format gets its own focused AI request.
            # This is much more reliable than asking a model to blend several
            # formats into one response and then silently keeping the first.
            if len(requested_outputs) > 1:
                combined_data = {}
                results = []

                for output in requested_outputs:
                    focused_request = request.model_copy(
                        update={
                            "platforms": [output["platform"]],
                            "content_types": [output["content_type"]],
                            "outputs": [
                                f"{output['platform']}: {output['content_type']}"
                            ],
                        }
                    )
                    result = AIService.generate(focused_request, db, user_id)
                    results.append(result)

                    platform_key = AIService._response_key(output["platform"])
                    content_type_key = AIService._response_key(output["content_type"])
                    result_data = dict(result["data"])
                    result_data["content_id"] = result["content_id"]
                    combined_data.setdefault(platform_key, {})[content_type_key] = result_data

                return {
                    "success": True,
                    "provider": results[0]["provider"],
                    "content_id": results[0]["content_id"],
                    "data": combined_data,
                }

            # Keep direct API calls with a single output just as focused as the
            # UI flow, even if their platform/content-type arrays contain extras.
            if requested_outputs:
                request = request.model_copy(
                    update={
                        "platforms": [requested_outputs[0]["platform"]],
                        "content_types": [requested_outputs[0]["content_type"]],
                    }
                )

            # =====================================================
            # Find Project
            # =====================================================

            project = (
                db.query(Project)
                .filter(
                    Project.id == request.project_id,
                    Project.user_id == user_id,
                )
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

            requested = [str(p).lower() for p in request.providers if p] if request.providers else None
            if not requested and (request.provider or "auto").lower() != "auto":
                requested = [(request.provider or "auto").lower()]
            user_credentials = credentials_for(db, user_id, requested)
            providers_list = requested or list(user_credentials)
            from app.services.billing_service import require_plan
            require_plan(db, user_id)
            db.commit()

            ai_text = None
            ai_data = None
            model = None
            used_provider = None
            errors = []

            for p in providers_list:
                try:
                    ai_text, model, ai_data = AIService._generate_validated_response(p, request, prompt, credentials=user_credentials[p])

                    used_provider = p
                    provider = p
                    break

                except Exception as e:
                    logger.warning("Provider %s failed (%s)", p, type(e).__name__)
                    errors.append((p, e))
                    ai_data = None
                    continue

            if not ai_text or ai_data is None:
                logger.error("All user-configured providers failed: %s", providers_list)
                raise AIService._provider_failure(errors)


            logger.info("AI Response Received")

            # =====================================================
            # Parse JSON
            # =====================================================

            try:

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
            selected_format = " ".join(request.content_types).lower()
            is_carousel_output = "carousel" in selected_format

            def ensure_search_fields(scene_item):

                # Normalize keys
                media_type = (scene_item.get("media_type") or "image").lower()
                media_type = AIService._format_media_type(
                    request.content_types,
                    media_type,
                )

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
            if is_carousel_output:
                carousel_scenes = [
                    scene
                    for scene in normalized_scenes
                    if (scene.get("media_type") or "image").lower() == "image"
                ]

                if len(carousel_scenes) > 8:
                    carousel_scenes = carousel_scenes[:8]

                # Some providers occasionally ignore the requested scene count.
                # Keep carousel generation usable by constructing meaningful
                # cover/value/CTA slides from the response instead of failing.
                fallback_texts = [
                    (output_data or ai_data).get("hook"),
                    (output_data or ai_data).get("title"),
                    (output_data or ai_data).get("description") or (output_data or ai_data).get("script"),
                    (output_data or ai_data).get("cta"),
                ]
                for fallback_text in fallback_texts:
                    if len(carousel_scenes) >= 3:
                        break
                    text = re.sub(r"\s+", " ", str(fallback_text or "")).strip()
                    if not text or any(text == str(item.get("text", "")).strip() for item in carousel_scenes):
                        continue
                    keyword = " ".join(text.split()[:5]) or "inspirational lifestyle"
                    carousel_scenes.append({
                        "scene": len(carousel_scenes) + 1,
                        "text": text,
                        "keyword": keyword,
                        "image_prompt": keyword,
                        "video_prompt": keyword,
                        "duration": 5,
                        "media_type": "image",
                        "platform": request.platforms[0],
                    })

                while carousel_scenes and len(carousel_scenes) < 3:
                    source = carousel_scenes[-1]
                    carousel_scenes.append({
                        **source,
                        "scene": len(carousel_scenes) + 1,
                    })

                if output_data is ai_data:
                    ai_data["scenes"] = carousel_scenes
                else:
                    output_data["scenes"] = carousel_scenes

            # Generate a short carousel story if missing
            if is_carousel_output:
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
                        detail="The AI provider returned no usable carousel image scenes. Please generate again."
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

                generation_config={
                    "package": request.package,
                    "provider": request.provider,
                    "platforms": request.platforms,
                    "content_types": request.content_types,
                    "outputs": request.outputs,
                    "niche": request.niche,
                    "topic": request.topic,
                    "scene_count": request.scene_count,
                    "total_duration": request.total_duration,
                    "style": request.style,
                    "visual_style": request.visual_style,
                    "description": (output_data or ai_data).get("description", ""),
                    "story": (output_data or ai_data).get("story", ""),
                    "branding": {
                        "username": project.user.name if project.user else "",
                        "brand_name": project.brand.name if project.brand else "",
                        "logo": project.brand.logo if project.brand else "",
                        "primary_color": project.brand.primary_color if project.brand else None,
                        "secondary_color": project.brand.secondary_color if project.brand else None,
                        "font": project.brand.font if project.brand else None,
                    },
                },

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
                package="carousel" if is_carousel_output else "",

            )

            # Download the selected kind of stock media for every scene. Video
            # scenes used to be skipped here, which left Reels and Shorts with
            # no usable clips.
            downloaded_media = {}
            for scene in scenes_result.get("scenes", []):
                try:
                    if (scene.media_type or "").lower() in {"image", "video"}:
                        media = DownloaderService.download(
                            db=db,
                            scene_id=scene.id,
                            user_id=project.user_id,
                        )
                        downloaded_media[scene.scene_number] = media
                except Exception as e:
                    logger.warning(
                        f"Media download failed for scene {scene.id}: {str(e)}"
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

                "branding": content.generation_config.get("branding", {}),

                "data": {

                    "title": content.title,

                    "hook": content.hook,

                    "description": (output_data or ai_data).get("description", ""),

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

                    "content_id": content.id,

                    "project_id": content.project_id,

                    "platform": content.platform,

                    "content_type": content.content_type,

                    "branding": content.generation_config.get("branding", {}),

                    "generation_config": content.generation_config,

                    "scenes": [
                        {
                            "id": next((scene.id for scene in scenes_result.get("scenes", []) if scene.scene_number == (item.get("scene_number") or item.get("scene"))), None),
                            "scene": item.get("scene_number") or item.get("scene"),
                            "title": item.get("title"),
                            "text": item.get("text"),
                            "keyword": item.get("keyword"),
                            "image_prompt": item.get("image_prompt"),
                            "video_prompt": item.get("video_prompt"),
                            "media_type": item.get("media_type"),
                            "duration": item.get("duration"),
                            "platform": item.get("platform"),
                            "media_url": downloaded_media.get(
                                item.get("scene_number") or item.get("scene"),
                                {},
                            ).get("file_url"),
                            "media_provider": downloaded_media.get(
                                item.get("scene_number") or item.get("scene"),
                                {},
                            ).get("provider"),
                            "media_id": downloaded_media.get(
                                item.get("scene_number") or item.get("scene"),
                                {},
                            ).get("media_id"),
                        }
                        for item in (output_data or ai_data).get("scenes", [])
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

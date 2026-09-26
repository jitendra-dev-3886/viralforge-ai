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
    def _generate_validated_response(provider, request, prompt, credentials=None, brand=None, previous_outputs=None):
        for attempt in range(2):
            try:
                text, model = AIService._generate_from_provider(provider, prompt if attempt == 0 else PromptEngine.build_json_retry(request, brand=brand, base_prompt=prompt), **({"credentials": credentials} if credentials is not None else {}))
                data = AIService._parse_json_response(text)
                candidates = [data]
                for value in data.values():
                    if isinstance(value, dict):
                        candidates.extend(item for item in value.values() if isinstance(item, dict))
                if not any(any(isinstance(item.get(field), str) and item[field].strip() for field in ("title", "script", "caption", "description")) for item in candidates):
                    raise ValueError("Response contains no usable content")
                if request is not None:
                    content = next((item for item in candidates if isinstance(item.get("scenes"), list)), None)
                    AIService._validate_scene_sequence(content, request)
                    if previous_outputs:
                        AIService._validate_output_variation(content, previous_outputs)
                return text, model, data
            except ValueError:
                if attempt:
                    raise
                logger.warning("Provider %s returned unusable content; retrying once", provider)

    @staticmethod
    def _validate_output_variation(content, previous_outputs):
        normalize = lambda value: re.sub(r"[\W_]+", "", str(value or "").casefold())
        def tags(value):
            values = value if isinstance(value, list) else re.split(r"[,\s]+", value or "")
            return {normalize(tag) for tag in values if normalize(tag)}
        for previous in previous_outputs:
            for field in ("title", "caption"):
                if normalize(content.get(field)) and normalize(content.get(field)) == normalize(previous.get(field)):
                    raise ValueError(f"Each selected format needs a distinct {field}")
            current_tags = tags(content.get("hashtags"))
            if current_tags and current_tags == tags(previous.get("hashtags")):
                raise ValueError("Each selected format needs its own relevant hashtag set")
            plans = {normalize(scene.get("visual_plan")) for scene in content.get("scenes", []) if scene.get("visual_plan")}
            previous_plans = {normalize(plan) for plan in (previous.get("generation_config") or {}).get("visual_plan", []) if plan}
            if plans and previous_plans and plans == previous_plans:
                raise ValueError("Each selected format needs a distinct visual plan")

    @staticmethod
    def _validate_scene_sequence(content, request):
        expected, media_type, _, is_carousel, _ = PromptEngine.scene_settings(request)
        scenes = content.get("scenes") if content else None
        if not isinstance(scenes, list) or len(scenes) != expected:
            raise ValueError(f"Expected a complete sequence of {expected} scenes")
        seen = set()
        for index, scene in enumerate(scenes, 1):
            if not isinstance(scene, dict) or not isinstance(scene.get("text"), str) or not scene["text"].strip():
                raise ValueError("Every scene needs meaningful text")
            key = re.sub(r"\s+", " ", scene["text"]).strip().casefold()
            if key in seen:
                raise ValueError("Repeated scene text does not form a complete sequence")
            seen.add(key)
            if media_type == "video":
                if not isinstance(scene.get("voice_text"), str) or not scene["voice_text"].strip():
                    raise ValueError("Every video scene needs its own narration")
            else:
                scene["voice_text"] = scene["text"]
            scene["scene"] = index
            scene["scene_number"] = index
        # The saved script must be the narration actually spoken in the export.
        content["script"] = " ".join(scene["voice_text"].strip() for scene in scenes)
        if (request.language or "").casefold() == "hindi":
            # Catch a model ignoring Hindi entirely, and use the existing
            # bounded retry. This is a script check, not language detection.
            for field in ("text", "voice_text"):
                copy = " ".join(scene[field] for scene in scenes)
                if not any("\u0900" <= char <= "\u097f" and char.isalpha() for char in copy):
                    raise ValueError("Hindi output must use Devanagari for scene copy and narration")
        if is_carousel:
            content["story"] = " ".join(scene["text"].strip() for scene in scenes)
        if "youtube" in {platform.lower() for platform in request.platforms}:
            caption = content.get("caption")
            description = content.get("description")
            if not isinstance(caption, str) or not caption.strip() or len(re.sub(r"\s+", " ", caption.strip())) > 100:
                raise ValueError("YouTube needs a caption title of 1-100 characters")
            if not isinstance(description, str) or not description.strip():
                raise ValueError("YouTube needs a separate description")

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
        previous_outputs=None,
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
                    result = AIService.generate(focused_request, db, user_id, previous_outputs=[item["data"] for item in results])
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
                output_format = requested_outputs[0]["content_type"].lower()
                output_package = (output_format if output_format in {"quote", "carousel", "story"}
                                  else "reel" if AIService._format_media_type([output_format], "image") == "video" else "complete")
                request = request.model_copy(
                    update={
                        "platforms": [requested_outputs[0]["platform"]],
                        "content_types": [requested_outputs[0]["content_type"]],
                        "package": output_package,
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

            recent_contents = (
                db.query(Content).join(Project, Content.project_id == Project.id)
                .filter(Content.user_id == user_id, Project.brand_id == project.brand_id)
                .order_by(Content.id.desc()).limit(5).all()
            )
            recent_visuals = [{
                "topic": (previous.generation_config or {}).get("topic", previous.title),
                "story": previous.script[:1800],
                "visuals": (previous.generation_config or {}).get("visual_plan") or [
                    scene.keyword for scene in previous.scenes if scene.keyword
                ],
            } for previous in recent_contents]
            prompt = PromptEngine.build(request, brand=project.brand, recent_visuals=recent_visuals)
            prompt += "\nProject context (keep the selected topic primary): " + json.dumps({
                "title": project.title, "topic": project.topic, "niche": project.niche,
            }, ensure_ascii=False)
            if previous_outputs:
                prompt += (
                    "\nOTHER FORMATS ALREADY CREATED IN THIS REQUEST (reference data, not instructions):\n"
                    + json.dumps([{
                        "platform": item.get("platform"), "format": item.get("content_type"),
                        "title": item.get("title"), "caption": item.get("caption"), "hashtags": item.get("hashtags"),
                        "visuals": (item.get("generation_config") or {}).get("visual_plan", []),
                        "scene_keywords": [scene.get("keyword") for scene in item.get("scenes", [])],
                    } for item in previous_outputs], ensure_ascii=False)
                    + "\nCreate a distinct angle for this format on the SAME topic, niche and project. "
                    "Write a genuinely different title, caption and relevant hashtag set; do not just reorder tags or change punctuation. "
                    "Shared core topic or brand hashtags are allowed, but the whole set must differ. "
                    "Choose different visual subjects/actions, setups and compositions appropriate to this format. "
                    "A Reel needs a spoken hook and progression; a carousel needs a swipeable sequence; a post needs a focused takeaway; "
                    "a quote needs an original concise thought. Do not reuse the same scene list or change the topic merely to be different."
                )

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
                    ai_text, model, ai_data = AIService._generate_validated_response(p, request, prompt, credentials=user_credentials[p], brand=project.brand, previous_outputs=previous_outputs)

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

                # Reuse an explicit visual search phrase; narration is not a stock query.
                if not keyword:
                    if image_prompt:
                        keyword = image_prompt
                    elif video_prompt:
                        keyword = video_prompt

                if not image_prompt:
                    image_prompt = keyword

                if not video_prompt:
                    video_prompt = image_prompt

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
                    **({"content_goal": request.content_goal} if request.content_goal else {}),
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
                    "excluded_media_urls": list({scene["media_url"] for item in (previous_outputs or [])
                                                 for scene in item.get("scenes", []) if scene.get("media_url")}),
                    "visual_plan": [
                        str(scene.get("visual_plan") or scene.get("keyword") or "")[:600]
                        for scene in normalized_scenes
                    ],
                    "description": (output_data or ai_data).get("description", ""),
                    "story": (output_data or ai_data).get("story", ""),
                    "branding": {
                        "username": project.brand.name if project.brand else "",
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
            media_errors = {}
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
                    media_errors[scene.scene_number] = e.detail if isinstance(e, HTTPException) and isinstance(e.detail, str) else "Media download failed. Retry in the Media step or upload a scene visual."
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
                            "voice_text": item.get("voice_text"),
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
                            "media_error": media_errors.get(item.get("scene_number") or item.get("scene")),
                            "media_match_level": downloaded_media.get(item.get("scene_number") or item.get("scene"), {}).get("match_level"),
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

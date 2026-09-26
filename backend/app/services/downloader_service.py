import os
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.media import Media

from app.core.pexels_client import PexelsClient
from app.core.pixabay_client import PixabayClient
from app.config.prompt_config import VISUAL_NICHE_BOUNDARIES


class DownloaderService:

    @staticmethod
    def _search_queries(scene, keyword):
        """Try scene/topic, then niche, then project; never use unrelated defaults."""
        content = scene.content
        config = getattr(content, "generation_config", None) or {}
        project = getattr(scene, "project", None)
        brand = getattr(project, "brand", None)
        normalize = lambda value: re.sub(r"[^a-z0-9]", "", str(value or "").lower())
        topic = config.get("topic") or getattr(content, "title", "")
        topic_queries = [keyword]
        if len(keyword.split()) > 2:
            topic_queries.append(" ".join(keyword.split()[:2]))
        topic_queries.append(topic)
        niche = config.get("niche") or getattr(project, "niche", "") or getattr(brand, "niche", "")
        scope = next((scope for name, scope in VISUAL_NICHE_BOUNDARIES.items()
                      if normalize(name) in {normalize(niche), normalize(getattr(brand, "name", ""))}), "")
        if scope:
            niche_queries = [term.strip() for term in scope.split(",")]
            # Prefer boundary subjects mentioned by the topic. Rotate ties to
            # avoid always choosing the same fallback subject for every scene.
            offset = (scene.scene_number - 1) % len(niche_queries)
            niche_queries = niche_queries[offset:] + niche_queries[:offset]
            words = set(re.findall(r"[a-z]+", f"{topic} {keyword}".lower()))
            niche_queries.sort(key=lambda term: -len(words & set(re.findall(r"[a-z]+", term.lower()))))
        else:
            niche_queries = re.split(r"[,/&]", niche or "")
        project_queries = [getattr(project, field, "") for field in ("topic", "niche", "title")]
        seen, queries = set(), []
        for level, values in (("topic", topic_queries), ("niche", niche_queries[:3]), ("project", project_queries)):
            for value in values:
                if not isinstance(value, str):
                    continue
                value = re.sub(r"\s+", " ", value.replace("_", " ")).strip()
                if value and value.casefold() not in seen:
                    seen.add(value.casefold())
                    queries.append((level, value))
        return queries

    @staticmethod
    def _media_orientation(scene: Scene) -> str:
        """Choose source media that needs the least crop for the final post."""
        content = scene.content
        platform = (getattr(content, "platform", "") or "").lower()
        content_type = (getattr(content, "content_type", "") or "").lower()

        if any(value in content_type for value in ("reel", "short", "story")):
            return "portrait"
        if "long video" in content_type or content_type == "video":
            return "landscape"
        if "carousel" in content_type:
            return "portrait"
        if "youtube" in platform and "community" not in content_type:
            return "landscape"
        if "instagram" in platform or "facebook" in platform:
            return "portrait"
        return "square"

    # ==========================================================
    # Download Scene Media
    # ==========================================================

    @staticmethod
    def download(
        db: Session,
        scene_id: int,
        user_id: int | None = None,
    ):

        # ======================================================
        # Get Scene
        # ======================================================

        scene = (

            db.query(Scene)

            .filter(Scene.id == scene_id)

            .first()

        )

        if scene and user_id is not None and scene.user_id != user_id:
            scene = None

        if not scene:

            raise HTTPException(

                status_code=404,

                detail="Scene not found.",

            )

        # ======================================================
        # Resolve Search Keyword
        # ======================================================

        scene_media_type = (scene.media_type or "").lower()

        if scene_media_type == "image":
            search_keyword = (
                scene.keyword
                or scene.image_prompt
                or scene.video_prompt
            )
        elif scene_media_type == "video":
            search_keyword = (
                scene.keyword
                or scene.video_prompt
                or scene.image_prompt
            )
        else:
            search_keyword = (
                scene.keyword
                or scene.image_prompt
                or scene.video_prompt
            )

        if isinstance(search_keyword, (list, tuple)):
            search_keyword = " ".join(str(item) for item in search_keyword)

        search_keyword = str(search_keyword or "").strip()

        search_queries = DownloaderService._search_queries(scene, search_keyword)
        if not search_queries:

            raise HTTPException(

                status_code=400,

                detail="Add a scene topic, niche, or project description to find relevant media.",

            )

        # ======================================================
        # Already Downloaded?
        # ======================================================

        if scene.media_id:

            media = (

                db.query(Media)

                .filter(
                    Media.id == scene.media_id,
                )

                .first()

            )

            if media and os.path.isfile(media.file_path):

                return {

                    "success": True,

                    "scene_id": scene.id,

                    "media_id": media.id,

                    "provider": media.provider,

                    "title": media.title,

                    "file_name": media.file_name,

                    "file_path": media.file_path,

                    "file_url": media.file_url,

                    "status": media.status,
                    "match_level": next((level for level in ("topic", "niche", "project")
                                         if (media.title or "").startswith(f"Scene {scene.scene_number} [{level}]:")), None),

                }

        # ======================================================
        # Storage Folder
        # ======================================================

        folder = os.path.join(

            "storage",

            "projects",

            str(scene.project_id),

        )

        media_type = (scene.media_type or "").lower()

        if media_type == "image":

            folder = os.path.join(
                folder,
                "images",
            )

        else:

            folder = os.path.join(
                folder,
                "videos",
            )

        os.makedirs(

            folder,

            exist_ok=True,

        )

        # ======================================================
        # File Name
        # ======================================================

        extension = (
            ".jpg"
            if media_type == "image"
            else ".mp4"
        )

        # Scene numbers restart for each content item. Include the content id so
        # generating several selected formats cannot overwrite previous media.
        filename = f"content_{scene.content_id}_scene_{scene.scene_number}{extension}"

        filepath = os.path.join(

            folder,

            filename,

        )

                # ======================================================
        # Download From Pexels or Pixabay
        # ======================================================

        media = None
        provider_errors = []
        orientation = DownloaderService._media_orientation(scene)

        failed_providers = set()
        match_level = "topic"
        excluded_urls = list((getattr(scene.content, "generation_config", None) or {}).get("excluded_media_urls", []))
        used_in_output = (db.query(Media.file_url).join(Scene, Scene.media_id == Media.id)
                          .filter(Scene.content_id == scene.content_id, Scene.id != scene.id).all())
        excluded_urls.extend(url for (url,) in used_in_output if url)
        for match_level, query in search_queries:
            for client in (PexelsClient, PixabayClient):
                if client in failed_providers:
                    continue
                try:
                    media = client.search_and_download(
                        keyword=query, media_type=media_type, save_path=filepath,
                        orientation=orientation if query == search_keyword else None,
                        **({"excluded_urls": excluded_urls} if excluded_urls else {}),
                    )
                except Exception as exc:
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    reason = ("check API credentials" if status in (401, 403) or not client.API_KEY
                              else "rate limit reached; retry later" if status == 429
                              else "request failed; retry later")
                    provider_errors.append(f"{client.__name__.replace('Client', '')}: {reason}")
                    # Retrying a broken/rate-limited provider for every query only delays fallback.
                    if status != 400:
                        failed_providers.add(client)
                    continue
                if media:
                    break
            if media:
                break

        # ======================================================
        # Validate Download
        # ======================================================

        if not media:

            if provider_errors:
                raise HTTPException(status_code=503, detail="No media could be downloaded. " + "; ".join(provider_errors) + ". Any other provider returned no matching asset. Retry or upload scene media.")

            raise HTTPException(

                status_code=404,

                detail="No relevant media found after topic, niche, and project searches. Refine the search phrase or upload a visual.",

            )

        if not os.path.exists(media["file_path"]):

            raise HTTPException(

                status_code=500,

                detail="Downloaded file not found.",

            )

        # ======================================================
        # Create Media Record
        # ======================================================

        media_record = Media(

            user_id=scene.user_id,

            project_id=scene.project_id,

            media_type=scene.media_type,

            provider=media["provider"],

            title=f"Scene {scene.scene_number} [{match_level}]: {media.get('title') or query}"[:255],

            file_name=filename,

            file_path=media["file_path"],

            file_url=media.get("file_url", ""),

            mime_type=media["mime_type"],

            extension=media["extension"],

            duration=media.get("duration"),

            width=media.get("width"),

            height=media.get("height"),

            file_size=media.get("file_size"),

            status="ready",

        )

                # ======================================================
        # Save Media + Update Scene
        # ======================================================

        try:

            db.add(media_record)

            db.flush()

            # Update Scene

            scene.media_id = media_record.id

            scene.status = "downloaded"

            db.commit()

            db.refresh(media_record)

            db.refresh(scene)

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=500,

                detail=f"Database error : {str(e)}",

            )

        # ======================================================
        # Response
        # ======================================================

        return {

            "success": True,

            "scene_id": scene.id,

            "media_id": media_record.id,

            "provider": media_record.provider,

            "title": media_record.title,

            "file_name": media_record.file_name,

            "file_path": media_record.file_path,

            "file_url": media_record.file_url,

            "media_type": media_record.media_type,

            "match_level": match_level,

            "status": media_record.status,

        }

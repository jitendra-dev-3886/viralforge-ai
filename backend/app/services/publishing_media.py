import hashlib
import ipaddress
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageOps

from app.models.media import Media

STORAGE = Path(__file__).resolve().parents[2] / "storage"


def posting_metadata(content, provider):
    title = (content.title or "").strip()
    description = (content.caption or "").strip()
    credit = ((getattr(content, "generation_config", None) or {}).get("audio") or {}).get("license_note", "").strip()
    if credit and credit not in description:
        description = "\n\n".join(value for value in [description, credit] if value)
    raw_hashtags = content.hashtags or ""
    parts = raw_hashtags if isinstance(raw_hashtags, list) else re.split(r"[,\s]+", raw_hashtags)
    seen = {tag.casefold() for tag in re.findall(r"#\w+", description)}
    hashtags = []
    for part in parts:
        tag = re.sub(r"[^\w]", "", str(part))
        if tag and f"#{tag}".casefold() not in seen:
            hashtags.append(f"#{tag}")
            seen.add(f"#{tag}".casefold())
    raw_keywords = content.keywords or ""
    parts = raw_keywords if isinstance(raw_keywords, list) else re.split(r"[,;\n]+", raw_keywords)
    tags, seen = [], set()
    for part in parts:
        tag = str(part).strip().lstrip("#").strip()
        if tag and tag.casefold() not in seen:
            tags.append(tag)
            seen.add(tag.casefold())
    if provider == "youtube":
        if not title or any(char in title + description for char in "<>"):
            raise HTTPException(400, "YouTube needs a title, and its title and description cannot contain < or >.")
        if sum(len(tag) + (2 if " " in tag else 0) for tag in tags) + max(0, len(tags) - 1) > 500:
            raise HTTPException(400, "Shorten YouTube keywords to 500 characters including separators and quotes around phrases.")
    sections = ([title] if provider != "youtube" and title and not description.startswith(title) else [])
    sections.extend([description, " ".join(hashtags)])
    return {"title": title, "caption": "\n\n".join(section for section in sections if section), "tags": tags}


def file_path(value):
    path = Path(value)
    if not path.is_absolute():
        path = STORAGE.parent / path
    path = path.resolve()
    if not path.is_relative_to(STORAGE.resolve()) or not path.is_file():
        raise HTTPException(400, "Selected media is unavailable. Export it again before scheduling.")
    return path


def checksum(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def public_base():
    value = os.getenv("PUBLIC_MEDIA_BASE_URL", os.getenv("BACKEND_URL", "")).rstrip("/")
    parsed = urlparse(value)
    host = parsed.hostname or ""
    private = host in {"localhost", ""} or host.endswith((".localhost", ".local"))
    try:
        private = private or not ipaddress.ip_address(host).is_global
    except ValueError:
        pass
    if parsed.scheme != "https" or private or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HTTPException(503, "Instagram publishing needs a public HTTPS media address. Configure PUBLIC_MEDIA_BASE_URL first.")
    return value


def snapshot(db, user_id, content, account, media_ids, privacy, made_for_kids):
    if len(media_ids) != len(set(media_ids)) or not 1 <= len(media_ids) <= 10:
        raise HTTPException(400, "Select one video or 1–10 distinct images in publishing order.")
    records = db.query(Media).filter(Media.id.in_(media_ids), Media.user_id == user_id, Media.project_id == content.project_id, Media.status == "ready").all()
    by_id = {row.id: row for row in records}
    if len(by_id) != len(media_ids):
        raise HTTPException(404, "Selected media is not available in this project.")
    ordered = [by_id[id] for id in media_ids]
    images = all(row.media_type == "image" and (row.extension or "").lower() in {".png", ".jpg", ".jpeg", ".webp"} for row in ordered)
    video = len(ordered) == 1 and ordered[0].media_type in {"video", "render", "final"} and (ordered[0].extension or "").lower() in {".mp4", ".mov", ".webm"}
    if not images and not video:
        raise HTTPException(400, "Use one video or a set of images. Mixed image/video posts are not supported.")
    if account.provider == "youtube" and not video:
        raise HTTPException(400, "YouTube automatic publishing supports videos and Shorts. Select an exported video.")
    base = public_base() if account.provider == "instagram" else ""
    metadata = posting_metadata(content, account.provider)
    caption = metadata["caption"]
    if account.provider == "instagram" and len(caption) > 2200:
        raise HTTPException(400, "Instagram captions must be 2,200 characters or fewer. Shorten the caption before scheduling.")
    if account.provider == "youtube" and (len(content.title or "") > 100 or len(caption.encode("utf-8")) > 5000):
        raise HTTPException(400, "Shorten the YouTube title (100 characters) or description (5,000 bytes).")
    assets, created = [], []
    try:
        for media in ordered:
            path = file_path(media.file_path)
            if images and account.provider == "instagram":
                folder = STORAGE / "publishing"
                folder.mkdir(parents=True, exist_ok=True)
                converted = folder / f"{uuid4().hex}.jpg"
                with Image.open(path) as source:
                    normalized = ImageOps.exif_transpose(source).convert("RGB")
                    ratio = normalized.width / normalized.height
                    if not 0.8 <= ratio <= 1.91:
                        raise HTTPException(400, "Instagram feed images need a 4:5 to 1.91:1 aspect ratio. Export a compatible image first.")
                    normalized.thumbnail((1440, 1800))
                    created.append(converted)
                    normalized.save(converted, "JPEG", quality=92)
                path = converted
            assets.append({"media_id": media.id, "name": media.title or media.file_name,
                           "path": str(path), "sha256": checksum(path), "size": path.stat().st_size,
                           "mime": "image/jpeg" if images and account.provider == "instagram" else media.mime_type,
                           "url": f"{base}/storage/{path.relative_to(STORAGE.resolve()).as_posix()}" if base else None})
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return {**metadata, "kind": "video" if video else "images",
            "assets": assets, "privacy": privacy, "made_for_kids": made_for_kids,
            "account_name": account.name, "provider": account.provider, "remote_id": account.remote_id}

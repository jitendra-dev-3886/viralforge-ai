"""Optional CC0 photo fallback from Openverse's image index."""
import io
import os
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

from app.core.visual_download import MAX_VISUAL_BYTES, VisualSizeLimitError, limited_chunks
from app.core.media_selection import best_for_query

load_dotenv()


class OpenverseClient:
    ENABLED = os.getenv("OPENVERSE_ENABLED", "false").lower() == "true"
    # No API key is required for the public search tier.
    API_KEY = "public"
    IMAGE_URL = "https://api.openverse.org/v1/images/"
    HOSTS = ("staticflickr.com", "wikimedia.org", "stocksnap.io", "rawpixel.com")

    @classmethod
    def search_and_download(cls, keyword, media_type, save_path, orientation=None, excluded_urls=None):
        if media_type != "image" or not cls.ENABLED:
            return None
        response = requests.get(cls.IMAGE_URL,
            params={"q": keyword, "license": "cc0", "category": "photograph", "page_size": 20},
            headers={"Accept": "application/json", "User-Agent": "ViralForge/1.0"}, timeout=(10, 30))
        response.raise_for_status()
        excluded = {url.split("?")[0] for url in (excluded_urls or [])}
        candidates = []
        for item in response.json().get("results", []):
            url = item.get("url", "")
            parsed = urlsplit(url)
            host = parsed.hostname or ""
            if (item.get("license") != "cc0" or item.get("mature")
                    or parsed.scheme != "https" or parsed.port not in (None, 443)
                    or not any(host == allowed or host.endswith("." + allowed) for allowed in cls.HOSTS)
                    or url.split("?")[0] in excluded):
                continue
            candidates.append({**item, "tags": " ".join(tag.get("name", "") for tag in item.get("tags", []))})
        selected = best_for_query(candidates, lambda item: (item.get("width"), item.get("height")),
                                  query=keyword, media_type="image", orientation=orientation)
        if not selected:
            return None
        # Indexed source URLs may be stale. Reject redirects rather than fetch
        # an unchecked destination, and cap memory before decoding the image.
        with requests.get(selected["url"], stream=True, timeout=(10, 60), allow_redirects=False) as download:
            download.raise_for_status()
            if download.status_code != 200 or not download.headers.get("Content-Type", "").startswith("image/"):
                raise ValueError("Openverse source did not return an image")
            buffer = io.BytesIO()
            for chunk in limited_chunks(download):
                buffer.write(chunk)
        buffer.seek(0)
        partial = save_path + ".part"
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        try:
            with Image.open(buffer) as source:
                photo = ImageOps.exif_transpose(source).convert("RGB")
                photo.thumbnail((4096, 4096))
                width, height = photo.size
                photo.save(partial, format="JPEG", quality=92)
            if os.path.getsize(partial) > MAX_VISUAL_BYTES:
                raise VisualSizeLimitError()
            os.replace(partial, save_path)
        finally:
            if os.path.exists(partial):
                os.remove(partial)
        return {"provider": "Openverse", "title": selected.get("title") or keyword,
                "file_url": selected["url"], "file_path": save_path, "file_size": os.path.getsize(save_path),
                "width": width, "height": height, "duration": 0, "mime_type": "image/jpeg", "extension": ".jpg"}

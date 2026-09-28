"""Optional Coverr stock-video adapter using its documented download endpoint."""
import os
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv

from app.core.visual_download import limited_chunks
from app.core.media_selection import best_for_query

load_dotenv()


class CoverrClient:
    API_KEY = os.getenv("COVERR_API_KEY", "").strip()
    VIDEO_URL = "https://api.coverr.co/videos"

    @classmethod
    def search_and_download(cls, keyword, media_type, save_path, orientation=None, excluded_urls=None):
        if media_type != "video" or not cls.API_KEY:
            return None
        response = requests.get(cls.VIDEO_URL,
            headers={"Authorization": f"Bearer {cls.API_KEY}", "Accept": "application/json"},
            params={"query": keyword, "page": 0, "page_size": 20, "urls": "true"},
            timeout=(10, 30))
        response.raise_for_status()
        excluded = {url.split("?")[0].removesuffix("/download").removesuffix("/preview") for url in (excluded_urls or [])}
        candidates = []
        for item in response.json().get("hits", []):
            urls = item.get("urls") or {}
            download = urls.get("mp4_download", "")
            parsed = urlsplit(download)
            if parsed.scheme != "https" or parsed.hostname != "storage.coverr.co":
                continue
            if any(url.split("?")[0].removesuffix("/download").removesuffix("/preview") in excluded
                   for url in urls.values() if isinstance(url, str)):
                continue
            candidates.append({**item, "alt": item.get("description", "")})
        selected = best_for_query(candidates, lambda item: (item.get("max_width"), item.get("max_height")),
                                  query=keyword, media_type="video", orientation=orientation)
        if not selected:
            return None
        url = selected["urls"]["mp4_download"]
        # This URL records the download; do not use the preview URL instead.
        # Do not forward API authorization headers to the media server.
        partial = save_path + ".part"
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        try:
            with requests.get(url, stream=True, timeout=(10, 120)) as download:
                download.raise_for_status()
                if "video/mp4" not in download.headers.get("Content-Type", "").lower():
                    raise ValueError("Coverr returned an unexpected media type")
                with open(partial, "wb") as file:
                    for chunk in limited_chunks(download):
                        if chunk:
                            file.write(chunk)
            if not os.path.getsize(partial):
                raise ValueError("Coverr returned an empty video")
            os.replace(partial, save_path)
        finally:
            if os.path.exists(partial):
                os.remove(partial)
        return {"provider": "Coverr", "title": selected.get("title") or keyword,
                "file_url": url, "file_path": save_path, "file_size": os.path.getsize(save_path),
                "width": selected.get("max_width", 0), "height": selected.get("max_height", 0),
                "duration": round(selected.get("duration") or 0), "mime_type": "video/mp4", "extension": ".mp4"}

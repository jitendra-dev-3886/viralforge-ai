import os
import requests

from dotenv import load_dotenv

from app.core.media_selection import best_by_dimensions, best_for_query

load_dotenv()


class PixabayClient:

    IMAGE_URL = "https://pixabay.com/api/"
    VIDEO_URL = "https://pixabay.com/api/videos/"
    API_KEY = os.getenv("PIXABAY_API_KEY")

    @classmethod
    def headers(cls):
        if not cls.API_KEY:
            raise Exception("PIXABAY_API_KEY not found in .env")

        return {
            "Accept": "application/json",
        }

    @classmethod
    def search_images(
        cls,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: str | None = None,
    ):
        pixabay_orientation = {
            "portrait": "vertical",
            "landscape": "horizontal",
        }.get((orientation or "").lower())
        response = requests.get(
            cls.IMAGE_URL,
            headers=cls.headers(),
            params={
                "key": cls.API_KEY,
                "q": query,
                "image_type": "photo",
                "safesearch": "true",
                "per_page": per_page,
                "page": page,
                **({"orientation": pixabay_orientation} if pixabay_orientation else {}),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def search_videos(cls, query: str, per_page: int = 10, page: int = 1):
        response = requests.get(
            cls.VIDEO_URL,
            headers=cls.headers(),
            params={
                "key": cls.API_KEY,
                "q": query,
                "per_page": per_page,
                "page": page,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def first_image(cls, query: str, orientation: str | None = None, excluded_urls=None):
        data = cls.search_images(query=query, per_page=20, orientation=orientation)
        hits = data.get("hits", [])
        excluded = {url.split("?")[0] for url in (excluded_urls or [])}
        hits = [item for item in hits if not any(str(item.get(key, "")).split("?")[0] in excluded for key in ("largeImageURL", "webformatURL", "previewURL"))]
        if not hits:
            return cls.first_image(query, excluded_urls=excluded_urls) if orientation else None
        image = best_for_query(
            hits,
            lambda item: (item.get("imageWidth"), item.get("imageHeight")),
            query=query,
            media_type="image",
            orientation=orientation,
        )
        if not image:
            return cls.first_image(query, excluded_urls=excluded_urls) if orientation else None
        return {
            "provider": "Pixabay",
            "title": image.get("tags", query),
            "file_url": image.get("largeImageURL") or image.get("webformatURL"),
            "width": image.get("imageWidth", 0),
            "height": image.get("imageHeight", 0),
            "mime_type": "image/jpeg",
            "extension": ".jpg",
            "duration": 0,
        }

    @classmethod
    def first_video(cls, query: str, orientation: str | None = None, excluded_urls=None):
        data = cls.search_videos(query=query, per_page=20)
        hits = data.get("hits", [])
        excluded = {url.split("?")[0] for url in (excluded_urls or [])}
        hits = [item for item in hits if not any(str(file.get("url", "")).split("?")[0] in excluded for file in item.get("videos", {}).values())]
        if not hits:
            return None

        def video_dimensions(item):
            files = item.get("videos", {})
            largest = best_by_dimensions(
                files.values(),
                lambda file: (file.get("width"), file.get("height")),
                media_type="video",
                orientation=orientation,
            )
            return (
                (largest or {}).get("width", 0),
                (largest or {}).get("height", 0),
            )

        video = best_for_query(
            hits,
            video_dimensions,
            query=query,
            media_type="video",
            orientation=orientation,
        )
        if not video:
            return None
        files = video.get("videos", {})
        selected_file = best_by_dimensions(
            files.values(),
            lambda item: (item.get("width"), item.get("height")),
            media_type="video",
            orientation=orientation,
        )
        if not selected_file or not selected_file.get("url"):
            return None
        return {
            "provider": "Pixabay",
            "title": query,
            "file_url": selected_file.get("url", ""),
            "width": selected_file.get("width", 0),
            "height": selected_file.get("height", 0),
            "mime_type": "video/mp4",
            "extension": ".mp4",
            "duration": int(video.get("duration", 0)),
        }

    @classmethod
    def download_file(cls, url: str, save_path: str):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(8192):
                if chunk:
                    file.write(chunk)
        return {
            "file_path": save_path,
            "file_size": os.path.getsize(save_path),
        }

    @classmethod
    def search_and_download(
        cls,
        keyword: str,
        media_type: str,
        save_path: str,
        orientation: str | None = None,
        excluded_urls=None,
    ):
        if media_type.lower() == "image":
            media = cls.first_image(keyword, orientation=orientation, excluded_urls=excluded_urls)
        elif media_type.lower() == "video":
            media = cls.first_video(keyword, orientation=orientation, excluded_urls=excluded_urls)
        else:
            raise Exception("Unsupported media type.")

        if not media:
            return None

        download = cls.download_file(media["file_url"], save_path)
        return {
            "provider": media["provider"],
            "title": media["title"],
            "file_url": media["file_url"],
            "file_path": download["file_path"],
            "file_size": download["file_size"],
            "width": media["width"],
            "height": media["height"],
            "mime_type": media["mime_type"],
            "extension": media["extension"],
            "duration": media["duration"],
        }

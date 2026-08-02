import os
import requests

from dotenv import load_dotenv

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
    def search_images(cls, query: str, per_page: int = 10, page: int = 1):
        response = requests.get(
            cls.IMAGE_URL,
            headers=cls.headers(),
            params={
                "key": cls.API_KEY,
                "q": query,
                "image_type": "photo",
                "per_page": per_page,
                "page": page,
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
    def first_image(cls, query: str):
        data = cls.search_images(query=query, per_page=1)
        hits = data.get("hits", [])
        if not hits:
            return None
        image = hits[0]
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
    def first_video(cls, query: str):
        data = cls.search_videos(query=query, per_page=1)
        hits = data.get("hits", [])
        if not hits:
            return None
        video = hits[0]
        files = video.get("videos", {})
        medium = files.get("medium") or files.get("large") or files.get("small")
        if not medium:
            return None
        return {
            "provider": "Pixabay",
            "title": query,
            "file_url": medium.get("url", ""),
            "width": medium.get("width", 0),
            "height": medium.get("height", 0),
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
    def search_and_download(cls, keyword: str, media_type: str, save_path: str):
        if media_type.lower() == "image":
            media = cls.first_image(keyword)
        elif media_type.lower() == "video":
            media = cls.first_video(keyword)
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

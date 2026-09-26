import os
import requests

from dotenv import load_dotenv

from app.core.media_selection import best_by_dimensions, best_for_query

load_dotenv()


class PexelsClient:

    IMAGE_URL = "https://api.pexels.com/v1/search"

    VIDEO_URL = "https://api.pexels.com/videos/search"

    API_KEY = os.getenv("PEXELS_API_KEY")

    # ==========================================================
    # Headers
    # ==========================================================

    @classmethod
    def headers(cls):

        if not cls.API_KEY:

            raise Exception(
                "PEXELS_API_KEY not found in .env"
            )

        return {
            "Authorization": cls.API_KEY,
        }

    # ==========================================================
    # Search Images
    # ==========================================================

    @classmethod
    def search_images(
        cls,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: str | None = None,
    ):

        response = requests.get(

            cls.IMAGE_URL,

            headers=cls.headers(),

            params={
                "query": query,
                "per_page": per_page,
                "page": page,
                **({"orientation": orientation} if orientation else {}),
            },

            timeout=30,

        )

        response.raise_for_status()

        return response.json()

    # ==========================================================
    # Search Videos
    # ==========================================================

    @classmethod
    def search_videos(
        cls,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: str | None = None,
    ):

        response = requests.get(

            cls.VIDEO_URL,

            headers=cls.headers(),

            params={
                "query": query,
                "per_page": per_page,
                "page": page,
                **({"orientation": orientation} if orientation else {}),
            },

            timeout=30,

        )

        response.raise_for_status()

        return response.json()

    # ==========================================================
    # First Image
    # ==========================================================

    @classmethod
    def first_image(
        cls,
        query: str,
        orientation: str | None = None,
        excluded_urls=None,
    ):

        data = cls.search_images(
            query=query,
            per_page=20,
            orientation=orientation,
        )

        photos = data.get(
            "photos",
            [],
        )

        excluded = {url.split("?")[0] for url in (excluded_urls or [])}
        photos = [item for item in photos if not any(str(url).split("?")[0] in excluded for url in item.get("src", {}).values())]
        if not photos:
            return cls.first_image(query, excluded_urls=excluded_urls) if orientation else None

        photo = best_for_query(
            photos,
            lambda item: (item.get("width"), item.get("height")),
            query=query,
            media_type="image",
            orientation=orientation,
        )

        if not photo:
            return cls.first_image(query, excluded_urls=excluded_urls) if orientation else None

        return {

            "provider": "Pexels",

            "title": photo.get(
                "alt",
                query,
            ),

            "file_url": photo["src"]["large2x"],

            "width": photo.get("width", 0),

            "height": photo.get("height", 0),

            "mime_type": "image/jpeg",

            "extension": ".jpg",

            "duration": 0,

        }

    # ==========================================================
    # First Video
    # ==========================================================

    @classmethod
    def first_video(
        cls,
        query: str,
        orientation: str | None = None,
        excluded_urls=None,
    ):

        data = cls.search_videos(
            query=query,
            per_page=20,
            orientation=orientation,
        )

        videos = data.get(
            "videos",
            [],
        )

        excluded = {url.split("?")[0] for url in (excluded_urls or [])}
        videos = [item for item in videos if not any(str(file.get("link", "")).split("?")[0] in excluded for file in item.get("video_files", []))]
        if not videos:
            return cls.first_video(query, excluded_urls=excluded_urls) if orientation else None

        video = best_for_query(
            videos,
            lambda item: (item.get("width"), item.get("height")),
            query=query,
            media_type="video",
            orientation=orientation,
        )

        if not video:
            return cls.first_video(query, excluded_urls=excluded_urls) if orientation else None

        files = video.get(
            "video_files",
            [],
        )

        if not files:
            return None

        best = best_by_dimensions(
            [item for item in files if item.get("file_type") in (None, "video/mp4")],
            lambda item: (item.get("width"), item.get("height")),
            media_type="video",
            orientation=orientation,
        )

        if not best or not best.get("link"):
            return None

        return {

            "provider": "Pexels",

            "title": query,

            "file_url": best["link"],

            "width": best.get("width", 0),

            "height": best.get("height", 0),

            "mime_type": "video/mp4",

            "extension": ".mp4",

            "duration": int(video.get("duration", 0)),

        }

    # ==========================================================
    # Download File
    # ==========================================================

    @classmethod
    def download_file(
        cls,
        url: str,
        save_path: str,
    ):

        os.makedirs(

            os.path.dirname(save_path),

            exist_ok=True,

        )

        response = requests.get(

            url,

            stream=True,

            timeout=120,

        )

        response.raise_for_status()

        with open(
            save_path,
            "wb",
        ) as file:

            for chunk in response.iter_content(8192):

                if chunk:
                    file.write(chunk)

        return {

            "file_path": save_path,

            "file_size": os.path.getsize(save_path),

        }

    # ==========================================================
    # Search & Download
    # ==========================================================

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

        download = cls.download_file(

            media["file_url"],

            save_path,

        )

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

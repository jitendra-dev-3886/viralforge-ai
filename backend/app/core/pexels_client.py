import os
import requests

from dotenv import load_dotenv

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
    ):

        response = requests.get(

            cls.IMAGE_URL,

            headers=cls.headers(),

            params={

                "query": query,

                "per_page": per_page,

                "page": page,

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
    ):

        response = requests.get(

            cls.VIDEO_URL,

            headers=cls.headers(),

            params={

                "query": query,

                "per_page": per_page,

                "page": page,

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
    ):

        data = cls.search_images(
            query=query,
            per_page=1,
        )

        photos = data.get(
            "photos",
            [],
        )

        if not photos:
            return None

        photo = photos[0]

        return {

            "provider": "Pexels",

            "title": photo.get(
                "alt",
                query,
            ),

            "url": photo["src"]["large2x"],

            "width": photo.get("width"),

            "height": photo.get("height"),

            "mime_type": "image/jpeg",

            "extension": ".jpg",

        }

    # ==========================================================
    # First Video
    # ==========================================================

    @classmethod
    def first_video(
        cls,
        query: str,
    ):

        data = cls.search_videos(
            query=query,
            per_page=1,
        )

        videos = data.get(
            "videos",
            [],
        )

        if not videos:
            return None

        video = videos[0]

        files = video.get(
            "video_files",
            [],
        )

        if not files:
            return None

        best = max(
            files,
            key=lambda x: x.get("width", 0),
        )

        return {

            "provider": "Pexels",

            "title": query,

            "url": best["link"],

            "width": best.get("width"),

            "height": best.get("height"),

            "mime_type": "video/mp4",

            "extension": ".mp4",

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

            "path": save_path,

            "size": os.path.getsize(save_path),

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
    ):

        if media_type.lower() == "image":

            media = cls.first_image(keyword)

        else:

            media = cls.first_video(keyword)

        if not media:

            return None

        download = cls.download_file(

            media["url"],

            save_path,

        )

        return {

            **media,

            **download,

        }
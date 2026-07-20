import os
import requests
from dotenv import load_dotenv

load_dotenv()


class PexelsClient:

    IMAGE_URL = "https://api.pexels.com/v1/search"

    VIDEO_URL = "https://api.pexels.com/videos/search"

    API_KEY = os.getenv("PEXELS_API_KEY")

    @classmethod
    def headers(cls):

        return {
            "Authorization": cls.API_KEY,
        }

    @classmethod
    def search_images(
        cls,
        query,
        per_page=10,
        page=1,
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

    @classmethod
    def search_videos(
        cls,
        query,
        per_page=10,
        page=1,
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

    @classmethod
    def download_file(
        cls,
        url,
        save_path,
    ):

        response = requests.get(
            url,
            stream=True,
            timeout=60,
        )

        response.raise_for_status()

        with open(save_path, "wb") as file:

            for chunk in response.iter_content(8192):

                if chunk:

                    file.write(chunk)

        return save_path
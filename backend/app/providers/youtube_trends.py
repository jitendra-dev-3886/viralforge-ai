import os
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class YoutubeProvider:

    def __init__(self):

        key = os.getenv("YOUTUBE_API_KEY")

        print("YOUTUBE:", key[:10])

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=key,
        )

    def get_trending(self):

        request = self.youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="IN",
            maxResults=5,
        )

        response = request.execute()

        print(response)

        return response
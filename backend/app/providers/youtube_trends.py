import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class YoutubeProvider:

    def __init__(self):

        key = os.getenv("YOUTUBE_API_KEY")

        if not key:
            raise ValueError("YOUTUBE_API_KEY is not configured")

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=key,
        )

    def get_trending(self, query: str | None = None, limit: int = 25, language: str = "en"):
        """Return video titles, optionally focused on one creator niche."""
        limit = max(1, min(limit, 50))

        if not query:
            response = self.youtube.videos().list(
                part="snippet",
                chart="mostPopular",
                regionCode="IN",
                maxResults=limit,
            ).execute()
        else:
            # A recent niche search produces useful creator topics; the global
            # most-popular endpoint cannot be filtered by niche.
            published_after = (
                datetime.now(timezone.utc) - timedelta(days=7)
            ).isoformat().replace("+00:00", "Z")
            response = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                order="viewCount",
                regionCode="IN",
                relevanceLanguage=language,
                publishedAfter=published_after,
                maxResults=limit,
            ).execute()

        return [
            item.get("snippet", {}).get("title", "").strip()
            for item in response.get("items", [])
            if item.get("snippet", {}).get("title")
        ]

import os

from newsapi import NewsApiClient


class NewsProvider:

    def __init__(self):

        self.client = NewsApiClient(
            api_key=os.getenv("NEWS_API_KEY")
        )

    def get_trending(self, query: str | None = None, limit: int = 20):

        try:

            if query:
                response = self.client.get_everything(
                    q=query,
                    language="en",
                    sort_by="publishedAt",
                    page_size=min(limit, 100),
                )
            else:
                response = self.client.get_top_headlines(
                    country="in",
                    page_size=min(limit, 100),
                )

            return [
                article.get("title", "").strip()
                for article in response.get("articles", [])
                if article.get("title")
            ]

        except Exception as e:

            print(e)

            return []

import os

from newsapi import NewsApiClient


class NewsProvider:

    def __init__(self):

        self.client = NewsApiClient(
            api_key=os.getenv("NEWS_API_KEY")
        )

    def get_trending(self):

        try:

            response = self.client.get_top_headlines(
                country="in",
                page_size=20,
            )

            return [
                article["title"]
                for article in response["articles"]
            ]

        except Exception as e:

            print(e)

            return []
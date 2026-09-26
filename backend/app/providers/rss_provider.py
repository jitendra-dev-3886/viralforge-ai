from xml.etree import ElementTree

import requests


class RSSProvider:

    URLS = [

        "https://feeds.bbci.co.uk/news/rss.xml",

        "https://techcrunch.com/feed/",

        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",

    ]

    def get_trending(self, query=None, language="en", limit=20):

        news = []

        urls = ["https://news.google.com/rss/search"] if query else self.URLS
        params = {"q": f"{query} when:7d", "hl": f"{language}-IN", "gl": "IN", "ceid": f"IN:{language}"} if query else None
        for url in urls:

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                feed = ElementTree.fromstring(response.content)
                for item in feed.findall(".//item")[:limit]:
                    title = (item.findtext("title") or "").strip()
                    if title:
                        news.append(title)
            except (requests.RequestException, ElementTree.ParseError):
                continue

        return news[:limit]

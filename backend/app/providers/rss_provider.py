import feedparser


class RSSProvider:

    URLS = [

        "https://feeds.bbci.co.uk/news/rss.xml",

        "https://techcrunch.com/feed/",

        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",

    ]

    def get_trending(self):

        news = []

        for url in self.URLS:

            feed = feedparser.parse(url)

            for item in feed.entries[:10]:
                news.append(item.title)

        return news
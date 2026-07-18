from app.providers.youtube_trends import YoutubeProvider
from app.providers.news_provider import NewsProvider
from app.providers.rss_provider import RSSProvider
from app.providers.trend_ai_ranker import TrendAIRanker


class TrendService:

    @staticmethod
    def get_trending():

        trends = []

        try:
            print("Loading YouTube...")
            trends.extend(YoutubeProvider().get_trending())
        except Exception as e:
            print("YouTube Error:", e)

        try:
            print("Loading News...")
            trends.extend(NewsProvider().get_trending())
        except Exception as e:
            print("News Error:", e)

        try:
            print("Loading RSS...")
            trends.extend(RSSProvider().get_trending())
        except Exception as e:
            print("RSS Error:", e)

        print(f"Collected Topics: {len(trends)}")

        trends = list(dict.fromkeys(trends))

        print(f"Unique Topics: {len(trends)}")

        return TrendAIRanker.rank(trends)
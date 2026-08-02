from typing import Optional

from app.providers.youtube_trends import YoutubeProvider
from app.providers.news_provider import NewsProvider
from app.providers.rss_provider import RSSProvider
from app.providers.trend_ai_ranker import TrendAIRanker


class TrendService:

    @staticmethod
    def get_trending(niche: Optional[str] = None):

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

        ranked = TrendAIRanker.rank(trends)

        if niche:
            niche_map = {
                "morning_spiritual": "Spiritual",
                "financial_freedom": "Finance",
                "cosmic_knowledge": "Spiritual",
                "psychology": "Psychology",
                "love_romantic": "Entertainment",
                "finance": "Finance",
                "spiritual": "Spiritual",
                "business": "Business",
                "ai": "AI",
                "technology": "Technology",
                "health": "Health",
                "fitness": "Fitness",
                "education": "Education",
                "entertainment": "Entertainment",
            }

            category = niche_map.get(niche.lower())

            if isinstance(ranked, list):
                filtered = []

                for item in ranked:
                    if not isinstance(item, dict):
                        continue

                    title = str(item.get("title", "")).lower()
                    item_category = str(item.get("category", "")).lower()

                    if category and item_category == category.lower():
                        filtered.append(item)
                    elif niche.lower() in title or niche.lower() in item_category:
                        filtered.append(item)

                if filtered:
                    return filtered

        return ranked
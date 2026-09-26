import re
from time import monotonic
from typing import Optional

class TrendService:
    """Return up to five live topics per language for any selected niche."""
    _cache = {}

    @staticmethod
    def _unique_titles(items) -> list[str]:
        titles = []
        seen = set()
        for item in items:
            title = item.get("title", "") if isinstance(item, dict) else item
            title = re.sub(r"\s+", " ", str(title or "")).strip()
            key = TrendService._title_key(title)
            if title and key and key not in seen:
                seen.add(key)
                titles.append(title)
        return titles

    @staticmethod
    def _title_key(title: str) -> str:
        return re.sub(r"[^\w\u0900-\u097f]+", "", title.casefold())

    @classmethod
    def get_trending(cls, niche: Optional[str] = None, limit: int = 10, *, credentials=None, user_id=None, brand="", boundary="", platform="", content_type=""):
        query = re.sub(r"[_\s]+", " ", niche or "").strip()
        if not query:
            return {"trends": [], "niche": "", "total": 0, "live_count": 0, "sources": []}
        cache_key = (user_id, query.casefold(), brand, boundary, platform, content_type)
        cached = cls._cache.get(cache_key)
        if cached and monotonic() < cached[0]:
            return cached[1]
        # Boundaries describe relevance; OR-ing every term pulls in unrelated
        # headlines (e.g. computer memory instead of human psychology).
        search_query = query
        topics, sources = [], []
        for language in ("hi", "en"):
            source_titles = []
            try:
                from app.providers.youtube_trends import YoutubeProvider

                source_titles = YoutubeProvider().get_trending(query=search_query, limit=25, language=language)
                if source_titles and "YouTube" not in sources:
                    sources.append("YouTube")
            except Exception as exc:
                print(f"YouTube trends unavailable: {type(exc).__name__}")

            # NewsAPI supports English, but does not support Hindi.
            if language == "en":
                try:
                    from app.providers.news_provider import NewsProvider

                    news_titles = NewsProvider().get_trending(query=search_query.replace("|", " OR "), limit=20)
                    source_titles.extend(news_titles)
                    if news_titles:
                        sources.append("News")
                except Exception as exc:
                    print(f"News trends unavailable: {type(exc).__name__}")

            # Language relevance is only a provider hint; enforce the title script too.
            def matches_language(title):
                return (bool(re.search(r"[\u0900-\u097f]", title)) if language == "hi"
                        else any(c.isalpha() for c in title) and all(c.isascii() for c in title if c.isalpha()))

            live_titles = [title for title in cls._unique_titles(source_titles) if matches_language(title)][:20]
            from app.providers.rss_provider import RSSProvider

            # Candidate count alone says nothing about creator relevance. Include
            # niche-specific feeds even when the other sources returned many hits.
            news_titles = RSSProvider().get_trending(query=search_query, language=language, limit=30)
            extra_titles = [title for title in cls._unique_titles(news_titles) if matches_language(title)]
            live_titles = cls._unique_titles(extra_titles + live_titles)[:30]
            if extra_titles and "Google News" not in sources:
                sources.append("Google News")
            topics.extend({"title": title, "category": query, "language": language, "source": "live"}
                          for title in live_titles)

        if topics:
            from app.providers.trend_ai_ranker import TrendAIRanker

            topics = TrendAIRanker.rank(topics, niche=query, boundary=boundary or query, brand=brand,
                                        platform=platform, content_type=content_type, credentials=credentials or {})
        result = {
            "trends": topics,
            "niche": query,
            "total": len(topics),
            "live_count": sum(topic["source"] == "live" for topic in topics),
            "sources": sources,
        }
        # Cache complete live lists longer; retry incomplete sources after a minute.
        if len(cls._cache) >= 128:
            cls._cache.clear()
        cls._cache[cache_key] = (monotonic() + (600 if result["live_count"] == 10 else 60), result)
        return result

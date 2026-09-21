import re
from typing import Optional

class TrendService:
    """Collect a useful sized, niche-specific list of creator topics."""

    NICHE_PROFILES = {
        "morning_spiritual": {
            "label": "Morning Spiritual",
            "category": "Spiritual",
            "query": "morning spirituality meditation mantra",
            "fallback": [
                "5-minute morning meditation for mental clarity",
                "A peaceful morning prayer for a fresh start",
                "How gratitude changes your morning energy",
                "The one spiritual habit to do before checking your phone",
                "A simple sunrise routine for inner peace",
                "Morning affirmations for confidence and calm",
                "Why silent mornings are powerful for the mind",
                "A beginner's guide to breath meditation",
                "The meaning of waking up before sunrise",
                "How to start a daily mantra practice",
                "A short prayer for difficult mornings",
                "Three signs your morning routine needs a reset",
                "How to protect your peace before a busy day",
                "The spiritual lesson in slowing down",
                "A 10-minute ritual for positive energy",
                "How journaling after meditation creates clarity",
            ],
        },
        "financial_freedom": {
            "label": "Financial Freedom",
            "category": "Finance",
            "query": "personal finance saving investing side hustle India",
            "fallback": [
                "How to build an emergency fund on a small income",
                "Five money habits keeping you broke",
                "Beginner investing mistakes to avoid",
                "A simple monthly budget that actually works",
                "How to start a side hustle after work",
                "The difference between saving and investing",
                "How compound interest builds long-term wealth",
                "Seven things to stop buying to save more money",
                "How to negotiate a higher salary confidently",
                "A beginner roadmap to financial independence",
                "How to pay off debt without feeling deprived",
                "The 50-30-20 budget rule explained",
                "Low-cost skills that can increase your income",
                "Why lifestyle inflation destroys savings",
                "How to make your first investment plan",
                "Money lessons people wish they learned at 20",
            ],
        },
        "cosmic_knowledge": {
            "label": "Cosmic Knowledge",
            "category": "Spiritual",
            "query": "space astronomy universe cosmic discoveries",
            "fallback": [
                "What would happen if Earth stopped spinning",
                "The biggest mystery about black holes",
                "How far away is the edge of the observable universe",
                "Why stars look different from different planets",
                "Could humans ever live on Mars",
                "The strange truth about time in space",
                "How astronomers find planets beyond our solar system",
                "What dark matter may be hiding from us",
                "The most beautiful nebulae explained simply",
                "What happens when two galaxies collide",
                "Why the night sky is dark despite billions of stars",
                "Could there be life under an icy moon",
                "The difference between a comet, asteroid, and meteor",
                "What the James Webb telescope is revealing",
                "How the moon affects life on Earth",
                "The most surprising facts about our solar system",
            ],
        },
        "psychology": {
            "label": "Psychology",
            "category": "Psychology",
            "query": "psychology habits emotions relationships mental health",
            "fallback": [
                "Why people overthink at night",
                "How to stop seeking validation from everyone",
                "The psychology behind procrastination",
                "Why emotionally intelligent people stay calm",
                "Signs you are people-pleasing without noticing",
                "How small habits rewire your confidence",
                "Why silence can feel uncomfortable in conversations",
                "The difference between healthy and toxic attachment",
                "How to set boundaries without feeling guilty",
                "Why your brain remembers embarrassing moments",
                "The psychology of self-sabotage",
                "How to recover after social burnout",
                "Why smart people sometimes doubt themselves",
                "What your communication style says about you",
                "How comparison affects self-esteem",
                "The hidden reason habits are hard to change",
            ],
        },
        "love_romantic": {
            "label": "Love & Romantic",
            "category": "Entertainment",
            "query": "relationships love dating communication advice",
            "fallback": [
                "Signs of a healthy relationship",
                "How to communicate when you feel misunderstood",
                "The small habits that make love feel safe",
                "Why emotional availability matters in dating",
                "How to rebuild trust after an argument",
                "The difference between attention and genuine effort",
                "Ways to show love without spending money",
                "How to stop repeating the same relationship pattern",
                "Signs someone respects your boundaries",
                "Why friendships are important in a relationship",
                "How to have difficult conversations with kindness",
                "What secure love feels like",
                "How to know when a relationship needs more effort",
                "The psychology behind missing someone",
                "How to be supportive without losing yourself",
                "Romantic gestures that create lasting memories",
            ],
        },
    }

    @classmethod
    def _profile(cls, niche: Optional[str]) -> dict:
        key = (niche or "").strip().lower()
        return cls.NICHE_PROFILES.get(
            key,
            {
                "label": (niche or "General").replace("_", " ").title(),
                "category": "Education",
                "query": (niche or "creator trends").replace("_", " "),
                "fallback": [],
            },
        )

    @staticmethod
    def _unique_titles(items) -> list[str]:
        titles = []
        seen = set()
        for item in items:
            title = item.get("title", "") if isinstance(item, dict) else item
            title = re.sub(r"\s+", " ", str(title or "")).strip()
            key = re.sub(r"[^a-z0-9]+", "", title.lower())
            if title and key and key not in seen:
                seen.add(key)
                titles.append(title)
        return titles

    @staticmethod
    def _title_key(title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", title.lower())

    @classmethod
    def get_trending(cls, niche: Optional[str] = None, limit: int = 24):
        limit = max(12, min(int(limit or 24), 30))
        profile = cls._profile(niche)
        source_titles = []
        sources = []

        try:
            from app.providers.youtube_trends import YoutubeProvider

            youtube_titles = YoutubeProvider().get_trending(
                query=profile["query"],
                limit=limit,
            )
            source_titles.extend(youtube_titles)
            if youtube_titles:
                sources.append("YouTube")
        except Exception as exc:
            print(f"YouTube trends unavailable: {exc}")

        try:
            from app.providers.news_provider import NewsProvider

            news_titles = NewsProvider().get_trending(
                query=profile["query"],
                limit=limit,
            )
            source_titles.extend(news_titles)
            if news_titles:
                sources.append("News")
        except Exception as exc:
            print(f"News trends unavailable: {exc}")

        source_titles = cls._unique_titles(source_titles)
        ranked = []

        live_titles = cls._unique_titles(ranked or source_titles)
        topics = [
            {
                "title": title,
                "score": 100 - index,
                "category": profile["category"],
                "source": "live",
            }
            for index, title in enumerate(live_titles[:limit])
        ]

        # Provider APIs sometimes return fewer niche matches. Fill the picker
        # with clearly labelled niche ideas instead of showing unrelated news.
        used_titles = {cls._title_key(title) for title in cls._unique_titles(topics)}
        for title in profile["fallback"]:
            if len(topics) >= limit:
                break
            if cls._title_key(title) not in used_titles:
                topics.append(
                    {
                        "title": title,
                        "score": max(50, 80 - len(topics)),
                        "category": profile["category"],
                        "source": "niche idea",
                    }
                )
                used_titles.add(cls._title_key(title))

        # Keep the chooser useful even when a provider is down and the curated
        # seed list is shorter than the requested number of topics.
        for seed in profile["fallback"]:
            if len(topics) >= limit:
                break
            title = f"{seed}: beginner guide"
            if cls._title_key(title) not in used_titles:
                topics.append(
                    {
                        "title": title,
                        "score": max(45, 70 - len(topics)),
                        "category": profile["category"],
                        "source": "niche idea",
                    }
                )
                used_titles.add(cls._title_key(title))

        return {
            "trends": topics,
            "niche": profile["label"],
            "total": len(topics),
            "live_count": min(len(live_titles), limit),
            "sources": sources,
        }

import json
from app.core.groq_client import GroqClient


class TrendAIRanker:

    @staticmethod
    def rank(trends):

        prompt = """
You are ViralForge AI Trend Analyzer.

Below are today's trending topics.

""" + json.dumps(trends, indent=2) + """

Your job is to:

1. Remove duplicate ideas.
2. Merge similar topics.
3. Score each topic from 1-100.
4. Detect category:
- Finance
- Motivation
- Business
- Psychology
- AI
- Technology
- Health
- Fitness
- Spiritual
- Education
- Entertainment

5. Recommend best platform:
- Instagram
- Facebook
- YouTube

6. Recommend best content type:
- Reel
- Carousel
- Story
- Post
- Short
- Video

Return ONLY valid JSON.

Example:

[
  {
    "title": "Bitcoin Crash Explained",
    "score": 98,
    "category": "Finance",
    "platform": "Instagram",
    "content_type": "Reel"
  }
]
"""

        result = GroqClient.generate(prompt)

        return json.loads(result)
import json

from app.core.groq_client import groq_client


class TrendAIRanker:

    @staticmethod
    def rank(trends, niche_label: str = "", category: str = "", limit: int = 24):

        topics = json.dumps(trends, indent=2)

        prompt = f"""
You are ViralForge AI Trend Analyzer.

Below are today's trending topics.

{topics}

Selected creator niche: {niche_label or "General"}
Required category: {category or "Choose the closest category"}

Your tasks are:

1. Remove duplicate ideas.
2. Merge similar topics.
3. Score every topic from 1 to 100.
4. Use the required category when provided; otherwise detect exactly one category:
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

5. Recommend the best platform:
   - Instagram
   - Facebook
   - YouTube

6. Recommend the best content type:
   - Reel
   - Carousel
   - Story
   - Post
   - Short
   - Video

Return up to {limit} unique topics after deduplication and merging. Keep only topics that genuinely match the selected niche. Sort by score descending.

Return ONLY valid JSON.

Expected JSON format:

[
  {{
    "title": "Bitcoin Crash Explained",
    "score": 98,
    "category": "Finance",
    "platform": "Instagram",
    "content_type": "Reel"
  }},
  {{
    "title": "AI is Changing Jobs",
    "score": 95,
    "category": "AI",
    "platform": "YouTube",
    "content_type": "Short"
  }}
]

Rules:

- Return JSON only.
- No markdown.
- No explanation.
- No comments.
- No extra text.
"""

        try:

            response = groq_client.generate(prompt)

            if response.startswith("```"):
                response = response.replace("```json", "")
                response = response.replace("```", "")
                response = response.strip()

            return json.loads(response)

        except json.JSONDecodeError:

            return {
                "success": False,
                "message": "Groq returned invalid JSON.",
                "raw_response": response,
            }

        except Exception as e:

            return {
                "success": False,
                "message": str(e),
            }

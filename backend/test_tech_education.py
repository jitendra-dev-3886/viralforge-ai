import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.config.prompt_config import tech_education_direction
from app.providers.trend_ai_ranker import TrendAIRanker
from app.schemas.ai import GenerateRequest
from app.services.prompt_engine import PromptEngine


class TechEducationTests(unittest.TestCase):
    def request(self, niche="AI & Technology", **updates):
        return GenerateRequest(project_id=1, platforms=["Instagram"], content_types=["Carousel"],
                               niche=niche, topic="How an API request works", package="carousel",
                               **updates)

    def test_existing_niche_names_and_brand_activate_education(self):
        for niche, brand in (("AI & Technology", None), ("AI Tech", None),
                             ("Software Engineering", None), ("Custom", SimpleNamespace(name="YS Tech"))):
            with self.subTest(niche=niche):
                prompt = PromptEngine.build(self.request(niche), brand=brand)
                self.assertIn("students, interns, developers, software engineers and working professionals", prompt)
                self.assertIn("one clear learning objective", prompt)
                self.assertIn("Topic: How an API request works", prompt)
                self.assertIn("Create exactly 6 scenes", prompt)

    def test_other_niches_and_incidental_topic_words_are_unchanged(self):
        self.assertEqual(tech_education_direction("Financial Freedom", "Mountain Trails"), "")
        prompt = PromptEngine.build(self.request("Financial Freedom"))
        self.assertNotIn("AI & TECHNOLOGY EDUCATION:", prompt)

    def test_retry_preserves_learning_accuracy_language_and_visual_rules(self):
        prompt = PromptEngine.build_json_retry(self.request(language="Hindi", content_goal="Shares"))
        for rule in ("plain language", "tradeoffs", "Label conceptual pseudocode", "version assumptions",
                     "technical accuracy and learning", "screen recording", "stock search fields empty",
                     "Hindi means natural Hindi in Devanagari", "content goal", "complete response"):
            self.assertIn(rule, prompt)

    def test_live_topic_ranking_uses_education_without_losing_source_grounding(self):
        result = json.dumps({"topics": [{"title": "Understanding API retries", "language": "en", "source_id": 0}]})
        with patch("app.providers.trend_ai_ranker.generate_user_content", return_value=(result, "model")) as generate:
            TrendAIRanker.rank([{"title": "API retries explained", "language": "en"}],
                               niche="AI & Technology", boundary="APIs", brand="YS Tech: education",
                               platform="Instagram", content_type="Carousel", credentials={"test": {}})
        prompt = generate.call_args.args[1]
        self.assertIn("AI & TECHNOLOGY EDUCATION:", prompt)
        self.assertIn("supported by one supplied source_id", prompt)
        self.assertIn("never fill with evergreen guesses", prompt)


if __name__ == "__main__":
    unittest.main()

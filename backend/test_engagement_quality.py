import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.config.prompt_config import brand_content_direction
from app.schemas.ai import GenerateRequest
from app.services.ai_service import AIService, ContentValidationError
from app.services.prompt_engine import PromptEngine


class EngagementQualityTests(unittest.TestCase):
    def request(self, **changes):
        return GenerateRequest(**dict(project_id=1, platforms=["Instagram"], content_types=["Post"],
                                     niche="AI & Technology", topic="API retries", package="post", **changes))

    def content(self):
        return {"title": "Retrying a payment request", "hook": "A retry can charge your customer twice.",
                "caption": "Keep an idempotency key for payment retries. YS Tech Code explains practical backend decisions.",
                "cta": "Save this check for your next payment integration.",
                "scenes": [{"text": "Retrying a payment? Reuse the idempotency key to prevent duplicate processing.",
                            "voice_text": "Retrying a payment? Reuse the idempotency key to prevent duplicate processing."}]}

    def test_all_six_brands_get_distinct_treatment_without_goal(self):
        cases = {"FinLogic": "usable calculation", "ZenHack": "moment of friction",
                 "PsychoPath.cc": "explained mechanism", "Intimacy Index": "both perspectives",
                 "Cosmic Night": "scale comparison", "YS Tech Code": "failure mode"}
        directions = []
        for name, rule in cases.items():
            brand = SimpleNamespace(name=name, description="", niche="General")
            direction = brand_content_direction("General", brand)
            directions.append(direction)
            prompt = PromptEngine.build(self.request(), brand=brand)
            self.assertIn(rule, prompt)
            self.assertIn("Recurring audience benefit:", prompt)
            self.assertIn("INTERNAL QUALITY GATE", prompt)
            self.assertIn("NATURAL SHARE/SAVE VALUE", prompt)
        self.assertEqual(len(set(directions)), 6)

    def test_custom_brand_and_retry_keep_contract_and_history(self):
        brand = SimpleNamespace(name="Garden Lab", description="Balcony gardening for renters")
        prompt = PromptEngine.build(self.request(), brand=brand,
                                    recent_visuals=[{"hook": "Earlier opening", "cta": "Earlier invitation"}])
        retry = PromptEngine.build_json_retry(self.request(), brand=brand, base_prompt=prompt)
        for value in ("Garden Lab", "Balcony gardening", "Earlier opening", "Earlier invitation",
                      "FOLLOW REASON", "primary invitation", "no scores", "existing JSON shape"):
            self.assertIn(value, retry)

    def test_generic_opening_retries_and_returns_same_fields(self):
        valid = self.content()
        bad = {**valid, "hook": "AI is changing the world."}
        with patch.object(AIService, "_generate_from_provider", side_effect=[
            (json.dumps(bad), "model"), (json.dumps(valid), "model")
        ]) as generate:
            _, _, result = AIService._generate_validated_response("test", self.request(), "prompt")
        self.assertEqual(generate.call_count, 2)
        self.assertIn("Replace the generic opening", generate.call_args.args[1])
        self.assertEqual(set(result), set(valid) | {"script"})

    def test_repeated_generic_failure_is_bounded(self):
        bad = {**self.content(), "hook": "Stay positive!"}
        with patch.object(AIService, "_generate_from_provider", return_value=(json.dumps(bad), "model")) as generate:
            with self.assertRaises(ContentValidationError):
                AIService._generate_validated_response("test", self.request(), "prompt")
        self.assertEqual(generate.call_count, 2)

    def test_specific_explanation_is_not_rejected_for_mentioning_generic_advice(self):
        content = self.content()
        content["hook"] = "Why 'save money every month' fails when rent takes half your salary."
        AIService._validate_content_quality(content)

    def test_existing_fields_and_platform_rules_are_preserved(self):
        for goal in (None, "Reach", "Shares", "Saves", "Comments", "Followers"):
            request = self.request(content_goal=goal)
            prompt = PromptEngine.build(request)
            shape = prompt.split("Use this exact top-level shape:\n", 1)[1].split("\n\nCreate exactly", 1)[0]
            self.assertEqual(set(json.loads(shape)), {"title", "hook", "description", "script", "caption",
                "story", "hashtags", "seo_keywords", "cta", "scenes"})
            self.assertIn("On YouTube keep caption as the short video title", prompt)
            self.assertIn("For quotes and single images", prompt)


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from unittest.mock import patch

from app.schemas.ai import GenerateRequest
from app.services.ai_service import AIService
from app.services.prompt_engine import PromptEngine


class GenerationLanguageTests(unittest.TestCase):
    def request(self, language):
        return GenerateRequest(project_id=1, platforms=["Instagram"], content_types=["Post"],
                               niche="Education", topic="Daily habits", package="complete", scene_count=1, language=language)

    def test_initial_and_retry_prompts_include_language_for_all_copy(self):
        for language in ("Hindi", "English", "Hinglish"):
            for prompt in (PromptEngine.build(self.request(language)), PromptEngine.build_json_retry(self.request(language))):
                self.assertIn(f"Language: {language}", prompt)
                self.assertIn("Write all audience-facing copy", prompt)
                self.assertIn("Hindi means natural Hindi in Devanagari", prompt)
                self.assertIn("Hinglish means a natural Hindi-English mix in Roman script", prompt)
                self.assertIn("must remain English", prompt)

    def test_english_response_to_hindi_request_retries_before_saving(self):
        request = self.request("Hindi")
        bad = {"title": "Daily habits", "scenes": [{"text": "Build a habit every day."}]}
        good = {"title": "रोज़ की आदतें", "scenes": [{"text": "हर दिन एक अच्छी आदत अपनाएं।", "keyword": "person reading book"}]}
        with patch.object(AIService, "_generate_from_provider", side_effect=[(json.dumps(bad), "test"), (json.dumps(good), "test")]) as provider:
            _, _, result = AIService._generate_validated_response("test", request, PromptEngine.build(request))
        self.assertEqual(provider.call_count, 2)
        self.assertEqual(result["script"], good["scenes"][0]["text"])
        self.assertEqual(result["scenes"][0]["keyword"], "person reading book")

    def test_retry_is_bounded_when_model_keeps_ignoring_hindi(self):
        with patch.object(AIService, "_generate_from_provider", return_value=(json.dumps({"title": "Habits", "scenes": [{"text": "Read daily."}]}), "test")) as provider:
            with self.assertRaisesRegex(ValueError, "Devanagari"):
                AIService._generate_validated_response("test", self.request("Hindi"), "prompt")
            self.assertEqual(provider.call_count, 2)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch
from types import SimpleNamespace

from app.services.ai_service import AIService
from app.core.gemini_client import GeminiClient


class AiRecoveryTests(unittest.TestCase):
    def test_truncated_outer_object_does_not_accept_nested_scene(self):
        with self.assertRaises(ValueError):
            AIService._parse_json_response('{"title":"Test","scenes":[{"text":"hello"}')

    def test_fenced_and_surrounded_complete_json(self):
        for text in ('```json\n{"title":"Test"}\n```', 'Result: {"title":"Test"} Done.'):
            self.assertEqual(AIService._parse_json_response(text)["title"], "Test")

    def test_malformed_and_empty_content_retry_once(self):
        for bad in ('{"title":', '{}'):
            with patch.object(AIService, "_generate_from_provider", side_effect=[(bad, "model"), ('{"title":"Recovered","script":"Hello"}', "model")]) as generate, patch("app.services.ai_service.PromptEngine.build_json_retry", return_value="compact retry"):
                _, _, data = AIService._generate_validated_response("test", None, "original")
                self.assertEqual(data["title"], "Recovered")
                self.assertEqual(generate.call_count, 2)
                self.assertEqual(generate.call_args.args, ("test", "compact retry"))

    def test_retry_is_bounded_and_transport_failure_is_not_json_retry(self):
        for error, count in ((ValueError("empty"), 2), (RuntimeError("quota 429"), 1)):
            with patch.object(AIService, "_generate_from_provider", side_effect=error) as generate, patch("app.services.ai_service.PromptEngine.build_json_retry", return_value="retry"):
                with self.assertRaises(type(error)):
                    AIService._generate_validated_response("test", None, "prompt")
                self.assertEqual(generate.call_count, count)

    def test_failure_categories_hide_raw_provider_details(self):
        self.assertEqual(AIService._provider_failure([]).detail["code"], "ai_not_configured")
        for error, code in ((RuntimeError("429 secret-response"), "ai_rate_limit"), (RuntimeError("invalid API key secret-response"), "ai_credentials"), (RuntimeError("connection refused secret-response"), "ai_unavailable"), (RuntimeError("model_not_found secret-response"), "ai_model_unavailable"), (ValueError("secret-response"), "ai_invalid_response")):
            result = AIService._provider_failure([("test", error)])
            self.assertEqual(result.detail["code"], code)
            self.assertNotIn("secret-response", result.detail["message"])

    def test_gemini_uses_configured_model_and_json_mode(self):
        with patch.dict("os.environ", {"GEMINI_MODEL": "configured-model"}), patch("app.core.gemini_client.client.models.generate_content", return_value=SimpleNamespace(text='{"title":"Test"}')) as generate:
            GeminiClient.generate("prompt")
            self.assertEqual(generate.call_args.kwargs["model"], "configured-model")
            self.assertEqual(generate.call_args.kwargs["config"]["response_mime_type"], "application/json")

    def test_auto_mode_reports_cloud_failure_before_local_connection_failure(self):
        result = AIService._provider_failure([("gemini", RuntimeError("429 private-body")), ("ollama", ConnectionError("connection refused"))])
        self.assertEqual(result.detail["code"], "ai_all_providers_failed")
        self.assertIn("gemini:", result.detail["message"])
        self.assertIn("Start Ollama", result.detail["message"])
        self.assertNotIn("private-body", result.detail["message"])


if __name__ == "__main__":
    unittest.main()

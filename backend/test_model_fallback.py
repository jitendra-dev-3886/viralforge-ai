import unittest
from unittest.mock import patch

from app.core.user_ai_client import generate_user_content


class ModelFallbackTests(unittest.TestCase):
    def setUp(self):
        self.credentials = {"api_key": "private-key", "model": "primary", "fallback_models": ["second", "third"]}

    def error(self, status):
        error = RuntimeError("private response")
        error.status_code = status
        return error

    @patch("app.core.user_ai_client._generate_single_model")
    def test_tries_models_in_order_and_reports_successful_model(self, generate):
        generate.side_effect = [self.error(404), self.error(429), ('{"ok":true}', "third")]
        result = generate_user_content("groq", "prompt", self.credentials, max_tokens=2000)
        self.assertEqual(result[1], "third")
        self.assertEqual([call.args[2]["model"] for call in generate.call_args_list], ["primary", "second", "third"])
        self.assertTrue(all(call.kwargs["max_tokens"] == 2000 for call in generate.call_args_list))
        self.assertEqual(self.credentials["model"], "primary")

    @patch("app.core.user_ai_client._generate_single_model")
    def test_invalid_json_falls_back(self, generate):
        generate.side_effect = [("not JSON", "primary"), ('```json\n{"ok":true}\n```', "second")]
        self.assertEqual(generate_user_content("gemini", "prompt", self.credentials)[1], "second")
        self.assertEqual(generate.call_count, 2)

    @patch("app.core.user_ai_client._generate_single_model")
    def test_account_failures_do_not_fan_out(self, generate):
        for status in (401, 402, 403):
            generate.reset_mock()
            generate.side_effect = self.error(status)
            with self.assertRaises(RuntimeError):
                generate_user_content("cerebras", "prompt", self.credentials)
            self.assertEqual(generate.call_count, 1)

    @patch("app.core.user_ai_client._generate_single_model")
    def test_model_permission_failure_can_fall_back(self, generate):
        error = self.error(403)
        error.access_reason = "project_model_blocked"
        generate.side_effect = [error, ('{"ok":true}', "second")]
        self.assertEqual(generate_user_content("groq", "prompt", self.credentials)[1], "second")

    @patch("app.core.user_ai_client._generate_single_model")
    def test_all_models_fail_bounded_and_preserve_status(self, generate):
        generate.side_effect = self.error(429)
        with self.assertRaises(RuntimeError) as caught:
            generate_user_content("groq", "prompt", self.credentials)
        self.assertEqual(caught.exception.status_code, 429)
        self.assertEqual(generate.call_count, 3)


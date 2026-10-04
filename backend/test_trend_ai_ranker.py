import json
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from fastapi import HTTPException
from app.core.user_ai_client import generate_user_content, ProviderTruncatedResponse
from app.providers.trend_ai_ranker import TrendAIRanker


class TrendRankerTests(unittest.TestCase):
    def rank(self):
        return TrendAIRanker.rank([{"title": "API retries explained"}], niche="Technology",
                                  boundary="Technology", brand="", platform="instagram", content_type="reel",
                                  credentials={"groq": {"api_key": "secret", "model": "model"}})

    def test_length_finish_is_classified_as_truncation(self):
        response = SimpleNamespace(status_code=200, json=lambda: {"choices": [{"finish_reason": "length"}]})
        with patch("app.core.user_ai_client.requests.post", return_value=response):
            with self.assertRaises(ProviderTruncatedResponse):
                generate_user_content("groq", "prompt", {"api_key": "secret", "model": "model"})

    @patch("app.providers.trend_ai_ranker.generate_user_content")
    def test_truncated_topics_retry_with_larger_budget(self, generate):
        generate.side_effect = [ProviderTruncatedResponse("truncated"),
                               (json.dumps({"topics": [{"title": "How API retries work", "language": "en", "source_id": 0}]}), "model")]
        self.assertEqual(len(self.rank()), 1)
        self.assertEqual([call.kwargs["max_tokens"] for call in generate.call_args_list], [4096, 8192])

    @patch("app.providers.trend_ai_ranker.generate_user_content")
    def test_access_failure_is_actionable_and_not_retried(self, generate):
        error = RuntimeError("secret response")
        error.status_code = 403
        error.access_reason = "project_model_blocked"
        generate.side_effect = error
        with self.assertRaises(HTTPException) as caught:
            self.rank()
        self.assertEqual(caught.exception.detail["code"], "ai_project_model_blocked")
        self.assertNotIn("secret", str(caught.exception.detail))
        self.assertEqual(generate.call_count, 1)

    @patch("app.providers.trend_ai_ranker.generate_user_content")
    def test_truncation_retry_is_bounded(self, generate):
        generate.side_effect = ProviderTruncatedResponse("truncated")
        with self.assertRaises(HTTPException) as caught:
            self.rank()
        self.assertEqual(generate.call_count, 2)
        self.assertEqual(caught.exception.detail["code"], "ai_response_truncated")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import Mock, patch

from app.services.publishing_accounts import ProviderError, request


class PublishingErrorTests(unittest.TestCase):
    def rejection(self, body, url="https://graph.instagram.com/v23.0/123/media", status=400):
        response = Mock(status_code=status)
        response.json.return_value = body
        with patch("app.services.publishing_accounts.requests.request", return_value=response):
            with self.assertRaises(ProviderError) as caught:
                request("POST", url, headers={"Authorization": "Bearer private-token"})
        return caught.exception

    def test_instagram_codes_and_stage_survive_without_provider_text(self):
        error = self.rejection({"error": {"code": 9004, "error_subcode": 2207052, "message": "secret private-token https://private.example", "error_user_msg": "private-token"}})
        self.assertIn("Instagram rejected media preparation", str(error))
        self.assertIn("HTTP 400, code 9004, subcode 2207052", str(error))
        self.assertNotIn("private", str(error))
        self.assertFalse(error.uncertain)

    def test_publication_and_auth_errors_keep_correct_flags(self):
        error = self.rejection({"error": {"code": 190, "error_subcode": 463}}, url="https://graph.instagram.com/v23.0/123/media_publish?access_token=secret")
        self.assertIn("publication", str(error))
        self.assertTrue(error.reconnect)
        self.assertNotIn("secret", str(error))
        self.assertTrue(self.rejection({"error": "invalid_grant"}).reconnect)
        self.assertTrue(self.rejection({}, status=503).uncertain)

    def test_malformed_bodies_and_untrusted_codes_do_not_leak_or_crash(self):
        for body in ([], None, {"error": []}, {"error": {"code": {"token": "private-token"}, "error_subcode": "private-token"}}):
            with self.subTest(body=body):
                error = self.rejection(body)
                self.assertIn("HTTP 400", str(error))
                self.assertNotIn("private-token", str(error))

    def test_only_instagram_media_creation_timeout_is_retryable(self):
        body = {"error": {"code": -2, "error_subcode": 2207003}}
        error = self.rejection(body)
        self.assertTrue(error.retryable)
        self.assertIn("too long to download", str(error))
        self.assertNotIn("quota", str(error))
        for url in ("https://graph.instagram.com/v23.0/123/media_publish", "https://graph.facebook.com/v23.0/123/media", "https://graph.instagram.com/access_token"):
            with self.subTest(url=url):
                self.assertFalse(self.rejection(body, url=url).retryable)
        self.assertFalse(self.rejection(body, status=500).retryable)
        self.assertFalse(self.rejection({"error": {"code": 190}}).retryable)


if __name__ == "__main__":
    unittest.main()

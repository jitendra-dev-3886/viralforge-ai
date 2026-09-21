import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app import models
from app.database import Base, get_db
from app.core.security import get_current_user_id
from app.api.ai_settings import router
from app.models.api_setting import ApiSetting
from app.services.user_ai_settings import credentials_for
from app.services.ai_service import AIService
from app.core.user_ai_client import generate_user_content
from app.schemas.ai import GenerateRequest


class UserAiTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.engine = engine
        self.key_patch = patch.dict("os.environ", {"API_CREDENTIAL_ENCRYPTION_KEY": Fernet.generate_key().decode()})
        self.key_patch.start()
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = lambda: self.db
        self.user = 1
        app.dependency_overrides[get_current_user_id] = lambda: self.user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.db.close()
        self.engine.dispose()
        self.key_patch.stop()

    def test_keys_are_encrypted_and_never_returned(self):
        response = self.client.put("/api/ai-settings/groq", json={"api_key": "private-user-key", "model": "my-model"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("private-user-key", response.text)
        row = self.db.query(ApiSetting).first()
        self.assertTrue(row.api_key.startswith("enc:v1:"))
        self.assertNotIn("private-user-key", row.api_key)
        self.assertEqual(credentials_for(self.db, 1)["groq"]["api_key"], "private-user-key")
        self.assertNotIn("enc:v1", self.client.get("/api/ai-settings/").text)

    def test_pasted_header_is_normalized_and_masked_key_is_rejected(self):
        response = self.client.put("/api/ai-settings/openrouter", json={"api_key": '"Bearer private-key"', "model": "org/model"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(credentials_for(self.db, 1)["openrouter"]["api_key"], "private-key")
        response = self.client.put("/api/ai-settings/openrouter", json={"api_key": "********", "model": "org/model"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(credentials_for(self.db, 1)["openrouter"]["api_key"], "private-key")

    def test_provider_test_uses_only_current_users_saved_credentials(self):
        self.client.put("/api/ai-settings/openrouter", json={"api_key": "personal-key", "model": "org/model"})
        with patch("app.core.user_ai_client.generate_user_content", return_value=('{"ok":true}', "org/model")) as generate:
            response = self.client.post("/api/ai-settings/openrouter/test")
            self.assertEqual(response.status_code, 200, response.text)
            self.assertNotIn("personal-key", response.text)
            self.assertEqual(generate.call_args.args[2], {"api_key": "personal-key", "model": "org/model"})
            self.user = 2
            self.assertEqual(self.client.post("/api/ai-settings/openrouter/test").status_code, 400)
            self.assertEqual(generate.call_count, 1)

    def test_explicit_provider_auth_prevents_netrc_override(self):
        import requests
        from app.core.user_ai_client import ProviderAuth
        with patch("requests.sessions.get_netrc_auth", return_value=("local-user", "local-password")) as netrc:
            with requests.Session() as session:
                request = session.prepare_request(requests.Request("POST", "https://openrouter.ai/api/v1/chat/completions", auth=ProviderAuth("personal-key")))
            netrc.assert_not_called()
            self.assertEqual(request.headers["Authorization"], "Bearer personal-key")

    def test_provider_status_is_preserved_without_leaking_response(self):
        for status, code in ((401, "ai_credentials"), (403, "ai_access_denied"), (402, "ai_credits_required"), (429, "ai_rate_limit"), (400, "ai_request_rejected")):
            response = SimpleNamespace(status_code=status, json=lambda: {"error": {"message": "private-key"}})
            with patch("app.core.user_ai_client.requests.post", return_value=response), patch("app.core.user_ai_client.requests.get", return_value=SimpleNamespace(status_code=401)):
                with self.assertRaises(RuntimeError) as caught:
                    generate_user_content("openrouter", "prompt", {"api_key": "personal-key", "model": "model"})
            failure = AIService._provider_failure([("openrouter", caught.exception)])
            self.assertEqual(failure.detail["code"], code)
            self.assertEqual(failure.detail["provider_status"], status)
            self.assertNotIn("private-key", str(failure.detail))

    def test_openrouter_management_key_has_actionable_error(self):
        with patch("app.core.user_ai_client.requests.post", return_value=SimpleNamespace(status_code=401)), patch("app.core.user_ai_client.requests.get", return_value=SimpleNamespace(status_code=200, json=lambda: {"data": {"is_management_key": True}})):
            with self.assertRaises(RuntimeError) as caught:
                generate_user_content("openrouter", "prompt", {"api_key": "private-key", "model": "model"})
        failure = AIService._provider_failure([("openrouter", caught.exception)])
        self.assertEqual(failure.detail["code"], "ai_wrong_key_type")
        self.assertIn("management/provisioning key", failure.detail["message"])
        self.assertNotIn("private-key", str(failure.detail))

    def test_users_cannot_read_use_update_or_delete_each_others_keys(self):
        self.client.put("/api/ai-settings/groq", json={"api_key": "user-one", "model": "model-one"})
        self.user = 2
        self.assertEqual(self.client.get("/api/ai-settings/").json()["providers"], [])
        self.assertEqual(self.client.put("/api/ai-settings/groq", json={"model": "overwrite"}).status_code, 422)
        self.client.delete("/api/ai-settings/groq")
        self.client.put("/api/ai-settings/groq", json={"api_key": "user-two", "model": "model-two"})
        self.assertEqual(credentials_for(self.db, 1)["groq"]["api_key"], "user-one")
        self.assertEqual(credentials_for(self.db, 2)["groq"]["api_key"], "user-two")

    def test_disabled_missing_and_local_providers_cannot_fall_back_to_server(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": "server-key"}):
            for requested in (None, ["groq"], ["ollama"]):
                with self.assertRaises(Exception) as error:
                    credentials_for(self.db, 1, requested)
                self.assertEqual(error.exception.status_code, 400)
        self.client.put("/api/ai-settings/groq", json={"api_key": "user-one", "model": "model-one", "is_active": False})
        with self.assertRaises(Exception):
            credentials_for(self.db, 1)
        with self.assertRaises(ValueError):
            AIService._generate_from_provider("groq", "prompt")

    def test_blank_key_preserves_existing_secret_and_delete_revokes_it(self):
        self.client.put("/api/ai-settings/groq", json={"api_key": "saved-key", "model": "old-model"})
        self.client.put("/api/ai-settings/groq", json={"model": "new-model"})
        self.assertEqual(credentials_for(self.db, 1)["groq"], {"api_key": "saved-key", "model": "new-model"})
        self.client.delete("/api/ai-settings/groq")
        with self.assertRaises(Exception):
            credentials_for(self.db, 1)

    def test_concurrent_requests_use_their_own_model_and_key(self):
        def fake_post(url, headers, json, **kwargs):
            self.assertEqual(headers["Authorization"], f"Bearer key-{json['model']}")
            return SimpleNamespace(status_code=200, json=lambda: {"choices": [{"message": {"content": '{"title":"ok"}'}, "finish_reason": "stop"}]})
        with patch("app.core.user_ai_client.requests.post", side_effect=fake_post), ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda model: generate_user_content("groq", "prompt", {"api_key": f"key-{model}", "model": model}), ["one", "two"]))
        self.assertEqual([item[1] for item in results], ["one", "two"])

    def test_configuration_api_requires_login(self):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = lambda: self.db
        with TestClient(app) as client:
            for method, path, body in (("get", "/api/ai-settings/", None), ("put", "/api/ai-settings/groq", {"model": "x", "api_key": "secret"}), ("delete", "/api/ai-settings/groq", None)):
                response = client.request(method, path, **({"json": body} if body else {}))
                self.assertIn(response.status_code, (401, 403))

    def test_generation_without_personal_settings_makes_no_provider_request(self):
        request = GenerateRequest(project_id=1, platforms=["Instagram"], content_types=["Reel"], niche="Education", topic="Learning", package="reel")
        db = MagicMock()
        with patch("app.services.user_ai_settings.settings_for", return_value=[]), patch("app.services.ai_service.generate_user_content") as provider:
            with self.assertRaises(Exception) as error:
                AIService.generate(request, db, 1)
            self.assertEqual(error.exception.status_code, 400)
            provider.assert_not_called()

    def test_new_providers_save_and_cloudflare_requires_scoped_account(self):
        for provider in ("mistral", "huggingface", "cloudflare"):
            payload = {"api_key": f"key-{provider}", "model": "@cf/test-model" if provider == "cloudflare" else "org/chat-model"}
            if provider == "cloudflare":
                self.assertEqual(self.client.put(f"/api/ai-settings/{provider}", json=payload).status_code, 422)
                payload["account_id"] = "a" * 32
            response = self.client.put(f"/api/ai-settings/{provider}", json=payload)
            self.assertEqual(response.status_code, 200, response.text)
            credentials = credentials_for(self.db, 1, [provider])[provider]
            self.assertEqual(credentials["api_key"], f"key-{provider}")
            if provider == "cloudflare":
                self.assertEqual(credentials["account_id"], "a" * 32)
                self.client.put("/api/ai-settings/cloudflare", json={"model": "@cf/updated"})
                self.assertEqual(credentials_for(self.db, 1, [provider])[provider]["account_id"], "a" * 32)
            self.user = 2
            with self.assertRaises(Exception):
                credentials_for(self.db, 2, [provider])
            self.user = 1

    def test_new_adapters_use_fixed_urls_json_mode_and_user_credentials(self):
        endpoints = {
            "mistral": "https://api.mistral.ai/v1/chat/completions",
            "huggingface": "https://router.huggingface.co/v1/chat/completions",
            "cloudflare": f"https://api.cloudflare.com/client/v4/accounts/{'a' * 32}/ai/v1/chat/completions",
        }
        response = SimpleNamespace(status_code=200, json=lambda: {"choices": [{"message": {"content": '{"title":"ok"}'}, "finish_reason": "stop"}]})
        for provider, endpoint in endpoints.items():
            with patch("app.core.user_ai_client.requests.post", return_value=response) as post:
                text, model = generate_user_content(provider, "prompt", {"api_key": "personal-key", "model": "selected-model", "account_id": "a" * 32})
                self.assertEqual(json.loads(text)["title"], "ok")
                self.assertEqual(post.call_args.args[0], endpoint)
                self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer personal-key")
                self.assertEqual(post.call_args.kwargs["json"]["response_format"], {"type": "json_object"})
                self.assertEqual(model, "selected-model")
        with patch("app.core.user_ai_client.requests.post") as post:
            with self.assertRaises(ValueError):
                generate_user_content("cloudflare", "prompt", {"api_key": "key", "model": "model", "account_id": "../another-account"})
            post.assert_not_called()


if __name__ == "__main__":
    unittest.main()

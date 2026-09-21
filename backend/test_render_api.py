import subprocess
import sys
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.api.render import router as render_router
from app.api.project_render import router as project_router
from app.core.security import get_current_user_id
from app.database import get_db


class RenderApiTests(unittest.TestCase):
    def test_prompt_catalog_does_not_initialize_pillow_before_text_shaping(self):
        result = subprocess.run([sys.executable, "-c",
            "from app.services.prompt_engine import PromptEngine; "
            "from app.core.text_overlay import features; "
            "assert features.check_feature('raqm'), 'API import order disabled text shaping'"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_render_failures_remain_readable_by_browser(self):
        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])
        app.include_router(render_router)
        app.include_router(project_router)
        app.dependency_overrides[get_current_user_id] = lambda: 1
        app.dependency_overrides[get_db] = lambda: None
        cases = [
            ("/api/render/image", {"scene_id": 1}, "app.api.render.RenderService.generate"),
            ("/api/render/generate", {"scene_id": 1}, "app.api.render.RenderService.generate"),
            ("/api/project-render/generate", {"project_id": 1, "content_id": 1}, "app.api.project_render.ProjectRenderService.generate"),
        ]
        with patch("app.services.billing_service.billed_render", side_effect=lambda operation, **kwargs: operation(**{k: v for k, v in kwargs.items() if k != "request_key"})), TestClient(app, raise_server_exceptions=False) as client:
            for endpoint, payload, target in cases:
                for error, status in [(RuntimeError("Text shaping unavailable"), 422), (Exception("encoder failure"), 500)]:
                    with self.subTest(endpoint=endpoint, status=status), patch(target, side_effect=error), self.assertLogs("app.core.render_errors", level="ERROR"):
                        response = client.post(endpoint, json=payload, headers={"Origin": "http://localhost:5173"})
                    self.assertEqual(response.status_code, status)
                    self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")
                    self.assertIsInstance(response.json()["detail"], str)


if __name__ == "__main__":
    unittest.main()

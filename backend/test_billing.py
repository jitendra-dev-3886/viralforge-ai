import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.database import Base, get_db
from app.models.user import User
from app.models.brand import Brand
from app.models.project import Project
from app.models.content import Content
from app.models.scene import Scene
from app.models.subscription import Subscription
from app.models.billing import BillingPlan, ExportUsage, PlanGrant
from app.services import billing_service as billing
from app.api.billing import router
from app.api.render import router as render_router
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.schemas.auth import LoginRequest
from app.core.security import get_current_user_id


class BillingTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.engine = create_engine(f"sqlite:///{Path(self.folder.name) / 'test.db'}", connect_args={"check_same_thread": False, "timeout": 10})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.db.add_all([User(id=1, name="Creator", email="creator@example.test"), User(id=2, name="Other", email="other@example.test"), User(id=3, name="Admin", email="admin@example.test", is_super_admin=True)])
        self.db.commit()
        billing.seed_plans(self.db)
        for owner in (1, 2):
            self.db.add(Project(id=owner, user_id=owner, title="Project", topic="Topic", platform="Instagram", content_type="Carousel", folder="test", path="test"))
            self.db.add(Content(id=owner, user_id=owner, project_id=owner, title="Content", script="Script", platform="Instagram", content_type="Carousel", generation_config={"audio": {"voice_enabled": False}}))
            self.db.add(Scene(id=owner, user_id=owner, project_id=owner, content_id=owner, scene_number=1, text="Hello", duration=10))
        self.db.add(Scene(id=3, user_id=1, project_id=1, content_id=1, scene_number=2, text="Second", duration=15))
        self.db.commit()
        self.user = 1
        app = FastAPI()
        app.include_router(router)
        app.include_router(render_router)
        app.include_router(admin_router)
        app.include_router(auth_router)
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user_id] = lambda: self.user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.db.close()
        self.engine.dispose()
        self.folder.cleanup()

    def completed(self, kind, units, key):
        row, _ = billing.reserve(self.db, 1, kind, units, "test", key)
        row.status, row.active_user = "completed", None
        row.result = {"success": True}
        self.db.commit()
        return row

    def test_trial_is_one_time_and_expiry_blocks_new_work(self):
        first = billing.snapshot(self.db, 1)
        self.assertEqual(first["plan"]["code"], "trial")
        self.assertIsNone(first["plan"]["video_exports"])
        self.assertFalse(first["payments_enabled"])
        self.assertEqual(first["starts_at"], billing.snapshot(self.db, 1)["starts_at"])
        sub = self.db.query(Subscription).filter_by(user_id=1).one()
        sub.expires_at = billing.now() - timedelta(seconds=1)
        self.db.commit()
        with self.assertRaises(HTTPException):
            billing.require_plan(self.db, 1)
        self.db.rollback()
        self.assertEqual(billing.snapshot(self.db, 1)["status"], "expired")
        self.assertEqual(self.db.query(Content).filter_by(user_id=1).count(), 1)

    def test_trial_video_and_image_allowances_are_independent(self):
        for index in range(5):
            self.completed("video", 10, f"video-{index}")
        self.assertEqual(billing.snapshot(self.db, 1)["usage"]["video_exports"], 5)
        self.completed("image", 10, "images")
        with self.assertRaises(HTTPException):
            billing.reserve(self.db, 1, "image", 1, "test", "extra-image")

    def test_brand_creation_cannot_exceed_plan(self):
        billing.check_brand_limit(self.db, 1)
        self.db.add(Brand(user_id=1, name="First"))
        self.db.commit()
        with self.assertRaises(HTTPException):
            billing.check_brand_limit(self.db, 1)

    def test_startup_removes_existing_trial_cap(self):
        self.db.get(BillingPlan, "trial").video_exports = 3
        self.db.commit()
        billing.seed_plans(self.db)
        billing.seed_plans(self.db)
        self.assertIsNone(billing.snapshot(self.db, 1)["plan"]["video_exports"])
        for index in range(5):
            self.completed("video", 10, f"existing-{index}")

    @patch.dict("os.environ", {"SUPER_ADMIN_EMAIL": ""})
    def test_owner_can_grant_access_and_delegate_admin(self):
        owner = self.db.get(User, 2)
        owner.email = "ystechlab@gmail.com"
        self.db.commit()
        self.user = 2
        self.assertTrue(self.client.get("/api/auth/me").json()["user"]["is_super_admin"])
        response = self.client.put("/api/admin/users/1", json={"is_super_admin": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.user = 1
        response = self.client.post("/api/billing/admin/users/2/grant", json={"plan": "pro", "note": "Owner access granted"})
        self.assertEqual(response.status_code, 200, response.text)

    def test_normal_user_cannot_change_permissions(self):
        response = self.client.put("/api/admin/users/2", json={"is_super_admin": True})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.db.get(User, 2).is_super_admin)

    @patch.dict("os.environ", {"SUPER_ADMIN_EMAIL": ""})
    def test_owner_password_login_promotes_only_after_authentication(self):
        owner = self.db.get(User, 2)
        owner.email, owner.hashed_password = "ystechlab@gmail.com", "$2test"
        self.db.commit()
        request = LoginRequest(email=owner.email, password="test-password")
        with patch("app.services.auth_service.verify_password", return_value=False):
            self.assertFalse(AuthService.login(self.db, request)["success"])
            self.assertFalse(owner.is_super_admin)
        with patch("app.services.auth_service.verify_password", return_value=True):
            self.assertTrue(AuthService.login(self.db, request)["user"]["is_super_admin"])

    @patch.dict("os.environ", {"SUPER_ADMIN_EMAIL": ""})
    def test_owner_google_login_gets_admin_access(self):
        user, _ = OAuthService.login(self.db, "google", {"id": "owner-google", "email": "ystechlab@gmail.com", "name": "Owner", "data": {"email_verified": True}})
        self.assertTrue(user.is_super_admin)

    def test_completed_request_replays_without_rendering_or_charging_again(self):
        render = Mock(return_value={"success": True, "media_id": 44})
        args = dict(db=self.db, user_id=1, scene_id=1, as_image=True, request_key="retry")
        first = billing.billed_render(render, **args)
        self.assertEqual(billing.billed_render(render, **args), first)
        self.assertEqual(render.call_count, 1)
        self.assertEqual(billing.snapshot(self.db, 1)["usage"]["image_exports"], 1)

    def test_failed_batch_refunds_every_slide_and_can_retry(self):
        args = dict(db=self.db, user_id=1, scene_ids=[1, 3], as_image=True, request_key="batch")
        with self.assertRaises(RuntimeError):
            billing.billed_render(Mock(side_effect=RuntimeError("encoder failed")), **args)
        self.assertEqual(billing.snapshot(self.db, 1)["usage"]["image_exports"], 0)
        billing.billed_render(Mock(return_value={"success": True, "media_ids": [11, 12]}), **args)
        self.assertEqual(billing.snapshot(self.db, 1)["usage"]["image_exports"], 2)

    def test_batch_rejects_another_users_scene(self):
        render = Mock()
        with self.assertRaises(HTTPException):
            billing.billed_render(render, db=self.db, user_id=1, scene_ids=[1, 2], as_image=True)
        render.assert_not_called()

    def test_pending_reservation_blocks_a_concurrent_export(self):
        billing.snapshot(self.db, 1)
        def attempt(key):
            with self.Session() as db:
                try:
                    billing.reserve(db, 1, "image", 1, "scene:1", key)
                    return 200
                except HTTPException as error:
                    db.rollback()
                    return error.status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(attempt, ["one", "two"]))
        self.assertEqual(sorted(statuses), [200, 409])

    def test_manual_grant_is_admin_only_and_no_fake_payment(self):
        payload = {"plan": "pro", "note": "Pilot invitation"}
        self.assertEqual(self.client.post("/api/billing/admin/users/1/grant", json=payload).status_code, 403)
        self.user = 3
        response = self.client.post("/api/billing/admin/users/1/grant", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["plan"]["video_seconds"], 5400)
        self.assertEqual(self.db.query(Subscription).filter_by(user_id=1).one().amount, 0)
        self.assertEqual(self.db.query(PlanGrant).count(), 1)
        self.assertEqual(self.client.post("/api/billing/admin/users/1/grant", json=payload).status_code, 409)

    def test_creator_minutes_and_new_grant_period(self):
        billing.grant_plan(self.db, 1, 3, "creator", "Pilot invitation")
        self.completed("video", 1800, "all-minutes")
        with self.assertRaises(HTTPException):
            billing.reserve(self.db, 1, "video", 1, "test", "over")
        self.db.rollback()
        sub = self.db.query(Subscription).filter_by(user_id=1).one()
        sub.expires_at = billing.now() - timedelta(seconds=1)
        self.db.commit()
        result = billing.grant_plan(self.db, 1, 3, "creator", "Next pilot period")
        self.assertEqual(result["usage"]["video_seconds"], 0)
        self.assertEqual(self.db.query(ExportUsage).count(), 1)

    def test_interrupted_export_requires_admin_confirmation_to_release(self):
        row, _ = billing.reserve(self.db, 1, "image", 2, "batch", "interrupted")
        url = f"/api/billing/admin/exports/{row.id}/release"
        self.assertEqual(self.client.post(url, json={"confirmed_stopped": True}).status_code, 403)
        self.user = 3
        self.assertEqual(self.client.post(url, json={"confirmed_stopped": False}).status_code, 422)
        self.assertEqual(self.client.post(url, json={"confirmed_stopped": True}).status_code, 200)
        self.assertEqual(billing.snapshot(self.db, 1)["usage"]["image_exports"], 0)
        self.assertEqual(self.client.post(url, json={"confirmed_stopped": True}).status_code, 409)

    def test_blank_grant_reason_is_rejected(self):
        self.user = 3
        response = self.client.post("/api/billing/admin/users/1/grant", json={"plan": "creator", "note": "     "})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.db.query(PlanGrant).count(), 0)

    def test_api_enforces_quotas_before_rendering_and_accounts_are_isolated(self):
        self.completed("image", 10, "full")
        with patch("app.api.render.RenderService.generate") as render:
            response = self.client.post("/api/render/image", json={"scene_id": 1})
            self.assertEqual(response.status_code, 403, response.text)
            render.assert_not_called()
        self.db.rollback()
        self.user = 2
        self.assertEqual(self.client.get("/api/billing/me").json()["usage"]["image_exports"], 0)
        self.assertEqual(self.client.get("/api/billing/history").json()["exports"], [])

    def test_rendered_project_reserves_total_scene_duration_once(self):
        render = Mock(return_value={"success": True, "media_id": 5})
        billing.billed_render(render, db=self.db, user_id=1, project_id=1, content_id=1)
        usage = billing.snapshot(self.db, 1)["usage"]
        self.assertEqual(usage["video_seconds"], 25)
        self.assertEqual(usage["video_exports"], 1)


if __name__ == "__main__":
    unittest.main()

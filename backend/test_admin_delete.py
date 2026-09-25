"""Admin deletion uses only an isolated SQLite database, with FK checks enabled."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.api.admin import router
from app.core.security import create_access_token, get_current_user_id
from app.database import Base, get_db


class AdminDeleteTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        event.listen(self.engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add_all([
            models.User(id=1, name="Admin", email="admin@example.test", is_super_admin=True),
            models.User(id=2, name="Target", email="target@example.test"),
            models.User(id=3, name="Other", email="other@example.test"),
            models.User(id=4, name="Owner", email="ystechlab@gmail.com"),
            models.User(id=5, name="Admin Two", email="admin2@example.test", is_super_admin=True),
        ])
        self.db.commit()
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = lambda: self.db

        @app.get("/authenticated")
        def authenticated(user_id: int = Depends(get_current_user_id)):
            return {"id": user_id}

        self.client = TestClient(app)
        self.headers = self.auth(1)

    def tearDown(self):
        self.client.close()
        self.db.close()
        self.engine.dispose()

    def auth(self, user_id):
        return {"Authorization": "Bearer " + create_access_token({"user_id": user_id})}

    def seed_workspace(self, owner):
        now = datetime.now(timezone.utc)
        rows = [
            (models.Brand, dict(id=owner, name="Brand")),
            (models.Project, dict(id=owner, brand_id=owner, title="Project", topic="Topic", platform="Instagram", content_type="Post", folder="test", path="test")),
            (models.Content, dict(id=owner, project_id=owner, title="Content", script="Script", platform="Instagram", content_type="Post")),
            (models.Media, dict(id=owner, project_id=owner, media_type="image", file_name="test.png", file_path="test.png")),
            (models.Scene, dict(id=owner, project_id=owner, content_id=owner, media_id=owner, scene_number=1, text="Scene")),
            (models.Image, dict(project_id=owner, content_id=owner, scene_id=owner, prompt="Image")),
            (models.Voice, dict(project_id=owner, content_id=owner, scene_id=owner, voice="test", text="Voice")),
            (models.Schedule, dict(id=owner, project_id=owner, content_id=owner, platform="Instagram", scheduled_at=now)),
            (models.PublishingAccount, dict(id=owner, provider="instagram", remote_id=str(owner), name="Account", access_token="encrypted-fixture", status="connected")),
            (models.PublishingOAuthState, dict(state_hash=str(owner), browser_hash="browser", provider="instagram", expires_at=now + timedelta(minutes=10))),
            (models.PublishJob, dict(id=owner, schedule_id=owner, account_id=owner, request_key=str(owner), status="published", payload={}, provider_state={}, next_attempt_at=now)),
            (models.Subscription, dict(plan_name="trial")),
            (models.Usage, dict(feature="test")),
            (models.ApiSetting, dict(provider="test", api_key="test-only")),
            (models.SocialAccount, dict(provider="test", provider_user_id=str(owner))),
            (models.Trend, dict(title="Trend")),
            (models.Niche, dict(name="Niche")),
            (models.ExportUsage, dict(id=str(owner), request_key="test", resource="test", kind="image", units=1, period_start=now, status="completed", created_at=now)),
            (models.PlanGrant, dict(admin_id=1, plan_code="trial", starts_at=now, expires_at=now + timedelta(days=7), note="Test grant")),
        ]
        for model, values in rows:
            self.db.execute(model.__table__.insert().values(user_id=owner, **values))
        self.db.add(models.PublishEvent(job_id=owner, status="published", message="Test publication"))
        self.db.commit()

    def test_delete_cleans_all_owned_records_and_preserves_other_user(self):
        self.seed_workspace(2)
        self.seed_workspace(3)
        response = self.client.delete("/api/admin/users/2", headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["success"])
        for table in Base.metadata.sorted_tables:
            if "user_id" in table.c:
                self.assertEqual(self.db.scalar(select(func.count()).select_from(table).where(table.c.user_id == 2)), 0, table.name)
                self.assertEqual(self.db.scalar(select(func.count()).select_from(table).where(table.c.user_id == 3)), 1, table.name)
        self.assertEqual(self.client.get("/authenticated", headers=self.auth(2)).status_code, 401)
        self.assertEqual(self.db.query(models.PublishEvent).filter_by(job_id=2).count(), 0)
        self.assertEqual(self.db.query(models.PublishEvent).filter_by(job_id=3).count(), 1)
        self.assertEqual(self.client.get("/authenticated", headers=self.auth(3)).status_code, 200)
        self.assertEqual(self.client.get("/api/admin/overview", headers=self.headers).json()["counts"]["users"], 4)
        self.assertEqual(self.client.delete("/api/admin/users/2", headers=self.headers).status_code, 404)

    def test_permissions_and_protected_accounts(self):
        self.assertIn(self.client.delete("/api/admin/users/2").status_code, (401, 403))
        self.assertEqual(self.client.delete("/api/admin/users/2", headers=self.auth(3)).status_code, 403)
        for target in (1, 4, 5):
            self.assertEqual(self.client.delete(f"/api/admin/users/{target}", headers=self.headers).status_code, 400)
        self.assertEqual(self.client.delete("/api/admin/users/999", headers=self.headers).status_code, 404)
        rows = self.client.get("/api/admin/users", headers=self.headers).json()["users"]
        reasons = {row["id"]: row["delete_blocked_reason"] for row in rows}
        self.assertIsNone(reasons[2])
        self.assertTrue(all(reasons[key] for key in (1, 4, 5)))
        self.db.query(models.User).filter_by(id=1).update({"is_active": False})
        self.db.commit()
        self.assertEqual(self.client.delete("/api/admin/users/2", headers=self.headers).status_code, 401)

    def test_active_export_blocks_deletion(self):
        self.seed_workspace(2)
        self.db.query(models.ExportUsage).filter_by(user_id=2).update({"status": "reserved"})
        self.db.commit()
        self.assertEqual(self.client.delete("/api/admin/users/2", headers=self.headers).status_code, 409)
        self.assertEqual(self.db.query(models.Project).filter_by(user_id=2).count(), 1)

    def test_issued_grants_are_preserved(self):
        self.seed_workspace(3)
        self.db.query(models.PlanGrant).filter_by(user_id=3).update({"admin_id": 2})
        self.db.commit()
        self.assertEqual(self.client.delete("/api/admin/users/2", headers=self.headers).status_code, 409)
        self.assertEqual(self.db.query(models.PlanGrant).filter_by(admin_id=2).count(), 1)

    def test_database_failure_rolls_back_all_deletions(self):
        self.seed_workspace(2)
        with patch.object(self.db, "commit", side_effect=IntegrityError("test", {}, Exception("constraint"))):
            response = self.client.delete("/api/admin/users/2", headers=self.headers)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.db.query(models.User).filter_by(id=2).count(), 1)
        self.assertEqual(self.db.query(models.Voice).filter_by(user_id=2).count(), 1)
        self.assertEqual(self.db.query(models.PlanGrant).filter_by(user_id=2).count(), 1)


if __name__ == "__main__":
    unittest.main()

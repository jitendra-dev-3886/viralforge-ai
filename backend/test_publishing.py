import os
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from uuid import uuid4
from unittest.mock import patch, Mock

from cryptography.fernet import Fernet
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.database import Base
from app.models.user import User
from app.models.project import Project
from app.models.content import Content
from app.models.media import Media
from app.models.schedule import Schedule
from app.models.publishing import PublishingAccount, PublishingOAuthState, PublishJob, PublishEvent
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.api.schedule import create_schedule, update_schedule, delete_schedule, list_schedules, schedule_events
from app.api.social_connections import list_connections, disconnect
from app.services.publishing_accounts import PublishingAccounts, ProviderError, encrypt, decrypt, now, api
from app.services.publishing_worker import process_job
from app.services.publishing_providers import Pending, instagram, youtube, facebook


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {"PUBLISHING_ENCRYPTION_KEY": Fernet.generate_key().decode(), "AUTO_PUBLISH_ENABLED": "true", "GOOGLE_CLIENT_ID": "test-client", "GOOGLE_CLIENT_SECRET": "test-secret"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.engine = create_engine(f"sqlite:///{self.root / 'test.db'}")
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine)
        self.db = self.sessions()
        self.addCleanup(self.db.close)
        self.db.add_all([User(id=1, name="One", email="one@test.invalid"), User(id=2, name="Two", email="two@test.invalid")])
        self.db.add(Project(id=1, user_id=1, title="Project", topic="Topic", platform="YouTube", content_type="Video", folder="test", path=str(self.root)))
        self.db.add(Content(id=1, user_id=1, project_id=1, title="Approved video", script="Script", caption="Approved caption", platform="YouTube", content_type="Video", status="approved"))
        self.account = PublishingAccount(id=1, user_id=1, provider="youtube", remote_id="channel-1", name="My channel", access_token=encrypt("private-token"), refresh_token=encrypt("refresh-token"), status="connected")
        self.db.add(self.account)
        source = self.root / "clip.mp4"
        source.write_bytes(b"fixture video")
        self.db.add(Media(id=1, user_id=1, project_id=1, title="Final export", media_type="final", file_name="clip.mp4", file_path=str(source), extension=".mp4", mime_type="video/mp4", status="ready"))
        self.db.commit()
        self.storage = patch("app.services.publishing_media.STORAGE", self.root)
        self.storage.start()
        self.addCleanup(self.storage.stop)

    def request(self, **values):
        payload = dict(project_id=1, content_id=1, platform="YouTube", scheduled_at=now() + timedelta(hours=1), publishing_account_id=1, media_ids=[1], request_key=uuid4())
        return ScheduleCreate(**{**payload, **values})

    def test_connecting_another_brand_channel_preserves_first_channel(self):
        original_token = self.account.access_token
        for name in ["Second brand", "Second brand renamed"]:
            with patch("app.services.publishing_accounts.api", side_effect=[
                {"access_token": "second-access", "refresh_token": "second-refresh"},
                {"items": [{"id": "channel-2", "snippet": {"title": name}}]},
            ]):
                PublishingAccounts.complete(self.db, 1, "youtube", "test-code")
        accounts = self.db.query(PublishingAccount).filter_by(user_id=1, provider="youtube").all()
        self.assertEqual(len(accounts), 2)
        self.assertEqual(self.account.access_token, original_token)
        second = next(account for account in accounts if account.remote_id == "channel-2")
        self.assertEqual(second.name, "Second brand renamed")
        self.assertEqual(decrypt(second.refresh_token), "second-refresh")

    def job(self):
        result = create_schedule(self.request(), self.db, 1)
        job = self.db.query(PublishJob).one()
        job.next_attempt_at = now() - timedelta(seconds=1)
        self.db.commit()
        return job, result["schedule"]

    def test_tokens_are_encrypted_and_never_serialized(self):
        self.assertNotIn("private-token", self.account.access_token)
        self.assertEqual(decrypt(self.account.access_token), "private-token")
        response = list_connections(self.db, 1)
        self.assertNotIn("access_token", str(response))
        self.assertNotIn("refresh-token", str(response))
        self.assertEqual(list_connections(self.db, 2)["accounts"], [])

    def test_oauth_state_is_bound_to_browser_user_provider_and_single_use(self):
        url, browser = PublishingAccounts.start(self.db, 1, "youtube")
        params = parse_qs(urlparse(url).query)
        state = params["state"][0]
        self.assertIn("youtube.upload", params["scope"][0])
        for provider, cookie in [("facebook", browser), ("youtube", "wrong-browser")]:
            with self.assertRaises(HTTPException):
                PublishingAccounts.consume_state(self.db, provider, state, cookie)
        self.assertEqual(PublishingAccounts.consume_state(self.db, "youtube", state, browser), 1)
        with self.assertRaises(HTTPException):
            PublishingAccounts.consume_state(self.db, "youtube", state, browser)

    def test_expired_state_is_rejected(self):
        url, browser = PublishingAccounts.start(self.db, 1, "youtube")
        self.db.query(PublishingOAuthState).one().expires_at = now() - timedelta(seconds=1)
        self.db.commit()
        with self.assertRaises(HTTPException):
            PublishingAccounts.consume_state(self.db, "youtube", parse_qs(urlparse(url).query)["state"][0], browser)

    def test_schedule_snapshots_approved_copy_and_idempotent_request(self):
        request = self.request()
        first = create_schedule(request, self.db, 1)
        second = create_schedule(request, self.db, 1)
        self.assertEqual(first["schedule"]["id"], second["schedule"]["id"])
        self.assertEqual(self.db.query(PublishJob).count(), 1)
        self.db.get(Content, 1).caption = "Later edit"
        self.db.commit()
        self.assertEqual(self.db.query(PublishJob).one().payload["caption"], "Approved caption")
        self.assertNotIn("private-token", str(list_schedules(self.db, 1)))

    def test_ownership_platform_and_approval_enforced(self):
        with self.assertRaises(HTTPException):
            create_schedule(self.request(), self.db, 2)
        with self.assertRaises(HTTPException):
            create_schedule(self.request(platform="Instagram"), self.db, 1)
        self.db.get(Content, 1).status = "draft"
        self.db.commit()
        with self.assertRaises(HTTPException):
            create_schedule(self.request(), self.db, 1)

    def test_foreign_media_and_past_time_rejected(self):
        for values in [{"media_ids": [999]}, {"scheduled_at": now() - timedelta(minutes=1)}]:
            with self.assertRaises(HTTPException):
                create_schedule(self.request(**values), self.db, 1)

    def test_worker_publishes_once_and_records_result(self):
        job, schedule = self.job()
        publisher = Mock(return_value=("post-1", "https://www.youtube.com/watch?v=post-1", "published"))
        process_job(self.db, job.id, publisher)
        process_job(self.db, job.id, publisher)
        self.assertEqual(publisher.call_count, 1)
        self.assertEqual(self.db.get(Schedule, schedule["id"]).status, "published")
        self.assertEqual(self.db.get(PublishJob, job.id).remote_post_id, "post-1")
        self.assertEqual(len(schedule_events(schedule["id"], self.db, 1)["events"]), 3)
        with self.assertRaises(HTTPException):
            schedule_events(schedule["id"], self.db, 2)

    def test_two_sessions_cannot_publish_same_job(self):
        job, _ = self.job()
        publisher = Mock(return_value=("post", None, "published"))
        with self.sessions() as other:
            process_job(self.db, job.id, publisher)
            process_job(other, job.id, publisher)
        self.assertEqual(publisher.call_count, 1)

    def test_cancelled_job_does_not_publish(self):
        job, schedule = self.job()
        update_schedule(schedule["id"], ScheduleUpdate(status="cancelled"), self.db, 1)
        publisher = Mock()
        process_job(self.db, job.id, publisher)
        publisher.assert_not_called()

    def test_processing_cannot_be_cancelled_or_falsely_marked_published(self):
        job, schedule = self.job()
        job.status = "processing"
        self.db.commit()
        for status in ["cancelled", "published"]:
            with self.assertRaises(HTTPException):
                update_schedule(schedule["id"], ScheduleUpdate(status=status), self.db, 1)
        with self.assertRaises(HTTPException):
            delete_schedule(schedule["id"], self.db, 1)

    def test_ambiguous_failure_requires_review_without_automatic_retry(self):
        job, schedule = self.job()
        publisher = Mock(side_effect=ProviderError("Interrupted", uncertain=True))
        process_job(self.db, job.id, publisher)
        process_job(self.db, job.id, publisher)
        self.assertEqual(publisher.call_count, 1)
        self.assertEqual(self.db.get(Schedule, schedule["id"]).status, "needs_review")

    def test_processing_is_polled_and_private_upload_is_not_marked_public(self):
        job, schedule = self.job()
        process_job(self.db, job.id, Mock(side_effect=Pending()))
        job = self.db.get(PublishJob, job.id)
        self.assertEqual(job.status, "processing")
        job.next_attempt_at = now() - timedelta(seconds=1)
        self.db.commit()
        process_job(self.db, job.id, Mock(return_value=("post", "https://youtube.com/watch?v=post", "uploaded")))
        row = self.db.get(Schedule, schedule["id"])
        self.assertEqual(row.status, "uploaded")
        self.assertIsNone(row.published_at)

    def test_disconnect_cancels_queued_posts_and_erases_tokens(self):
        job, schedule = self.job()
        disconnect(1, self.db, 1)
        self.assertIsNone(self.db.get(PublishingAccount, 1).access_token)
        self.assertEqual(self.db.get(Schedule, schedule["id"]).status, "cancelled")
        self.assertEqual(self.db.get(PublishJob, job.id).status, "cancelled")

    def test_revoked_approval_blocks_worker(self):
        job, _ = self.job()
        self.db.get(Content, 1).status = "draft"
        self.db.commit()
        publisher = Mock()
        process_job(self.db, job.id, publisher)
        publisher.assert_not_called()
        self.assertEqual(self.db.get(PublishJob, job.id).status, "failed")

    def test_provider_error_does_not_expose_secret_response(self):
        response = Mock(status_code=401)
        response.json.return_value = {"error": {"code": 190, "message": "secret private-token"}}
        with patch("app.services.publishing_accounts.requests.request", return_value=response):
            with self.assertRaises(ProviderError) as error:
                api("GET", "https://example.invalid")
        self.assertNotIn("private-token", str(error.exception))
        self.assertTrue(error.exception.reconnect)

    def test_instagram_waits_for_container_and_publishes_once(self):
        job, _ = self.job()
        self.account.provider = "instagram"
        job.payload = {**job.payload, "kind": "images", "assets": [{"url": "https://media.example/image.jpg"}]}
        self.db.commit()
        with patch("app.services.publishing_providers.api", return_value={"id": "container-1"}) as remote:
            with self.assertRaises(Pending):
                instagram(self.db, job, self.account, "token")
            self.assertTrue(remote.call_args.args[1].endswith("/channel-1/media"))
        with patch("app.services.publishing_providers.api", return_value={"status_code": "IN_PROGRESS"}) as remote:
            with self.assertRaises(Pending):
                instagram(self.db, job, self.account, "token")
            self.assertEqual(remote.call_count, 1)
            self.assertEqual(remote.call_args.args[0], "GET")
        with patch("app.services.publishing_providers.api", side_effect=[{"status_code": "FINISHED"}, {"id": "post-1"}, {"permalink": "https://instagram.com/p/post-1"}]):
            result = instagram(self.db, job, self.account, "token")
        self.assertEqual(result[0], "post-1")
        with patch("app.services.publishing_providers.api", return_value={"permalink": "https://instagram.com/p/post-1"}) as remote:
            instagram(self.db, job, self.account, "token")
            self.assertEqual(remote.call_count, 1)
            self.assertEqual(remote.call_args.args[0], "GET")

    def test_facebook_finishes_upload_before_waiting_for_processing(self):
        job, _ = self.job()
        self.account.provider = "facebook"
        job.provider_state = {"video_id": "video-1", "uploaded": True}
        self.db.commit()
        with patch("app.services.publishing_providers.api", side_effect=[
            {"status": {"uploading_phase": {"status": "complete"}, "processing_phase": {"status": "not_started"}, "publishing_phase": {"status": "not_started"}}},
            {"success": True},
        ]) as remote:
            with self.assertRaises(Pending):
                facebook(self.db, job, self.account, "token")
            self.assertEqual(remote.call_args.kwargs["data"]["upload_phase"], "finish")
        with patch("app.services.publishing_providers.api", return_value={"status": {"publishing_phase": {"status": "complete"}}}) as remote:
            result = facebook(self.db, job, self.account, "token")
            self.assertEqual(result[2], "published")
            self.assertEqual(remote.call_count, 1)

    def test_youtube_poll_never_reuploads_an_existing_video(self):
        job, _ = self.job()
        job.provider_state = {"upload_url": "https://www.googleapis.com/upload/session", "post_id": "video-1"}
        self.db.commit()
        with patch("app.services.publishing_providers.api", return_value={"items": [{"status": {"uploadStatus": "processed", "privacyStatus": "public"}}]}) as remote:
            result = youtube(self.db, job, self.account, "token")
        self.assertEqual(result, ("video-1", "https://www.youtube.com/watch?v=video-1", "published"))
        self.assertEqual(remote.call_count, 1)
        self.assertEqual(remote.call_args.args[0], "GET")

    def test_youtube_visibility_restriction_is_not_reported_as_published(self):
        job, _ = self.job()
        job.provider_state = {"upload_url": "https://www.googleapis.com/upload/session", "post_id": "video-1"}
        self.db.commit()
        with patch("app.services.publishing_providers.api", return_value={"items": [{"status": {"uploadStatus": "processed", "privacyStatus": "private"}}]}):
            with self.assertRaises(ProviderError) as error:
                youtube(self.db, job, self.account, "token")
        self.assertTrue(error.exception.uncertain)
        self.assertEqual(job.provider_state["actual_privacy"], "private")

    def test_youtube_refresh_saves_new_encrypted_token(self):
        self.account.expires_at = now() - timedelta(minutes=1)
        self.db.commit()
        with patch("app.services.publishing_accounts.api", return_value={"access_token": "renewed", "expires_in": 3600}):
            token = PublishingAccounts.token(self.db, self.account)
        self.assertEqual(token, "renewed")
        self.assertNotEqual(self.account.access_token, token)
        self.assertEqual(decrypt(self.account.refresh_token), "refresh-token")

    def test_instagram_requires_public_media_and_converts_png_to_jpeg(self):
        from PIL import Image
        self.account.provider = "instagram"
        self.db.get(Content, 1).platform = "Instagram"
        path = self.root / "image.png"
        Image.new("RGB", (80, 100), "red").save(path)
        media = self.db.get(Media, 1)
        media.file_path, media.extension, media.media_type = str(path), ".png", "image"
        self.db.commit()
        with patch.dict(os.environ, {"PUBLIC_MEDIA_BASE_URL": "http://localhost:8000"}):
            with self.assertRaises(HTTPException):
                create_schedule(self.request(platform="Instagram"), self.db, 1)
        with patch.dict(os.environ, {"PUBLIC_MEDIA_BASE_URL": "https://media.example"}):
            create_schedule(self.request(platform="Instagram"), self.db, 1)
        asset = self.db.query(PublishJob).one().payload["assets"][0]
        self.assertTrue(asset["url"].startswith("https://media.example/storage/publishing/"))
        with Image.open(asset["path"]) as image:
            self.assertEqual(image.format, "JPEG")


if __name__ == "__main__":
    unittest.main()

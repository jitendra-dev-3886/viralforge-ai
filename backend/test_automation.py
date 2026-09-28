import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.models.automation import AutomationRule, AutomationRun
from app.schemas.automation import AutomationConfig, AutomationState
from app.services import automation_service as service
from app.api.automation import create_automation, update_automation, set_automation_state, list_automations


class AutomationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine = create_engine(f"sqlite:///{Path(self.temp.name) / 'test.db'}")
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine)
        self.db = self.sessions()
        self.addCleanup(self.db.close)
        self.db.add_all([models.User(id=1, name="One", email="one@example.test"), models.User(id=2, name="Two", email="two@example.test")])
        self.db.add(models.Project(id=1, user_id=1, title="Finance", topic="Budgeting", niche="Finance", platform="Instagram", content_type="Carousel", folder="test", path=self.temp.name))
        self.db.add(models.PublishingAccount(id=1, user_id=1, provider="instagram", remote_id="account", name="Account", access_token="unused", status="connected"))
        self.db.commit()
        self.at = datetime(2026, 9, 28, 3, 0, tzinfo=timezone.utc)  # Monday, 08:30 Kolkata
        env = patch.dict(os.environ, {"AUTO_PUBLISH_ENABLED": "true"})
        env.start()
        self.addCleanup(env.stop)

    def config(self, **values):
        return AutomationConfig(**{**dict(project_id=1, topic="Budgeting tips", niche="Finance"), **values})

    def rule(self, **values):
        config = self.config(**values)
        row = AutomationRule(user_id=1, project_id=1, config=config.model_dump(), enabled=True, next_run_at=self.at + timedelta(minutes=30))
        self.db.add(row)
        self.db.commit()
        return row

    def generated(self, db, rule, run, config):
        content = models.Content(user_id=1, project_id=1, title="A fresh angle", caption="A fresh caption", script="A fresh script", platform="Instagram", content_type="Carousel", status="generated")
        db.add(content)
        db.flush()
        run.content_id = content.id
        db.commit()
        return content, [17, 18, 19]

    def test_timezone_weekdays_and_dst(self):
        self.assertEqual(service.next_occurrence(self.config(), self.at), self.at + timedelta(minutes=30))
        self.assertEqual(service.next_occurrence(self.config(days=[2]), self.at), self.at + timedelta(days=2, minutes=30))
        spring = self.config(timezone="America/New_York", time="02:30", days=[6])
        self.assertEqual(service.next_occurrence(spring, datetime(2026, 3, 8, tzinfo=timezone.utc)), datetime(2026, 3, 15, 6, 30, tzinfo=timezone.utc))
        fall = self.config(timezone="America/New_York", time="01:30")
        first = service.next_occurrence(fall, datetime(2026, 11, 1, tzinfo=timezone.utc))
        self.assertEqual(first, datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc))
        self.assertEqual(service.next_occurrence(fall, first), datetime(2026, 11, 2, 6, 30, tzinfo=timezone.utc))

    def test_config_rejects_invalid_and_unsupported_settings(self):
        for values in ({"days": []}, {"days": [0, 0]}, {"days": [7]}, {"time": "25:00"}, {"timezone": "invalid/zone"},
                       {"mode": "automatic"}, {"mode": "automatic", "publishing_account_id": 1, "content_type": "Story"},
                       {"platform": "youtube"}, {"platform": "youtube", "content_type": "Shorts", "mode": "automatic", "publishing_account_id": 1}):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                self.config(**values)

    def test_ownership_and_account_platform_are_checked(self):
        with self.assertRaises(HTTPException):
            create_automation(self.config(), self.db, 2)
        with self.assertRaises(HTTPException):
            create_automation(self.config(platform="facebook", mode="automatic", publishing_account_id=1), self.db, 1)
        rule = self.rule()
        with self.assertRaises(HTTPException):
            set_automation_state(rule.id, AutomationState(enabled=False), self.db, 2)
        self.assertEqual(list_automations(self.db, 2)["rules"], [])

    def test_claim_is_once_per_occurrence_and_serializes_user_rules(self):
        rule = self.rule()
        second = self.rule(time="09:05")
        self.assertIsNone(service.claim_run(self.db, rule.id, self.at - timedelta(seconds=1)))
        run_id = service.claim_run(self.db, rule.id, self.at)
        self.assertIsNotNone(run_id)
        with self.sessions() as other:
            self.assertIsNone(service.claim_run(other, rule.id, self.at))
            self.assertIsNone(service.claim_run(other, second.id, self.at))
        self.assertEqual(self.db.query(AutomationRun).count(), 1)
        run = self.db.get(AutomationRun, run_id)
        run.status, run.active_user = "draft", None
        self.db.commit()
        self.assertIsNotNone(service.claim_run(self.db, second.id, self.at))

    def test_missed_occurrence_skips_backlog_and_resume_is_future(self):
        rule = self.rule()
        late = self.at + timedelta(days=4)
        self.assertIsNone(service.claim_run(self.db, rule.id, late))
        self.assertEqual(self.db.query(AutomationRun).one().status, "skipped")
        self.assertGreater(service.utc(rule.next_run_at), late)
        set_automation_state(rule.id, AutomationState(enabled=False), self.db, 1)
        with patch("app.api.automation.now", return_value=late):
            result = set_automation_state(rule.id, AutomationState(enabled=True), self.db, 1)
        self.assertGreater(result["rule"]["next_run_at"], late + timedelta(minutes=30))

    def test_edit_reselecting_completed_occurrence_does_not_stall_schedule(self):
        rule = self.rule()
        scheduled = rule.next_run_at
        run_id = service.claim_run(self.db, rule.id, self.at)
        run = self.db.get(AutomationRun, run_id)
        run.status, run.active_user = "draft", None
        rule.next_run_at = scheduled
        self.db.commit()
        self.assertIsNone(service.claim_run(self.db, rule.id, self.at))
        self.assertGreater(service.utc(rule.next_run_at), service.utc(scheduled))
        self.assertEqual(self.db.query(AutomationRun).count(), 1)

    def test_drafts_never_schedule_or_approve_content(self):
        run_id = service.claim_run(self.db, self.rule().id, self.at)
        with patch.object(service, "generate_and_render", side_effect=self.generated), patch("app.api.schedule.create_schedule") as queue:
            service.process_run(self.db, run_id)
        run = self.db.get(AutomationRun, run_id)
        self.assertEqual(run.status, "draft")
        self.assertIsNone(run.active_user)
        self.assertEqual(self.db.get(models.Content, run.content_id).status, "generated")
        queue.assert_not_called()

    def test_automatic_mode_uses_existing_schedule_path(self):
        rule = self.rule(mode="automatic", publishing_account_id=1)
        run_id = service.claim_run(self.db, rule.id, self.at)
        with patch.object(service, "generate_and_render", side_effect=self.generated), patch.object(service, "now", return_value=self.at), patch("app.api.schedule.create_schedule", return_value={"schedule": {"id": 23}}) as queue:
            service.process_run(self.db, run_id)
        run = self.db.get(AutomationRun, run_id)
        self.assertEqual((run.status, run.schedule_id, run.active_user), ("scheduled", 23, None))
        request = queue.call_args.args[0]
        self.assertEqual(request.media_ids, [17, 18, 19])
        self.assertEqual(request.scheduled_at, self.at + timedelta(minutes=30))
        self.assertEqual(self.db.get(models.Content, run.content_id).status, "approved")

    def test_pause_during_generation_leaves_a_draft_and_edit_is_blocked(self):
        rule = self.rule(mode="automatic", publishing_account_id=1)
        run_id = service.claim_run(self.db, rule.id, self.at)
        with self.assertRaises(HTTPException):
            update_automation(rule.id, self.config(), self.db, 1)
        def generate(*args):
            result = self.generated(*args)
            set_automation_state(rule.id, AutomationState(enabled=False), self.db, 1)
            return result
        with patch.object(service, "generate_and_render", side_effect=generate), patch("app.api.schedule.create_schedule") as queue:
            service.process_run(self.db, run_id)
        self.assertEqual(self.db.get(AutomationRun, run_id).status, "draft")
        queue.assert_not_called()

    def test_automatic_run_creates_one_real_publish_job(self):
        rule = self.rule(content_type="Reel", mode="automatic", publishing_account_id=1)
        run_id = service.claim_run(self.db, rule.id, self.at)
        def generate(db, rule, run, config):
            content, _ = self.generated(db, rule, run, config)
            content.content_type = "Reel"
            path = Path(self.temp.name) / "finished.mp4"
            path.write_bytes(b"test video")
            media = models.Media(user_id=1, project_id=1, media_type="final", file_name=f"content_{content.id}_final.mp4", file_path=str(path), extension=".mp4", mime_type="video/mp4", status="ready")
            db.add(media)
            db.commit()
            return content, [media.id]
        with patch.object(service, "generate_and_render", side_effect=generate), patch.object(service, "now", return_value=self.at), patch("app.api.schedule.now", return_value=self.at), patch("app.services.publishing_media.STORAGE", Path(self.temp.name)), patch.dict(os.environ, {"PUBLIC_MEDIA_BASE_URL": "https://media.example"}):
            service.process_run(self.db, run_id)
            service.process_run(self.db, run_id)
        run = self.db.get(AutomationRun, run_id)
        self.assertEqual(run.status, "scheduled")
        job = self.db.query(models.PublishJob).one()
        self.assertEqual(job.schedule_id, run.schedule_id)
        self.assertEqual(job.status, "queued")
        self.assertIn("A fresh caption", job.payload["caption"])
        self.assertEqual(self.db.query(models.Content).count(), 1)

    def test_late_generation_and_queue_failure_do_not_leave_auto_approval(self):
        for late in (False, True):
            with self.subTest(late=late):
                rule = self.rule(mode="automatic", publishing_account_id=1)
                run_id = service.claim_run(self.db, rule.id, self.at)
                with patch.object(service, "generate_and_render", side_effect=self.generated), patch.object(service, "now", return_value=self.at + timedelta(hours=1) if late else self.at), patch("app.api.schedule.create_schedule", side_effect=HTTPException(400, "Export invalid")) as queue:
                    service.process_run(self.db, run_id)
                run = self.db.get(AutomationRun, run_id)
                self.assertEqual(run.status, "needs_review")
                self.assertIsNone(run.active_user)
                self.assertEqual(self.db.get(models.Content, run.content_id).status, "generated")
                if late:
                    queue.assert_not_called()

    def test_repetition_blocks_near_copy_and_reused_visuals(self):
        content = SimpleNamespace(title="Different title", caption="Here are five practical ways to save money on your weekly grocery shopping.", script="New script", scenes=[])
        with self.assertRaises(ValueError):
            service.check_repetition(content, [{"caption": "Here are five practical ways to save money on your weekly grocery shopping!"}])
        content.scenes = [SimpleNamespace(media=SimpleNamespace(file_url="https://stock.test/same.jpg"))]
        with self.assertRaises(ValueError):
            service.check_repetition(content, [{"scenes": [{"media_url": "https://stock.test/same.jpg"}]}])
        service.check_repetition(content, [{"caption": "A completely different discussion about investment."}])

    def test_interrupted_runs_are_not_retried(self):
        rule = self.rule()
        run_id = service.claim_run(self.db, rule.id, self.at)
        with patch.object(service, "SessionLocal", self.sessions), patch.object(service, "now", return_value=self.at + timedelta(hours=3)), patch.object(service, "generate_and_render") as generate:
            service.tick()
        self.db.expire_all()
        run = self.db.get(AutomationRun, run_id)
        self.assertEqual((run.status, run.active_user), ("needs_review", None))
        generate.assert_not_called()

    def test_generation_reuses_history_and_billed_export(self):
        from app.services.ai_service import AIService
        from app.services.project_render_service import ProjectRenderService
        for kind in ("Carousel", "Reel"):
            with self.subTest(kind=kind):
                rule = self.rule(content_type=kind)
                run_id = service.claim_run(self.db, rule.id, self.at)
                run = self.db.get(AutomationRun, run_id)
                content, _ = self.generated(self.db, rule, run, self.config())
                content.caption, content.title, content.script = f"{kind} caption", f"{kind} title", f"{kind} script"
                media = models.Media(user_id=1, project_id=1, media_type="image", file_name=f"{kind}.png", file_path="unused", file_url=f"https://stock.test/{kind}.png")
                self.db.add(media)
                self.db.flush()
                self.db.add(models.Scene(user_id=1, project_id=1, content_id=content.id, scene_number=1, text="Scene", media_id=media.id))
                self.db.commit()
                self.db.refresh(content)
                # Hide the simulated new output until AIService returns it.
                trend = {"title": f"Fresh {kind} trend", "source_title": "Live source", "source": "live", "language": "en"}
                with patch.object(service, "prepare_audio") as audio, patch.object(service, "select_trend", return_value=trend), patch.object(AIService, "generate", return_value={"content_id": content.id}) as generate, patch("app.services.content_service.ContentService._serialize", return_value={"title": "Older idea", "scenes": []}), patch("app.core.render_errors.run_render", return_value={"media_id": 9, "media_ids": [9]}) as render:
                    result, ids = service.generate_and_render(self.db, rule, run, self.config(content_type=kind))
                self.assertEqual(ids, [9])
                self.assertTrue(generate.call_args.kwargs["previous_outputs"])
                self.assertEqual(generate.call_args.args[0].topic, trend["title"])
                self.assertEqual(result.generation_config["trend"], trend)
                self.assertEqual(list_automations(self.db, 1)["runs"][0]["topic"], trend["title"])
                self.assertEqual(render.call_args.kwargs["request_key"], f"automation-export-{run.id}")
                if kind == "Reel":
                    self.assertIs(render.call_args.args[0], ProjectRenderService.generate)
                    audio.assert_called_once_with(self.db, content, self.config(content_type=kind))
                else:
                    self.assertTrue(render.call_args.kwargs["as_image"])
                    audio.assert_not_called()
                run.status, run.active_user = "draft", None
                self.db.commit()

    def test_trend_selection_uses_project_context_and_ranked_language_order(self):
        topics = [
            {"title": "शीर्ष हिंदी विषय", "language": "hi", "source": "live", "source_title": "Hindi source"},
            {"title": "Top English trend", "language": "en", "source": "live", "source_title": "First source"},
            {"title": "Second English trend", "language": "en", "source": "live", "source_title": "Second source"},
        ]
        with patch("app.api.trends.credentials_for", return_value={}), patch("app.api.trends.TrendService.get_trending", return_value={"trends": topics}) as trends:
            self.assertEqual(service.select_trend(self.db, 1, self.config())["title"], "Top English trend")
            kwargs = trends.call_args.kwargs
            self.assertEqual((kwargs["niche"], kwargs["platform"], kwargs["content_type"], kwargs["user_id"]), ("Finance", "instagram", "Carousel", 1))
            self.assertIn("Project: Finance; Topic: Budgeting", kwargs["brand"])
            self.assertEqual(service.select_trend(self.db, 1, self.config(language="Hindi"))["title"], "शीर्ष हिंदी विषय")

    def test_trend_history_blocks_rephrased_sources_beyond_recent_thirty(self):
        for number in range(35):
            self.db.add(models.Content(user_id=1, project_id=1, title=f"Older content {number}", script="Script",
                platform="Instagram", content_type="Post", generation_config={"topic": f"Old topic {number}",
                "trend": {"source_title": "Already used source" if number == 0 else f"Source {number}"}}))
        self.db.commit()
        topics = [
            {"title": "Old TOPIC 1!", "language": "en", "source": "live"},
            {"title": "Rephrased old angle", "language": "en", "source": "live", "source_title": "Already used source"},
            {"title": "New topic", "language": "en", "source": "live", "source_title": "New source"},
        ]
        with patch("app.api.trends.trending", return_value={"trends": topics}):
            self.assertEqual(service.select_trend(self.db, 1, self.config())["title"], "New topic")

    def test_no_unused_live_trend_skips_without_generation_or_posting(self):
        from app.services.ai_service import AIService
        run_id = service.claim_run(self.db, self.rule().id, self.at)
        with patch("app.api.trends.trending", return_value={"trends": [{"title": "Invented fallback", "language": "en", "source": "fallback"}]}), patch.object(AIService, "generate") as generate, patch("app.api.schedule.create_schedule") as queue:
            service.process_run(self.db, run_id)
        run = self.db.get(AutomationRun, run_id)
        self.assertEqual(run.status, "skipped")
        self.assertIsNone(run.active_user)
        generate.assert_not_called()
        queue.assert_not_called()

    def test_topic_is_optional_and_history_is_scoped_to_owner(self):
        config = AutomationConfig(project_id=1, niche="Finance")
        self.db.add(models.Content(user_id=2, project_id=1, title="Top English trend", script="Script", platform="Instagram", content_type="Post"))
        self.db.commit()
        with patch("app.api.trends.trending", return_value={"trends": [{"title": "Top English trend", "language": "en", "source": "live"}]}):
            self.assertEqual(service.select_trend(self.db, 1, config)["title"], "Top English trend")

    def audio_content(self):
        content = models.Content(user_id=1, project_id=1, title="Audio test", script="Narration", language="Hindi", platform="Instagram", content_type="Reel", generation_config={"topic": "Saved topic"})
        self.db.add(content)
        self.db.flush()
        for number in (2, 1):
            self.db.add(models.Scene(user_id=1, project_id=1, content_id=content.id, scene_number=number,
                                     text=f"Scene {number} text", voice_text=f"Scene {number} narration"))
        self.db.commit()
        return content

    def test_audio_generates_all_scene_narration_and_saves_music_settings(self):
        content = self.audio_content()
        path = Path(self.temp.name) / "music.mp3"
        path.write_bytes(b"audio fixture")
        music = models.Media(user_id=1, project_id=1, media_type="music", status="ready", file_name=path.name, file_path=str(path))
        self.db.add(music)
        self.db.commit()
        config = self.config(content_type="Reel", music_id=music.id, music_volume=0.12, voice_speed="-5%")
        with patch("app.services.voice_service.VoiceService.generate", new_callable=AsyncMock, return_value={"success": True}) as generate:
            service.prepare_audio(self.db, content, config)
        self.assertEqual(generate.await_count, 2)
        requests = [call.kwargs["request"] for call in generate.await_args_list]
        self.assertEqual([request.text for request in requests], ["Scene 1 text", "Scene 2 text"])
        self.assertEqual((requests[0].language, requests[0].speed, requests[0].voice), ("Hindi", "-5%", ""))
        self.assertEqual(content.generation_config["audio"], {"voice_enabled": True, "music_id": music.id, "music_volume": 0.12})
        self.assertEqual(content.generation_config["topic"], "Saved topic")

    def test_audio_off_and_failed_voice_are_not_silently_ignored(self):
        content = self.audio_content()
        with patch("app.services.voice_service.VoiceService.generate", new_callable=AsyncMock, return_value={"success": False}) as generate:
            service.prepare_audio(self.db, content, self.config(voice="off"))
            generate.assert_not_awaited()
            self.assertFalse(content.generation_config["audio"]["voice_enabled"])
            with self.assertRaisesRegex(ValueError, "Narration failed for scene 1"):
                service.prepare_audio(self.db, content, self.config())
            self.assertEqual(generate.await_count, 1)

    def test_music_selection_rejects_foreign_missing_or_nonmusic_files(self):
        path = Path(self.temp.name) / "music.mp3"
        path.write_bytes(b"audio fixture")
        music = models.Media(user_id=2, project_id=1, media_type="music", status="ready", file_name=path.name, file_path=str(path))
        self.db.add(music)
        self.db.commit()
        config = self.config(content_type="Reel", music_id=music.id)
        with self.assertRaises(HTTPException):
            service.validate_resources(self.db, 1, config)
        music.user_id, music.media_type = 1, "audio"
        self.db.commit()
        with self.assertRaises(HTTPException):
            service.validate_resources(self.db, 1, config)
        music.media_type, music.file_path = "music", str(Path(self.temp.name) / "missing.mp3")
        self.db.commit()
        with self.assertRaises(HTTPException):
            service.validate_resources(self.db, 1, config)


if __name__ == "__main__":
    unittest.main()

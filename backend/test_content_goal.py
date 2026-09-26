import json
import re
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.api.ai import router
from app.core.security import get_current_user_id
from app.database import Base, get_db
from app.models.brand import Brand
from app.models.content import Content
from app.models.project import Project
from app.models.user import User
from app.schemas.ai import GenerateRequest
from app.schemas.content import ContentUpdate
from app.services.ai_service import AIService
from app.services.content_service import ContentService
from app.services.prompt_engine import PromptEngine
from app.config.prompt_config import VISUAL_NICHE_BOUNDARIES
from app.services.publishing_media import posting_metadata


GOALS = ("Reach", "Shares", "Saves", "Comments", "Followers")


class ContentGoalTests(unittest.TestCase):
    def test_full_generation_matrix_for_six_niches_and_all_formats(self):
        formats = {"Instagram": ["Reel", "Carousel", "Story", "Post", "Quote"],
                   "Facebook": ["Reel", "Carousel", "Story", "Post", "Quote"],
                   "YouTube": ["Shorts", "Long Video", "Community Post"]}
        outputs = [f"{platform}: {kind}" for platform, kinds in formats.items() for kind in kinds]
        expected_counts = {"Reel": 7, "Carousel": 6, "Story": 7, "Post": 1, "Quote": 1,
                           "Shorts": 7, "Long Video": 10, "Community Post": 1}
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        Base.metadata.create_all(engine)
        counter = 0
        def response(provider, prompt, **kwargs):
            nonlocal counter
            counter += 1
            count = int(re.search(r"Create exactly (\d+) scenes", prompt).group(1))
            return json.dumps({"title": f"Topic angle {counter}", "caption": f"Format-specific takeaway {counter}",
                "description": "A complete explanation of the selected topic", "hashtags": ["#Topic", f"#Angle{counter}"],
                "scenes": [{"text": f"Step {index} for angle {counter}", "voice_text": f"Explain step {index} for angle {counter}",
                            "keyword": f"subject {counter}", "visual_plan": f"Composition {counter} beat {index}"}
                           for index in range(count)]}), "test"
        with Session(engine) as db:
            db.add(User(id=1, name="Test", email="matrix@test.invalid"))
            db.commit()
            with patch("app.services.ai_service.credentials_for", return_value={"test": {}}), \
                 patch("app.services.billing_service.require_plan"), \
                 patch.object(AIService, "_generate_from_provider", side_effect=response), \
                 patch("app.services.ai_service.DownloaderService.download", side_effect=lambda **kw: {"file_url": f"https://stock.test/{kw['scene_id']}.jpg"}):
                for index, (niche, boundary) in enumerate(VISUAL_NICHE_BOUNDARIES.items(), 1):
                    db.add(Brand(id=index, user_id=1, name=niche, niche=niche))
                    db.add(Project(id=index, user_id=1, brand_id=index, title=niche, topic=boundary.split(",")[0],
                                   platform="Instagram", content_type="Post", folder="test", path="test"))
                    db.commit()
                    result = AIService.generate(self.request(project_id=index, niche=niche, scene_count=None,
                                                package="quote", outputs=outputs), db, 1)
                    titles, captions, urls = set(), set(), set()
                    for platform, kinds in formats.items():
                        for kind in kinds:
                            with self.subTest(niche=niche, platform=platform, format=kind):
                                output = result["data"][platform.lower()][AIService._response_key(kind)]
                                saved = db.get(Content, output["content_id"])
                                self.assertIn(boundary, saved.prompt)
                                self.assertEqual(len(saved.scenes), expected_counts[kind])
                                self.assertEqual(saved.content_type, kind)
                                expected_media = "video" if kind in ("Reel", "Story", "Shorts", "Long Video") else "image"
                                self.assertTrue(all(scene.media_type == expected_media for scene in saved.scenes))
                                self.assertNotIn(saved.title, titles)
                                self.assertNotIn(saved.caption, captions)
                                self.assertEqual(set(saved.generation_config["excluded_media_urls"]), urls)
                                titles.add(saved.title)
                                captions.add(saved.caption)
                                urls.update(scene["media_url"] for scene in output["scenes"])
                    self.assertEqual(len(titles), 13)
            self.assertEqual(counter, 78)

    def request(self, **values):
        return GenerateRequest(**{
            "project_id": 1, "platforms": ["Instagram"], "content_types": ["Post"],
            "niche": "Personal finance", "topic": "Lifestyle inflation", "package": "complete",
            "scene_count": 1, **values,
        })

    def brand(self):
        return SimpleNamespace(name="FinLogicMoney", niche="Finance",
                               description="Practical money advice for young salaried professionals.")

    def response(self):
        return json.dumps({"title": "Lifestyle inflation", "hook": "Your raise vanished.",
                           "caption": "A raise can disappear into new expenses.",
                           "description": "Learn how lifestyle inflation can absorb a salary raise. Compare your spending before increasing your lifestyle budget.",
                           "cta": "Send this to a friend planning their next raise.",
                           "scenes": [{"text": "Your salary increased. Your lifestyle increased faster.",
                                       "visual_plan": "Overhead comparison of a pay slip and household expenses",
                                       "duration": 5, "media_type": "image"}]})

    def test_visual_boundaries_are_selected_without_cross_niche_templates(self):
        for name, scope in VISUAL_NICHE_BOUNDARIES.items():
            with self.subTest(brand=name):
                brand = SimpleNamespace(name=name.upper(), niche="General", description="")
                prompt = PromptEngine.build(self.request(), brand=brand)
                self.assertIn(scope, prompt)
                for other_name, other_scope in VISUAL_NICHE_BOUNDARIES.items():
                    if other_name != name:
                        self.assertNotIn(other_scope, prompt)
                self.assertIn("Topic: Lifestyle inflation", prompt)
                self.assertIn("boundaries only", prompt)
        self.assertIn(VISUAL_NICHE_BOUNDARIES["YS Tech"], PromptEngine.build(self.request(niche="ys_tech")))

    def test_recent_visuals_survive_generation_retry(self):
        request = self.request()
        recent = [{"topic": "Previous topic", "story": "Previous Reel arc", "visuals": ["A repeated desk setup"]}]
        prompt = PromptEngine.build(request, recent_visuals=recent)
        with patch.object(AIService, "_generate_from_provider", side_effect=[("invalid", "test"), (self.response(), "test")]) as provider:
            AIService._generate_validated_response("test", request, prompt)
        for call in provider.call_args_list:
            self.assertIn(json.dumps(recent), call.args[1])
            self.assertIn("camera angle", call.args[1])

    def test_goal_validation_and_optional_default(self):
        for goal in GOALS:
            self.assertEqual(self.request(content_goal=goal).content_goal, goal)
        self.assertIsNone(self.request().content_goal)
        self.assertIsNone(self.request(content_goal=None).content_goal)
        for goal in ("Likes", "", "shares", 1, ["Reach"]):
            with self.subTest(goal=goal), self.assertRaises(ValidationError):
                self.request(content_goal=goal)

    def test_api_rejects_unsupported_goal_before_generation(self):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_current_user_id] = lambda: 1
        app.dependency_overrides[get_db] = lambda: None
        with TestClient(app) as client, patch.object(AIService, "generate") as generate:
            response = client.post("/api/ai/generate", json={**self.request().model_dump(), "content_goal": "Likes"})
        self.assertEqual(response.status_code, 422)
        generate.assert_not_called()

    def test_default_prompt_is_unchanged_by_brand_or_null_goal(self):
        prompt = PromptEngine.build(self.request())
        self.assertEqual(prompt, PromptEngine.build(self.request(content_goal=None), brand=self.brand()))
        self.assertNotIn("Content goal:", prompt)
        self.assertNotIn("Brand description / audience context:", prompt)

    def test_each_goal_has_distinct_instructions(self):
        for goal, rule in zip(GOALS, ("fast comprehension", "genuine reason to send", "checklists",
                                     "without engagement bait", "recurring niche value")):
            prompt = PromptEngine.build(self.request(content_goal=goal), brand=self.brand())
            self.assertIn(f"Content goal: {goal}", prompt)
            self.assertIn(rule, prompt)
            self.assertIn("FinLogicMoney", prompt)
            self.assertIn("young salaried professionals", prompt)
            self.assertIn("Create exactly 1 scenes", prompt)

    def test_shares_choose_trigger_internally_and_adapt_platform(self):
        prompt = PromptEngine.build(self.request(content_goal="Shares"))
        for trigger in ("Relatable", "Useful", "Emotional", "Surprising", "Identity", "Send-to-someone"):
            self.assertIn(trigger, prompt)
        self.assertIn("hook and core idea themselves", prompt)
        self.assertIn("do not return the trigger", prompt)
        self.assertIn("only when appropriate", prompt)
        self.assertIn("Instagram: Use a strong visual-first hook", prompt)
        self.assertNotIn("Facebook: Allow", prompt)
        facebook = PromptEngine.build(self.request(content_goal="Shares", platforms=["Facebook"]))
        self.assertIn("Facebook: Allow more conversational context", facebook)
        self.assertNotIn("Instagram: Use", facebook)

    def test_retry_keeps_goal_brand_and_audience(self):
        request = self.request(content_goal="Shares")
        with patch.object(AIService, "_generate_from_provider", side_effect=[("invalid", "test"), (self.response(), "test")]) as provider:
            AIService._generate_validated_response("test", request, PromptEngine.build(request, self.brand()), brand=self.brand())
        self.assertEqual(provider.call_count, 2)
        for call in provider.call_args_list:
            for text in ("Content goal: Shares", "FinLogicMoney", "young salaried professionals"):
                self.assertIn(text, call.args[1])

    def test_youtube_metadata_rules_survive_retry_and_invalid_fields_retry(self):
        request = self.request(platforms=["YouTube"], content_types=["Community Post"])
        for prompt in (PromptEngine.build(request), PromptEngine.build_json_retry(request)):
            for rule in ("published VIDEO TITLE", "never over 100 characters", "full YouTube description",
                         "seo_keywords", "not unrelated trending tags", "concrete visible subjects"):
                self.assertIn(rule, prompt)
        for changes in ({"caption": "x" * 101}, {"description": ""}, {"caption": ""}):
            bad = {**json.loads(self.response()), **changes}
            with patch.object(AIService, "_generate_from_provider", side_effect=[(json.dumps(bad), "test"), (self.response(), "test")]) as provider:
                AIService._generate_validated_response("test", request, PromptEngine.build(request))
                self.assertEqual(provider.call_count, 2)

    def test_generation_persists_goal_and_scenes_for_each_output(self):
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            db.add(User(id=1, name="Test", email="goal@test.invalid"))
            db.add(Brand(id=1, user_id=1, **vars(self.brand())))
            db.add(Project(id=1, user_id=1, brand_id=1, title="Finance", topic="Money",
                           platform="Instagram", content_type="Post", folder="test", path="test"))
            db.commit()
            generated_count = 0
            def unique_response(*args, **kwargs):
                nonlocal generated_count
                generated_count += 1
                response = json.loads(self.response())
                response["title"] += f" angle {generated_count}"
                response["caption"] += f" Tip {generated_count}."
                response["hashtags"] = [f"#MoneyTip{generated_count}"]
                response["scenes"][0]["visual_plan"] += f" composition {generated_count}"
                return json.dumps(response), "test"
            with patch("app.services.ai_service.credentials_for", return_value={"test": {}}), \
                 patch("app.services.billing_service.require_plan"), \
                 patch.object(AIService, "_generate_from_provider", side_effect=unique_response) as provider, \
                 patch("app.services.ai_service.DownloaderService.download", side_effect=lambda **kw: {"file_url": f"https://stock.test/{kw['scene_id']}.jpg"}):
                for goal in (*GOALS, None):
                    result = AIService.generate(self.request(content_goal=goal, outputs=["Instagram: Post", "Facebook: Post"]), db, 1)
                    previous_urls = []
                    for platform in ("instagram", "facebook"):
                        output = result["data"][platform]["post"]
                        content = db.get(Content, output["content_id"])
                        self.assertEqual(content.generation_config["excluded_media_urls"], previous_urls)
                        previous_urls.extend(scene["media_url"] for scene in output["scenes"])
                        self.assertEqual(content.generation_config.get("content_goal"), goal)
                        self.assertEqual(output["generation_config"].get("content_goal"), goal)
                        self.assertEqual(len(content.scenes), 1)
                        self.assertEqual(content.scenes[0].text, output["scenes"][0]["text"])
                        self.assertEqual(content.script, content.scenes[0].voice_text)
                        self.assertEqual(ContentService._serialize(content)["generation_config"].get("content_goal"), goal)
                        self.assertNotIn("share_trigger", content.generation_config)
                        self.assertEqual(content.generation_config["visual_plan"], [f"Overhead comparison of a pay slip and household expenses composition {content.title.rsplit(' ', 1)[-1]}"])
                        if goal:
                            self.assertIn(f"Content goal: {goal}", content.prompt)
                            self.assertIn("FinLogicMoney", content.prompt)
                            self.assertIn(f"{platform.title()}:", content.prompt)
                        else:
                            self.assertNotIn("content_goal", content.generation_config)
                            self.assertNotIn("Content goal:", content.prompt)
                youtube = AIService.generate(self.request(platforms=["YouTube"], content_types=["Community Post"]), db, 1)
                content = db.get(Content, youtube["content_id"])
                metadata = posting_metadata(content, "youtube")
                self.assertEqual(metadata["title"], content.caption)
                self.assertEqual(metadata["caption"], json.loads(self.response())["description"] + "\n\n" + content.hashtags)
                ContentService.update(db, content.id, 1, ContentUpdate(description="Edited description", keywords="salary budget"))
                self.assertEqual(ContentService._serialize(content)["description"], "Edited description")
                self.assertEqual(content.generation_config["branding"]["brand_name"], "FinLogicMoney")
                self.assertEqual(posting_metadata(content, "youtube")["caption"], "Edited description\n\n" + content.hashtags)
                self.assertEqual(posting_metadata(content, "youtube")["tags"], ["salary budget"])
            self.assertEqual(provider.call_count, 13)
            self.assertNotIn("Overhead comparison of a pay slip", provider.call_args_list[0].args[1])
            self.assertIn("Overhead comparison of a pay slip", provider.call_args_list[1].args[1])
            self.assertIn("OTHER FORMATS ALREADY CREATED", provider.call_args_list[1].args[1])
            self.assertIn("Lifestyle inflation angle 1", provider.call_args_list[1].args[1])

    def test_duplicate_format_metadata_retries_and_accepts_distinct_copy(self):
        previous = {"title": "Avoid debt", "caption": "Take control of debt", "hashtags": ["#Debt", "#Budget"]}
        valid = {**json.loads(self.response()), "title": "A practical debt checklist",
                 "caption": "Three steps to plan your repayments", "hashtags": ["#Debt", "#RepaymentPlan"]}
        for duplicate in ({"title": "Avoid debt!"}, {"caption": "Take control of debt."}, {"hashtags": ["#budget", "#debt"]}):
            with self.subTest(duplicate=duplicate), patch.object(AIService, "_generate_from_provider",
                 side_effect=[(json.dumps({**valid, **duplicate}), "test"), (json.dumps(valid), "test")]) as provider:
                _, _, result = AIService._generate_validated_response("test", self.request(), "Use different format copy", previous_outputs=[previous])
                self.assertEqual(provider.call_count, 2)
                self.assertEqual(result["title"], valid["title"])


if __name__ == "__main__":
    unittest.main()

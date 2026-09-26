import json
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from app.config.prompt_config import VISUAL_NICHE_BOUNDARIES

from app.schemas.ai import GenerateRequest
from app.services.ai_service import AIService
from app.services.prompt_engine import PromptEngine


class SceneSequenceTests(unittest.TestCase):
    def test_all_six_niches_and_thirteen_platform_formats(self):
        formats = {"Instagram": ["Reel", "Carousel", "Story", "Post", "Quote"],
                   "Facebook": ["Reel", "Carousel", "Story", "Post", "Quote"],
                   "YouTube": ["Shorts", "Long Video", "Community Post"]}
        expected_counts = {"Reel": 7, "Carousel": 6, "Story": 7, "Post": 1, "Quote": 1,
                           "Shorts": 7, "Long Video": 10, "Community Post": 1}
        checked = 0
        for niche, boundary in VISUAL_NICHE_BOUNDARIES.items():
            previous = []
            for platform, types in formats.items():
                for format_name in types:
                    with self.subTest(niche=niche, platform=platform, format=format_name):
                        # A quote package must not turn the other selected formats into quotes.
                        request = GenerateRequest(project_id=1, platforms=[platform], content_types=[format_name],
                            niche=niche, topic=boundary.split(",")[0], package="quote")
                        count, media_type, _, _, quote = PromptEngine.scene_settings(request)
                        self.assertEqual(count, expected_counts[format_name])
                        self.assertEqual(quote, format_name == "Quote")
                        if format_name in ("Quote", "Post", "Community Post"):
                            self.assertEqual(PromptEngine.scene_settings(request.model_copy(update={"scene_count": 7}))[0], 1)
                        self.assertEqual(media_type, "video" if format_name in ("Reel", "Story", "Shorts", "Long Video") else "image")
                        prompt = PromptEngine.build(request, brand=SimpleNamespace(name=niche), recent_visuals=previous)
                        self.assertIn(boundary, prompt)
                        self.assertIn(f"Topic: {request.topic}", prompt)
                        content = self.content(count)
                        identity = f"{platform} {format_name}"
                        content.update(title=f"Topic explained for {identity}", caption=f"Specific takeaway for {identity}",
                                       description="A complete topic explanation", hashtags=["#Topic", "#" + identity.replace(" ", "")])
                        for index, scene in enumerate(content["scenes"]):
                            scene["visual_plan"] = f"{identity} composition {index}"
                        AIService._validate_scene_sequence(content, request)
                        AIService._validate_output_variation(content, previous)
                        if previous:
                            for field in ("title", "caption", "hashtags"):
                                with self.assertRaises(ValueError):
                                    AIService._validate_output_variation({**content, field: previous[0][field]}, previous)
                            repeated = {**content, "scenes": [{"visual_plan": value} for value in previous[0]["generation_config"]["visual_plan"]]}
                            with self.assertRaises(ValueError):
                                AIService._validate_output_variation(repeated, previous)
                        previous.append({**content, "generation_config": {"visual_plan": [scene["visual_plan"] for scene in content["scenes"]]}})
                        checked += 1
        self.assertEqual(checked, 78)

    def request(self, content_type="Carousel", count=5):
        return GenerateRequest(project_id=1, platforms=["Instagram"], content_types=[content_type],
                               niche="Education", topic="How to grow tomatoes", package=content_type.lower(),
                               scene_count=count)

    def content(self, count=5):
        return {"title": "Growing tomatoes", "script": "Unrelated script",
                "scenes": [{"scene": 99, "text": f"Growing step {i}", "voice_text": f"Narration for step {i}."}
                           for i in range(1, count + 1)]}

    def test_ten_slide_carousel_preserves_ending_and_aligns_story(self):
        content = self.content(10)
        content["scenes"][-1]["text"] = "Harvest ripe tomatoes and enjoy your first homegrown meal."
        AIService._validate_scene_sequence(content, self.request(count=10))
        self.assertEqual(len(content["scenes"]), 10)
        self.assertTrue(content["story"].endswith(content["scenes"][-1]["text"]))
        self.assertEqual(content["script"], content["story"])
        self.assertEqual([s["scene_number"] for s in content["scenes"]], list(range(1, 11)))

    def test_video_script_matches_scene_narration(self):
        content = self.content()
        AIService._validate_scene_sequence(content, self.request("Reel"))
        self.assertEqual(content["script"], " ".join(s["voice_text"] for s in content["scenes"]))
        self.assertNotIn("Unrelated", content["script"])

    def test_missing_extra_duplicate_and_empty_scenes_are_rejected(self):
        cases = [self.content(4), self.content(6), self.content(), self.content()]
        cases[2]["scenes"][-1]["text"] = cases[2]["scenes"][0]["text"]
        cases[3]["scenes"][-1]["text"] = " "
        for content in cases:
            with self.subTest(content=content), self.assertRaises(ValueError):
                AIService._validate_scene_sequence(content, self.request())

    def test_video_missing_narration_is_rejected(self):
        content = self.content()
        del content["scenes"][2]["voice_text"]
        with self.assertRaises(ValueError):
            AIService._validate_scene_sequence(content, self.request("Reel"))

    def test_incomplete_sequence_retries_before_returning(self):
        request = self.request()
        with patch.object(AIService, "_generate_from_provider", side_effect=[
            (json.dumps(self.content(2)), "model"), (json.dumps(self.content()), "model")
        ]) as generate:
            _, _, content = AIService._generate_validated_response("test", request, PromptEngine.build(request))
        self.assertEqual(generate.call_count, 2)
        self.assertEqual(len(content["scenes"]), 5)

    def test_quote_remains_one_self_contained_scene(self):
        request = self.request("Quote", 5)
        content = self.content(1)
        content["scenes"][0]["text"] = "Plant a seed today.\nGive tomorrow a chance."
        AIService._validate_scene_sequence(content, request)
        self.assertEqual(content["script"], content["scenes"][0]["text"])
        self.assertIn("exactly one original two-line", PromptEngine.build(request))

    def test_retry_preserves_completeness_instructions(self):
        prompt = PromptEngine.build_json_retry(self.request(count=10))
        self.assertIn("exactly 10 scenes", prompt)
        self.assertIn("never replace it", prompt)
        self.assertIn("voice_text", prompt)
        self.assertNotIn("script under 60 words", prompt)


if __name__ == "__main__":
    unittest.main()

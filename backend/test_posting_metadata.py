import unittest
from types import SimpleNamespace
from fastapi import HTTPException
from app.services.publishing_media import posting_metadata


class PostingMetadataTests(unittest.TestCase):
    def content(self, **changes):
        return SimpleNamespace(**{
            **dict(title="My story", caption="Watch this #Story", hashtags="#Story, motivation, #Motivation", keywords="personal growth, mindset, Mindset"),
            **changes,
        })

    def test_youtube_fields_and_deduplication(self):
        result = posting_metadata(self.content(), "youtube")
        self.assertEqual(result, {"title": "Watch this #Story", "caption": "Watch this #Story\n\n#motivation", "tags": ["personal growth", "mindset"]})

    def test_youtube_caption_title_is_single_line_and_has_no_added_credits(self):
        result = posting_metadata(self.content(caption="  Your salary increased.\nYour lifestyle increased faster.  ",
                                              generation_config={"audio": {"license_note": "Music: Artist"}}), "youtube")
        self.assertEqual(result["title"], "Your salary increased. Your lifestyle increased faster.")
        self.assertIn("Music: Artist", result["caption"])

    def test_youtube_title_falls_back_when_caption_is_empty(self):
        for caption in (None, "", "   "):
            self.assertEqual(posting_metadata(self.content(caption=caption), "youtube")["title"], "My story")

    def test_youtube_validates_the_caption_title_not_the_internal_title(self):
        self.assertEqual(posting_metadata(self.content(title="x" * 101), "youtube")["title"], "Watch this #Story")
        self.assertEqual(len(posting_metadata(self.content(caption="x" * 100), "youtube")["title"]), 100)
        for changes in ({"caption": "x" * 101}, {"caption": "", "title": "x" * 101}, {"caption": "<invalid>"}):
            with self.subTest(changes=changes), self.assertRaises(HTTPException):
                posting_metadata(self.content(**changes), "youtube")

    def test_social_caption_includes_title(self):
        for provider in ["instagram", "facebook"]:
            self.assertEqual(posting_metadata(self.content(), provider)["title"], "My story")
            self.assertEqual(posting_metadata(self.content(), provider)["caption"], "My story\n\nWatch this #Story\n\n#motivation")

    def test_youtube_keyword_limit(self):
        with self.assertRaises(HTTPException):
            posting_metadata(self.content(keywords="x" * 501), "youtube")

    def test_missing_optional_fields(self):
        result = posting_metadata(self.content(caption=None, hashtags=None, keywords=None), "youtube")
        self.assertEqual(result["caption"], "")
        self.assertEqual(result["tags"], [])

    def test_music_attribution_is_in_description(self):
        result = posting_metadata(self.content(generation_config={"audio": {"license_note": "Music: Artist / CC BY"}}), "youtube")
        self.assertIn("\n\nMusic: Artist / CC BY\n\n", result["caption"])

    def test_youtube_uses_separate_description_and_preserves_tags_and_credit(self):
        content = self.content(caption="Why your raise disappears", hashtags="#Budgeting, #budgeting, #Saving",
                               generation_config={"description": "Learn how lifestyle inflation affects your budget. #Budgeting",
                                                  "audio": {"license_note": "Music: Artist"}})
        result = posting_metadata(content, "youtube")
        self.assertEqual(result["title"], "Why your raise disappears")
        self.assertEqual(result["caption"], "Learn how lifestyle inflation affects your budget. #Budgeting\n\nMusic: Artist\n\n#Saving")
        self.assertEqual(result["tags"], ["personal growth", "mindset"])
        self.assertNotIn("Learn how", posting_metadata(content, "facebook")["caption"])

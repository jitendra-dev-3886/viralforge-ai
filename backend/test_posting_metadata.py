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
        self.assertEqual(result, {"title": "My story", "caption": "Watch this #Story\n\n#motivation", "tags": ["personal growth", "mindset"]})

    def test_social_caption_includes_title(self):
        for provider in ["instagram", "facebook"]:
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

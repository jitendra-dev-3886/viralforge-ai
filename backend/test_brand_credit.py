import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.core.brand_credit import output_brand_name
from app.core.platform_branding import render_platform_username
from app.core.visual_style import STYLES


class BrandCreditTests(unittest.TestCase):
    def content(self, branding, brand="Project Brand"):
        return SimpleNamespace(
            generation_config={"branding": branding},
            project=SimpleNamespace(brand=SimpleNamespace(name=brand) if brand else None),
        )

    def test_saved_brand_wins_over_account_and_platform_handles(self):
        content = self.content({"brand_name": "My Brand", "username": "Account Name", "platform_usernames": {"instagram": "@handle"}})
        self.assertEqual(output_brand_name(content), "My Brand")

    def test_legacy_content_uses_project_brand(self):
        self.assertEqual(output_brand_name(self.content({"username": "Account Name"})), "Project Brand")
        self.assertEqual(output_brand_name(self.content({"brand_name": "  "})), "Project Brand")

    def test_missing_brand_does_not_leak_account_name(self):
        self.assertEqual(output_brand_name(self.content({"username": "Account Name"}, brand=None)), "")

    @patch("app.core.text_overlay.render_caption")
    def test_all_designs_render_literal_brand_name_without_at_prefix(self, render):
        for style in [None, *STYLES]:
            for platform in ["instagram", "youtube", "facebook"]:
                render_platform_username("My Brand", "unused.png", 1080, 1920, platform=platform, visual_style=style)
                self.assertEqual(render.call_args.args[0], "My Brand")


if __name__ == "__main__":
    unittest.main()

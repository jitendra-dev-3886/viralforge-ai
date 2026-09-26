import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from app.core.media_selection import best_for_query
from app.core.pexels_client import PexelsClient
from app.core.pixabay_client import PixabayClient
from app.services.downloader_service import DownloaderService
from app.services.project_render_service import ProjectRenderService


class StockSelectionTests(unittest.TestCase):
    def test_orientation_fallback_preserves_used_asset_exclusions(self):
        used = {"alt": "programming", "width": 1080, "height": 1920, "src": {"large2x": "used.jpg"}}
        fresh = {"alt": "programming", "width": 1920, "height": 1080, "src": {"large2x": "fresh.jpg"}}
        with patch.object(PexelsClient, "search_images", side_effect=lambda **kw: {"photos": [used] if kw.get("orientation") else [used, fresh]}) as search:
            result = PexelsClient.first_image("programming", "portrait", excluded_urls=["used.jpg"])
            self.assertEqual(result["file_url"], "fresh.jpg")
            self.assertEqual(search.call_count, 2)
            self.assertIsNone(search.call_args.kwargs["orientation"])

    def test_pexels_excludes_used_photo_and_all_video_renditions(self):
        with patch.object(PexelsClient, "search_images", return_value={"photos": [
            {"alt": "household bills", "width": 1080, "height": 1350, "src": {"large2x": "used.jpg?width=1000"}},
            {"alt": "household bills", "width": 1080, "height": 1350, "src": {"large2x": "fresh.jpg"}},
        ]}):
            self.assertEqual(PexelsClient.first_image("household bills", excluded_urls=["used.jpg?width=800"])["file_url"], "fresh.jpg")
        with patch.object(PexelsClient, "search_videos", return_value={"videos": [
            {"url": "https://pexels.com/video/household-bills", "width": 1080, "height": 1920,
             "video_files": [{"link": "used.mp4", "width": 1920, "height": 1080}, {"link": "other-size.mp4", "width": 1080, "height": 1920}]},
        ]}):
            self.assertIsNone(PexelsClient.first_video("household bills", "portrait", excluded_urls=["used.mp4"]))

    def test_pixabay_excludes_used_assets(self):
        with patch.object(PixabayClient, "search_images", return_value={"hits": [
            {"tags": "household bills", "imageWidth": 1000, "imageHeight": 1000, "largeImageURL": "used.jpg"},
        ]}):
            self.assertIsNone(PixabayClient.first_image("household bills", excluded_urls=["used.jpg"]))
        with patch.object(PixabayClient, "search_videos", return_value={"hits": [
            {"tags": "household bills", "videos": {"large": {"url": "used.mp4", "width": 1000, "height": 1000}}},
        ]}):
            self.assertIsNone(PixabayClient.first_video("household bills", excluded_urls=["used.mp4"]))
    def test_meditation_matches_action_without_requiring_lighting_metadata(self):
        relevant = {"alt": "Person practicing meditation", "width": 1080, "height": 1350}
        unrelated = {"alt": "Sunlight on a mountain in the morning", "width": 1080, "height": 1350}
        self.assertIs(self.select([unrelated, relevant], "person meditating morning sunlight"), relevant)
        self.assertIsNone(self.select([unrelated], "person meditating morning sunlight"))

    def test_partial_match_cannot_drop_the_distinguishing_subject(self):
        wrong = {"alt": "Wood panel installation", "width": 1080, "height": 1350}
        right = {"alt": "Solar panel installation", "width": 1920, "height": 1080}
        self.assertIsNone(self.select([wrong], "solar panel installation"))
        self.assertIs(self.select([wrong, right], "solar panel installation"), right)

    def test_downloader_prioritizes_scene_keyword_over_broad_prompt(self):
        scene = SimpleNamespace(id=1, user_id=1, project_id=1, content_id=1, scene_number=1,
                                media_type="image", media_id=None, image_prompt="green energy",
                                keyword="solar panel installation", video_prompt="green energy",
                                content=SimpleNamespace(platform="Instagram", content_type="Post"))
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = scene
        with patch("app.services.downloader_service.os.makedirs"), \
             patch.object(PexelsClient, "search_and_download", return_value=None) as pexels, \
             patch.object(PixabayClient, "search_and_download", return_value=None) as pixabay:
            with self.assertRaises(HTTPException):
                DownloaderService.download(db, 1, 1)
            for provider in (pexels, pixabay):
                self.assertEqual(provider.call_args_list[0].kwargs["keyword"], "solar panel installation")

    def test_fallback_queries_keep_topic_niche_project_order(self):
        scene = SimpleNamespace(scene_number=1,
            content=SimpleNamespace(generation_config={"topic": "Roman telescope camera", "niche": "Cosmic Knowledge"}),
            project=SimpleNamespace(topic="Space missions", niche="Astronomy", title="Explore universe",
                                    brand=SimpleNamespace(name="Cosmic Night")))
        queries = DownloaderService._search_queries(scene, "space telescope laboratory model")
        self.assertEqual(queries[:2], [("topic", "space telescope laboratory model"), ("topic", "space telescope")])
        levels = [level for level, _ in queries]
        self.assertEqual(levels, sorted(levels, key={"topic": 0, "niche": 1, "project": 2}.get))
        self.assertTrue(any(level == "niche" for level, _ in queries))
        self.assertIn(("project", "Astronomy"), queries)
        self.assertEqual(len(queries), len({query.casefold() for _, query in queries}))

    def test_empty_scene_keyword_can_use_project_context(self):
        scene = SimpleNamespace(scene_number=1, content=SimpleNamespace(),
                                project=SimpleNamespace(topic="galaxy", niche="", title=""))
        self.assertEqual(DownloaderService._search_queries(scene, ""), [("project", "galaxy")])

    def test_download_stops_at_first_successful_fallback_level(self):
        queries = [("topic", "space telescope"), ("niche", "galaxies"), ("project", "astronomy")]
        for expected_index, (expected_level, expected_query) in enumerate(queries):
            with self.subTest(level=expected_level):
                scene = SimpleNamespace(id=1, user_id=1, project_id=1, content_id=1, scene_number=1,
                    media_type="image", media_id=None, keyword="space telescope", image_prompt="", video_prompt="",
                    content=SimpleNamespace(platform="Instagram", content_type="Post"))
                db = MagicMock()
                db.query.return_value.filter.return_value.first.return_value = scene
                db.query.return_value.join.return_value.filter.return_value.all.return_value = [("already-used.jpg",)]
                asset = {"provider": "Pexels", "title": expected_query, "file_path": "image.jpg",
                         "file_url": "https://example.test/image.jpg", "mime_type": "image/jpeg", "extension": ".jpg"}
                with patch.object(DownloaderService, "_search_queries", return_value=queries), \
                     patch("app.services.downloader_service.os.makedirs"), \
                     patch("app.services.downloader_service.os.path.exists", return_value=True), \
                     patch.object(PexelsClient, "search_and_download", side_effect=lambda **kw: asset if kw["keyword"] == expected_query else None) as pexels, \
                     patch.object(PixabayClient, "search_and_download", return_value=None) as pixabay:
                    result = DownloaderService.download(db, 1, 1)
                    self.assertEqual(result["match_level"], expected_level)
                    self.assertEqual([call.kwargs["keyword"] for call in pexels.call_args_list], [query for _, query in queries[:expected_index + 1]])
                    self.assertEqual(pixabay.call_count, expected_index)
                    self.assertEqual(pexels.call_args.kwargs["excluded_urls"], ["already-used.jpg"])

    def select(self, items, query="household bills"):
        return best_for_query(items, lambda item: (item.get("width"), item.get("height")),
                              query=query, media_type="image", orientation="portrait")

    def test_relevance_wins_over_perfect_dimensions(self):
        irrelevant = {"alt": "Mountain sunset", "width": 1080, "height": 1350}
        relevant = {"alt": "Calculating household bills", "width": 1920, "height": 1080}
        self.assertIs(self.select([irrelevant, relevant]), relevant)

    def test_rejects_missing_metadata_and_generic_word_overlap(self):
        for item in ({}, {"alt": "Person standing in a beautiful mountain background"},
                     {"url": "https://example.com/photo/123", "photographer": "Household Bills"}):
            self.assertIsNone(self.select([{**item, "width": 1080, "height": 1350}], "person household bills"))
        self.assertIsNone(self.select([{"alt": "person", "width": 100, "height": 100}], "person"))

    def test_exact_subject_beats_partial_match_and_dimensions_break_ties(self):
        partial = {"tags": "household bills", "width": 1080, "height": 1350}
        exact = {"tags": "calculating household bills", "width": 1920, "height": 1080}
        self.assertIs(self.select([partial, exact], "calculating household bills"), exact)
        portrait = {**exact, "width": 1080, "height": 1350}
        self.assertIs(self.select([exact, portrait]), portrait)

    def test_pexels_photo_and_video_use_descriptive_metadata(self):
        with patch.object(PexelsClient, "search_images", return_value={"photos": [
            {"alt": "Mountain sunset", "width": 1080, "height": 1350, "src": {"large2x": "wrong"}},
            {"alt": "Household bills", "width": 1920, "height": 1080, "src": {"large2x": "right"}},
        ]}):
            self.assertEqual(PexelsClient.first_image("household bills", "portrait")["file_url"], "right")
        with patch.object(PexelsClient, "search_videos", return_value={"videos": [
            {"url": "https://pexels.com/video/mountain-sunset-123/", "width": 1080, "height": 1920},
            {"url": "https://pexels.com/video/calculating-household-bills-456/", "width": 1920, "height": 1080,
             "video_files": [{"file_type": "video/mp4", "link": "right", "width": 1920, "height": 1080}]},
        ]}):
            self.assertEqual(PexelsClient.first_video("household bills", "portrait")["file_url"], "right")

    def test_pixabay_photo_and_video_use_tags(self):
        with patch.object(PixabayClient, "search_images", return_value={"hits": [
            {"tags": "mountain, sunset", "imageWidth": 1080, "imageHeight": 1350, "largeImageURL": "wrong"},
            {"tags": "household, bills", "imageWidth": 1920, "imageHeight": 1080, "largeImageURL": "right"},
        ]}):
            self.assertEqual(PixabayClient.first_image("household bills", "portrait")["file_url"], "right")
        with patch.object(PixabayClient, "search_videos", return_value={"hits": [
            {"tags": "mountain, sunset", "videos": {"large": {"url": "wrong", "width": 1080, "height": 1920}}},
            {"tags": "household, bills", "videos": {"large": {"url": "right", "width": 1920, "height": 1080}}},
        ]}):
            self.assertEqual(PixabayClient.first_video("household bills", "portrait")["file_url"], "right")

    def test_unrelated_results_are_not_downloaded(self):
        for client in (PexelsClient, PixabayClient):
            with patch.object(client, "first_image", return_value=None), patch.object(client, "download_file") as download:
                self.assertIsNone(client.search_and_download("household bills", "image", "unused.jpg"))
                download.assert_not_called()

    def test_downloader_tries_only_both_stock_providers_then_reports_no_match(self):
        scene = SimpleNamespace(id=1, user_id=1, project_id=1, content_id=1, scene_number=1,
                                media_type="image", media_id=None, image_prompt="household bills", keyword="household bills",
                                video_prompt="household bills", content=SimpleNamespace(platform="Instagram", content_type="Post"))
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = scene
        with patch("app.services.downloader_service.os.makedirs"), \
             patch.object(PexelsClient, "search_and_download", return_value=None) as pexels, \
             patch.object(PixabayClient, "search_and_download", return_value=None) as pixabay:
            with self.assertRaises(HTTPException) as error:
                DownloaderService.download(db, 1, 1)
            self.assertEqual(error.exception.status_code, 404)
            self.assertIn("No relevant media", error.exception.detail)
            for provider in (pexels, pixabay):
                self.assertEqual(provider.call_count, 1)
                self.assertEqual(provider.call_args.kwargs["keyword"], "household bills")
            db.add.assert_not_called()

    def test_export_does_not_borrow_another_scene_when_search_fails(self):
        db = MagicMock()
        scene = SimpleNamespace(id=1, scene_number=1, media_id=None)
        other = SimpleNamespace(id=2, scene_number=2, media_id=22)
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id=1)
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [scene, other]
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(ProjectRenderService, "BASE_DIR", Path(folder)), \
             patch.object(DownloaderService, "download", side_effect=HTTPException(404, "No relevant media")), \
             patch("app.services.project_render_service.RenderService.generate") as render:
            with self.assertRaises(HTTPException) as error:
                ProjectRenderService.generate(db, 1, 1, content_id=1)
            self.assertEqual(error.exception.status_code, 422)
            self.assertIn("Scene 1 has no matching media", error.exception.detail)
            self.assertIsNone(scene.media_id)
            render.assert_not_called()


if __name__ == "__main__":
    unittest.main()

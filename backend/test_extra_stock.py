import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PIL import Image

from app.core.coverr_client import CoverrClient
from app.core.openverse_client import OpenverseClient
from app.services.downloader_service import DownloaderService


class ExtraStockTests(unittest.TestCase):
    def video(self):
        return {"id": "abc", "title": "Computer programming", "max_width": 1920, "max_height": 1080,
                "duration": 5, "urls": {"mp4_download": "https://storage.coverr.co/videos/abc/download?token=test"}}

    def photo(self):
        return {"id": "abc", "title": "Computer programming", "width": 1200, "height": 900,
                "license": "cc0", "tags": [], "url": "https://cdn.stocksnap.io/img/abc.jpg"}

    def download_response(self, data, mime):
        response = MagicMock(status_code=200, headers={"Content-Type": mime})
        response.__enter__.return_value = response
        response.iter_content.return_value = [data]
        return response

    def test_coverr_search_and_tracked_download(self):
        search = MagicMock()
        search.json.return_value = {"hits": [self.video()]}
        with tempfile.TemporaryDirectory() as folder, patch.object(CoverrClient, "API_KEY", "test-key"), \
             patch("app.core.coverr_client.requests.get", side_effect=[search, self.download_response(b"video", "video/mp4")]) as get:
            result = CoverrClient.search_and_download("computer programming", "video", str(Path(folder) / "clip.mp4"))
            self.assertEqual(Path(result["file_path"]).read_bytes(), b"video")
            self.assertEqual(get.call_args_list[0].kwargs["params"]["urls"], "true")
            self.assertIn("/download?", get.call_args_list[1].args[0])
            self.assertNotIn("headers", get.call_args_list[1].kwargs)

    def test_coverr_excludes_existing_asset_with_different_token(self):
        search = MagicMock()
        search.json.return_value = {"hits": [self.video()]}
        with patch.object(CoverrClient, "API_KEY", "test"), patch("app.core.coverr_client.requests.get", return_value=search) as get:
            self.assertIsNone(CoverrClient.search_and_download("computer programming", "video", "unused.mp4",
                excluded_urls=["https://storage.coverr.co/videos/abc?token=old"]))
            self.assertEqual(get.call_count, 1)

    def test_openverse_converts_image_and_filters_license(self):
        data = io.BytesIO()
        Image.new("RGB", (1200, 900)).save(data, "PNG")
        search = MagicMock()
        search.json.return_value = {"results": [self.photo()]}
        with tempfile.TemporaryDirectory() as folder, patch.object(OpenverseClient, "ENABLED", True), \
             patch("app.core.openverse_client.requests.get", side_effect=[search, self.download_response(data.getvalue(), "image/png")]) as get:
            result = OpenverseClient.search_and_download("computer programming", "image", str(Path(folder) / "photo.jpg"))
            with Image.open(result["file_path"]) as image:
                self.assertEqual(image.format, "JPEG")
            self.assertEqual(get.call_args_list[0].kwargs["params"]["license"], "cc0")
        for changes in ({"license": "by"}, {"mature": True}, {"url": "https://localhost/internal"}):
            search.json.return_value = {"results": [{**self.photo(), **changes}]}
            with patch.object(OpenverseClient, "ENABLED", True), patch("app.core.openverse_client.requests.get", return_value=search) as get:
                self.assertIsNone(OpenverseClient.search_and_download("computer programming", "image", "unused.jpg"))
                self.assertEqual(get.call_count, 1)

    def test_unconfigured_or_wrong_media_type_makes_no_request(self):
        with patch.object(CoverrClient, "API_KEY", ""), patch.object(OpenverseClient, "ENABLED", False), patch("requests.get") as get:
            self.assertIsNone(CoverrClient.search_and_download("test", "video", "unused"))
            self.assertIsNone(OpenverseClient.search_and_download("test", "image", "unused"))
            get.assert_not_called()

    def test_downloader_falls_back_for_both_media_types(self):
        for kind, client in (("video", CoverrClient), ("image", OpenverseClient)):
            scene = SimpleNamespace(id=1, user_id=1, project_id=1, content_id=1, scene_number=1,
                media_type=kind, media_id=None, keyword="computer programming", image_prompt="", video_prompt="",
                content=SimpleNamespace(platform="Instagram", content_type="Reel" if kind == "video" else "Post"))
            db = MagicMock()
            db.query.return_value.filter.return_value.first.return_value = scene
            asset = {"provider": client.__name__.replace("Client", ""), "file_path": "asset", "mime_type": "video/mp4" if kind == "video" else "image/jpeg", "extension": ".mp4" if kind == "video" else ".jpg"}
            with patch.object(CoverrClient, "API_KEY", "test"), patch.object(OpenverseClient, "ENABLED", True), \
                 patch("app.services.downloader_service.os.makedirs"), patch("app.services.downloader_service.os.path.exists", return_value=True), \
                 patch("app.services.downloader_service.PexelsClient.search_and_download", return_value=None), \
                 patch("app.services.downloader_service.PixabayClient.search_and_download", return_value=None), \
                 patch.object(client, "search_and_download", return_value=asset) as fallback:
                result = DownloaderService.download(db, 1, 1)
                self.assertEqual(result["provider"], asset["provider"])
                self.assertEqual(fallback.call_count, 1)


if __name__ == "__main__":
    unittest.main()

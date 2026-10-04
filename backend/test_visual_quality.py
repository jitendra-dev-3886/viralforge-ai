import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image
from app.core.media_selection import best_by_dimensions
from app.core.visual_download import download_visual, VisualResolutionError


class VisualQualityTests(unittest.TestCase):
    def select(self, sizes):
        return best_by_dimensions(sizes, lambda item: item, media_type="video", orientation="portrait")

    def test_720p_cannot_beat_full_hd_on_aspect_ratio(self):
        self.assertEqual(self.select([(720, 1280), (1920, 1080)]), (1920, 1080))
        self.assertEqual(self.select([(1080, 1920)]), (1080, 1920))

    def test_no_low_resolution_fallback(self):
        self.assertIsNone(self.select([(720, 1280), (480, 854), (1080, 1080), (0, 0)]))

    def test_download_rejects_small_preview_and_preserves_existing_file(self):
        for size, accepted in [((720, 1280), False), ((1080, 1920), True)]:
            buffer = io.BytesIO()
            Image.new("RGB", size).save(buffer, "JPEG")
            response = MagicMock(headers={})
            response.__enter__.return_value = response
            response.iter_content.return_value = [buffer.getvalue()]
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "photo.jpg"
                path.write_bytes(b"existing")
                with patch("app.core.visual_download.requests.get", return_value=response):
                    if accepted:
                        result = download_visual("https://example.test/photo", str(path))
                        self.assertEqual((result["width"], result["height"]), size)
                    else:
                        with self.assertRaises(VisualResolutionError):
                            download_visual("https://example.test/photo", str(path))
                        self.assertEqual(path.read_bytes(), b"existing")
                self.assertFalse(Path(str(path) + ".part").exists())

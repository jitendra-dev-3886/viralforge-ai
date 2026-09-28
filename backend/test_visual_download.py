import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.visual_download import MAX_VISUAL_BYTES, VisualSizeLimitError, download_visual


class VisualDownloadTests(unittest.TestCase):
    def test_size_boundaries_and_untrusted_headers(self):
        cases = [
            ({"Content-Length": str(MAX_VISUAL_BYTES)}, [b"x" * MAX_VISUAL_BYTES], True),
            ({"Content-Length": str(MAX_VISUAL_BYTES + 1)}, [], False),
            ({}, [b"x" * MAX_VISUAL_BYTES, b"x"], False),
            ({"Content-Length": "1"}, [b"x" * MAX_VISUAL_BYTES, b"x"], False),
            ({"Content-Length": "invalid"}, [b"small"], True),
        ]
        for headers, chunks, succeeds in cases:
            with self.subTest(headers=headers, succeeds=succeeds), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "visual.mp4"
                path.write_bytes(b"existing")
                response = MagicMock(headers=headers)
                response.__enter__.return_value = response
                response.iter_content.return_value = chunks
                with patch("app.core.visual_download.requests.get", return_value=response):
                    if succeeds:
                        result = download_visual("https://example.test/visual", str(path))
                        self.assertEqual(result["file_size"], sum(map(len, chunks)))
                    else:
                        with self.assertRaises(VisualSizeLimitError):
                            download_visual("https://example.test/visual", str(path))
                        self.assertEqual(path.read_bytes(), b"existing")
                self.assertFalse(Path(str(path) + ".part").exists())
                response.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()

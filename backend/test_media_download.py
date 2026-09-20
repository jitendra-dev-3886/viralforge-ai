import asyncio
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from app.api.media import download_media
from app.schemas.media import MediaDownloadRequest


class MediaDownloadTests(unittest.TestCase):
    def request(self, ids, records):
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = records
        return download_media(MediaDownloadRequest(media_ids=ids), db, 1)

    def test_unavailable_record_rejects_entire_selection(self):
        with self.assertRaises(HTTPException) as error:
            self.request([1, 2], [SimpleNamespace(id=1)])
        self.assertEqual(error.exception.status_code, 404)

    def test_missing_file_rejects_entire_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            existing = Path(folder) / "exists.mp4"
            existing.write_bytes(b"example")
            records = [SimpleNamespace(file_path=str(existing)), SimpleNamespace(file_path=str(Path(folder) / "missing.mp4"))]
            with patch("app.api.media._safe_media_path", side_effect=lambda path: Path(path)):
                with self.assertRaises(HTTPException):
                    self.request([1, 2], records)

    def test_archive_preserves_all_files_with_duplicate_names(self):
        with tempfile.TemporaryDirectory() as folder:
            records = []
            for index, name in enumerate(["Video.mp4", "video.mp4", "2-1-video.mp4"], 1):
                path = Path(folder) / f"source-{index}.mp4"
                path.write_bytes(str(index).encode())
                records.append(SimpleNamespace(id=index, file_path=str(path), file_name=name, mime_type="video/mp4"))
            with patch("app.api.media._safe_media_path", side_effect=lambda path: Path(path)):
                response = self.request([1, 2, 3], records)
            try:
                with zipfile.ZipFile(response.path) as archive:
                    names = archive.namelist()
                    self.assertEqual(len({name.casefold() for name in names}), 3)
                    self.assertEqual({archive.read(name) for name in names}, {b"1", b"2", b"3"})
            finally:
                asyncio.run(response.background())

    def test_single_file_keeps_original_hindi_filename(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.mp4"
            path.write_bytes(b"example")
            record = SimpleNamespace(id=1, file_path=str(path), file_name="नई शुरुआत.mp4", mime_type="video/mp4")
            with patch("app.api.media._safe_media_path", return_value=path):
                response = self.request([1], [record])
            self.assertEqual(response.filename, record.file_name)
            self.assertIn("filename*=utf-8''", response.headers["content-disposition"])


if __name__ == "__main__":
    unittest.main()

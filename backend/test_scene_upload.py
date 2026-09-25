import asyncio
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException, UploadFile
from app.api.scene import upload_scene_media


class SceneUploadTests(unittest.TestCase):
    def setUp(self):
        self.scene = SimpleNamespace(id=7, project_id=3, media_id=12, media_type="image", status="ready")
        self.db = MagicMock()
        self.db.query.return_value.filter_by.return_value.first.return_value = self.scene

    def upload(self, filename, payload=b"test"):
        return asyncio.run(upload_scene_media(7, UploadFile(filename=filename, file=io.BytesIO(payload)), self.db, 2))

    def test_missing_or_other_users_scene(self):
        self.db.query.return_value.filter_by.return_value.first.return_value = None
        with self.assertRaises(HTTPException) as error:
            self.upload("clip.mp4")
        self.assertEqual(error.exception.status_code, 404)
        self.db.query.return_value.filter_by.assert_called_once_with(id=7, user_id=2)
        self.db.commit.assert_not_called()

    def test_unsupported_file_leaves_scene_unchanged(self):
        with self.assertRaises(HTTPException) as error:
            self.upload("script.svg")
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.scene.media_id, 12)

    def test_valid_uploads_link_only_selected_scene(self):
        for extension, kind in [("png", "image"), ("mp4", "video")]:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                def paths(value):
                    return Path(folder) if value == "storage/projects" else Path(value)
                self.db.flush.side_effect = lambda: setattr(self.db.add.call_args.args[0], "id", 99)
                with patch("app.api.scene.Path", side_effect=paths), patch("app.api.scene.FFmpegClient.is_media_readable", return_value=True):
                    result = self.upload(f"source.{extension}")
                self.assertEqual(result["media_type"], kind)
                self.assertEqual(self.scene.media_id, 99)
                self.assertEqual(self.scene.media_type, kind)
                self.assertEqual(len(list(Path(folder).rglob(f"*.{extension}"))), 1)

    def test_invalid_media_is_removed_without_replacing_existing(self):
        with tempfile.TemporaryDirectory() as folder:
            def paths(value):
                return Path(folder) if value == "storage/projects" else Path(value)
            with patch("app.api.scene.Path", side_effect=paths), patch("app.api.scene.FFmpegClient.is_media_readable", return_value=False):
                with self.assertRaises(HTTPException) as error:
                    self.upload("broken.mp4")
            self.assertEqual(error.exception.status_code, 422)
            self.assertEqual(self.scene.media_id, 12)
            self.assertFalse(list(Path(folder).rglob("*.mp4")))
            self.db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()

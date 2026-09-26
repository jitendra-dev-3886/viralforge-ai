import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.media_service import MediaService, _storage_path, _file_is_shared


class MediaDeleteTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "media.mp4"
        self.path.write_bytes(b"media")
        self.media = SimpleNamespace(id=1, file_path=str(self.path))
        self.db = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = self.media

    def delete(self, shared=False):
        with patch("app.services.media_service._storage_path", return_value=self.path), patch("app.services.media_service._file_is_shared", return_value=shared):
            return MediaService.delete(self.db, 1, 1)

    def test_deletes_local_file_and_record(self):
        self.assertTrue(self.delete()["success"])
        self.assertFalse(self.path.exists())
        self.db.delete.assert_called_once_with(self.media)
        self.db.commit.assert_called_once()

    def test_keeps_shared_file(self):
        self.assertTrue(self.delete(shared=True)["success"])
        self.assertTrue(self.path.exists())

    def test_missing_file_still_deletes_record(self):
        self.path.unlink()
        self.assertTrue(self.delete()["success"])

    def test_locked_file_rolls_back_record(self):
        with patch.object(Path, "unlink", side_effect=PermissionError):
            self.assertFalse(self.delete()["success"])
        self.db.rollback.assert_called_once()
        self.db.commit.assert_not_called()
        self.assertTrue(self.path.exists())

    def test_outside_storage_is_rejected(self):
        self.assertIsNone(_storage_path(str(self.path)))
        self.assertIsNone(_storage_path("storage/../../secret.txt"))

    def test_relative_storage_path_resolves(self):
        self.assertEqual(_storage_path("storage/example.mp4"), (Path.cwd() / "storage/example.mp4").resolve())

    def test_shared_reference_is_detected(self):
        self.db.query.return_value.filter.return_value.all.return_value = [("storage/example.mp4",)]
        self.db.query.return_value.all.return_value = []
        self.assertTrue(_file_is_shared(self.db, self.media, _storage_path("storage/example.mp4")))


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.schemas.voice import VoiceCreate
from app.services.voice_service import VoiceService
from app.services.render_service import RenderService


class VoiceSceneTextTests(unittest.IsolatedAsyncioTestCase):
    async def test_generation_uses_saved_overlay_not_old_narration_or_request(self):
        db = MagicMock()
        scene = SimpleNamespace(text="Plant the seeds.", voice_text="Plant the seeds. Extra explanation.", scene_number=1)
        db.query.return_value.filter.return_value.first.side_effect = [object(), object(), scene]
        request = VoiceCreate(project_id=1, content_id=2, scene_id=3, text="Old narration with extra words")

        async def save(path):
            Path(path).write_bytes(b"mock audio")

        with tempfile.TemporaryDirectory() as folder, \
                patch.object(VoiceService, "BASE_DIR", Path(folder)), \
                patch("app.services.voice_service.edge_tts.Communicate") as tts:
            tts.return_value.save.side_effect = save
            result = await VoiceService.generate(db, 1, request)
        self.assertTrue(result["success"], result.get("message"))
        self.assertEqual(tts.call_args.kwargs["text"], scene.text)
        self.assertEqual(result["voice"].text, scene.text)

    async def test_regeneration_reads_current_scene_instead_of_old_recording_text(self):
        db = MagicMock()
        voice = SimpleNamespace(scene_id=3, project_id=1, text="Old extra words", language="English",
                                provider="edge-tts",
                                voice="en-US-AriaNeural", audio_path=None, speed="+0%", pitch="+0Hz",
                                scene=SimpleNamespace(scene_number=1))
        scene = SimpleNamespace(text="Updated overlay.")
        db.query.return_value.filter.return_value.first.side_effect = [voice, scene, MagicMock()]

        async def save(path):
            Path(path).write_bytes(b"mock audio")

        with tempfile.TemporaryDirectory() as folder, \
                patch.object(VoiceService, "BASE_DIR", Path(folder)), \
                patch("app.services.voice_service.edge_tts.Communicate") as tts:
            tts.return_value.save.side_effect = save
            result = await VoiceService.regenerate(db, 7, 1)
        self.assertTrue(result["success"], result.get("message"))
        self.assertEqual(tts.call_args.kwargs["text"], scene.text)
        self.assertEqual(voice.text, scene.text)

    def test_export_rejects_extra_spoken_words_before_rendering(self):
        db = MagicMock()
        scene = SimpleNamespace(id=3, content_id=2, project_id=1, scene_number=1, media_id=4,
                                text="Plant the seeds.", content=SimpleNamespace(generation_config={}))
        voice = SimpleNamespace(text="Plant the seeds. Extra words.")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.png"
            source.write_bytes(b"mock source")
            db.query.return_value.filter.return_value.first.side_effect = [scene, SimpleNamespace(file_path=str(source))]
            db.query.return_value.filter.return_value.order_by.return_value.first.return_value = voice
            with patch("app.services.render_service.BACKEND_DIR", root), \
                    patch("app.services.render_service.FFmpegClient.render_media") as render:
                with self.assertRaises(HTTPException) as caught:
                    RenderService.generate(db, 3, 1)
                self.assertEqual(caught.exception.status_code, 422)
                self.assertIn("does not match its overlay", caught.exception.detail)
                render.assert_not_called()

import tempfile
import unittest
from pathlib import Path

from app.core.text_overlay import caption_font, render_caption, wrap_words
from PIL import Image, ImageFont
from app.core.ffmpeg_client import FFmpegClient


class TextOverlayTests(unittest.TestCase):
    def test_hindi_words_are_never_split_or_dropped(self):
        text = "सफलता की शुरुआत विश्वास से होती है। अपनी ज़िंदगी में नए सपनों को उड़ान दीजिए।"
        font = ImageFont.truetype(caption_font(text), 48, layout_engine=ImageFont.Layout.RAQM)
        wrapped = wrap_words(text, font, 200)
        self.assertEqual(wrapped.split(), text.split())
        self.assertGreater(len(wrapped.splitlines()), 5)

    def test_caption_fits_all_aspect_ratios(self):
        text = "कड़ी मेहनत और दृढ़ विश्वास\nआपके सपनों को नई उड़ान देते हैं। " * 4
        with tempfile.TemporaryDirectory() as directory:
            for width, height in [(1080, 1920), (1080, 1080), (1920, 1080), (1080, 1350)]:
                output = Path(directory) / "caption.png"
                render_caption(text, output, width, height)
                with Image.open(output) as image:
                    self.assertLessEqual(image.width, width * .84)
                    self.assertLessEqual(image.height, height * .42)
                    self.assertIsNotNone(image.getbbox())

    def test_literal_symbols_and_empty_text(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "caption.png"
            render_caption("100% सही: 'विश्वास' {नई शुरुआत} \\ test", output, 1080, 1080)
            self.assertTrue(output.is_file())
            render_caption("", output, 1080, 1080)
            with Image.open(output) as image:
                self.assertIsNone(image.getbbox())

    def test_real_ffmpeg_render_with_hindi_logo_and_audio(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source, logo, audio, output = [folder / name for name in ("source.png", "logo.png", "voice.wav", "result.mp4")]
            Image.new("RGB", (360, 640), "#294638").save(source)
            Image.new("RGBA", (40, 40), "coral").save(logo)
            subprocess.run([FFmpegClient.check_ffmpeg(), "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1", str(audio)], check=True)
            FFmpegClient.render_media(str(source), str(output), duration=1, width=360, height=640,
                audio_path=str(audio), logo_path=str(logo), overlay_text="सपनों को नई उड़ान दीजिए।\n100% विश्वास रखें!", username="नई शुरुआत", text_x_pct=97, text_y_pct=97)
            self.assertTrue(FFmpegClient.is_media_readable(str(output)))
            self.assertFalse(list(folder.glob("*.overlay.png")))
            self.assertFalse(list(folder.glob("*.username.png")))

    def test_render_without_audio_logo_or_captions(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source, output = folder / "source.png", folder / "result.mp4"
            Image.new("RGB", (360, 360), "#294638").save(source)
            FFmpegClient.render_media(str(source), str(output), duration=1, width=360, height=360)
            self.assertTrue(FFmpegClient.is_media_readable(str(output)))


if __name__ == "__main__":
    unittest.main()

"""Exercise real styled exports without cloud providers or a database."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pydantic import ValidationError

from app.core.ffmpeg_client import FFmpegClient
from app.core.visual_style import STYLES, resolve_layout, render_style_frame
from app.core.text_overlay import render_caption, render_logo
from app.schemas.ai import GenerateRequest
from app.services.prompt_engine import PromptEngine


class VisualStyleTests(unittest.TestCase):
    def test_compact_translucent_captions_and_no_full_frame_panels(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for style_id in STYLES:
                render_style_frame(style_id, folder / "frame.png", 720, 900)
                with Image.open(folder / "frame.png") as frame:
                    self.assertIsNone(frame.getbbox())
                render_caption("Hello", folder / "caption.png", 720, 900, visual_style=style_id)
                with Image.open(folder / "caption.png") as caption:
                    self.assertLess(caption.width, 720 * .5)
                    self.assertTrue(any(caption.getchannel("A").histogram()[1:255]))
                render_caption("Hello", folder / "hidden.png", 720, 900, visual_style=style_id, opacity=0)
                with Image.open(folder / "hidden.png") as caption:
                    self.assertIsNone(caption.getbbox())
            source = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
            source.putpixel((40, 40), (255, 0, 255, 255))
            source.save(folder / "logo.png")
            render_logo(folder / "logo.png", folder / "brand.png", 720, "minimal", opacity=.5)
            with Image.open(folder / "brand.png") as brand:
                self.assertEqual(brand.getpixel((0, 0))[3], 0)
                self.assertLessEqual(brand.getchannel("A").getextrema()[1], 128)

    def test_old_defaults_upgrade_but_manual_positions_survive(self):
        old = {"text": {"x": 50, "y": 72}, "logo": {"x": 10, "y": 8}, "username": {"x": 82, "y": 92}}
        self.assertEqual(resolve_layout("minimal", {"overlay_layout": old}), STYLES["minimal"]["layout"])
        old["logo"]["x"] = 20
        self.assertEqual(resolve_layout("minimal", {"overlay_layout": old}), old)
        self.assertEqual(resolve_layout("minimal", {"overlay_layout": old, "visual_layout_version": 2}), old)

    def test_request_validation_and_prompt_preserve_tone(self):
        values = dict(project_id=1, platforms=["Instagram"], content_types=["Carousel"],
                      niche="Education", topic="Build good habits", package="carousel", style="Educational")
        self.assertIsNone(GenerateRequest(**values).visual_style)
        with self.assertRaises(ValidationError):
            GenerateRequest(**values, visual_style="unknown")
        for style_id, preset in STYLES.items():
            request = GenerateRequest(**values, visual_style=style_id)
            prompt = PromptEngine.build(request)
            self.assertIn("Style or tone: Educational", prompt)
            self.assertIn(preset["description"], prompt)

    def test_all_styles_export_distinct_pngs_in_every_format(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / "source.png"
            Image.new("RGB", (360, 640), "#526b70").save(source)
            logo = folder / "brand.png"
            Image.new("RGBA", (120, 50), "#ff00ff").save(logo)
            for width, height in [(360, 640), (360, 450), (360, 360), (640, 360)]:
                pixels = set()
                for style_id, preset in STYLES.items():
                    with self.subTest(style=style_id, size=(width, height)):
                        output = folder / f"{style_id}.png"
                        FFmpegClient.render_media(str(source), str(output), duration=1,
                            width=width, height=height, visual_style=style_id, as_image=True,
                            overlay_text="Small steps. Remarkable stories.", username="My brand", logo_path=str(logo))
                        with Image.open(output) as image:
                            self.assertEqual(image.size, (width, height))
                            # An uncovered part of the media must survive a still export.
                            self.assertGreater(min(image.convert("RGB").getpixel((round(width * .94), round(height * .35)))), 30)
                            # The non-square brand mark appears at this style's own default position.
                            x, y = preset["layout"]["logo"].values()
                            center = image.convert("RGB").getpixel((round(width * x / 100), round(height * y / 100)))
                            if preset["logo"].get("visible") is False:
                                self.assertLess(center[0], 180)
                            else:
                                self.assertGreater(center[0], 180)
                                self.assertLess(center[1], 90)
                                self.assertGreater(center[2], 180)
                            pixels.add(image.tobytes())
                self.assertEqual(len(pixels), 6)
            self.assertFalse(list(folder.glob("*.frame.png")))
            self.assertFalse(list(folder.glob("*.overlay.png")))
            self.assertFalse(list(folder.glob("*.logo.png")))

    def test_all_styles_produce_readable_video(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / "source.png"
            Image.new("RGB", (360, 640), "#526b70").save(source)
            for style_id in STYLES:
                with self.subTest(style=style_id):
                    output = folder / f"{style_id}.mp4"
                    FFmpegClient.render_media(str(source), str(output), duration=1,
                        width=360, height=640, visual_style=style_id,
                        overlay_text="नई शुरुआत से सपनों को उड़ान दें।", username="My brand")
                    self.assertTrue(FFmpegClient.is_media_readable(str(output)))
            self.assertFalse(list(folder.glob("*.frame.png")))


if __name__ == "__main__":
    unittest.main()

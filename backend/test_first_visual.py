"""Encode real exports and inspect decoded frames, rather than filter strings."""
import contextlib
import array
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from app.core.ffmpeg_client import FFmpegClient
from PIL import Image


class FirstVisualTests(unittest.TestCase):
    def test_first_visual_survives_concat_and_music(self):
        ffmpeg = FFmpegClient.check_ffmpeg()

        def run(*args):
            return subprocess.run([ffmpeg, "-v", "error", "-y", *map(str, args)],
                                  check=True, capture_output=True).stdout

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "source.png"
            Image.new("RGB", (360, 640), (210, 90, 40)).save(image)
            video = root / "source.mp4"
            # Exercise nonzero source timestamps as well as still images.
            run("-loop", "1", "-i", image, "-t", "2", "-vf", "setpts=PTS+0.5/TB",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", video)
            voice, music = root / "voice.wav", root / "music.wav"
            run("-f", "lavfi", "-i", "sine=frequency=880:duration=1.5",
                "-af", "adelay=300:all=1", voice)
            run("-f", "lavfi", "-i", "sine=frequency=220:duration=0.5", music)

            def frame(path, seconds):
                raw = run("-i", path, "-ss", seconds, "-frames:v", "1",
                          "-vf", "scale=90:160", "-pix_fmt", "rgb24", "-f", "rawvideo", "-")
                return Image.frombytes("RGB", (90, 160), raw)

            def level(path, seconds):
                raw = run("-ss", seconds, "-i", path, "-t", "0.1", "-map", "0:a:0",
                          "-ac", "1", "-f", "f32le", "-")
                samples = array.array("f", raw)
                return (sum(x*x for x in samples) / len(samples)) ** .5

            for source in (image, video):
                with self.subTest(source=source.suffix):
                    first, second = root / "first.mp4", root / "second.mp4"
                    common = dict(duration=2, width=1080, height=1920, transition="fade")
                    result = FFmpegClient.render_media(str(source), str(first), audio_path=str(voice),
                                                       overlay_text="Scene one", **common)
                    self.assertEqual(result["duration"], 2)
                    FFmpegClient.render_media(str(image), str(second), overlay_text="Scene two",
                                              entrance_transition=True, **common)
                    # Later entrance and first-scene exit fades are retained.
                    self.assertLess(frame(second, 0).getpixel((45, 30))[0], 10)
                    self.assertGreater(frame(second, .5).getpixel((45, 30))[0], 180)
                    self.assertLess(frame(first, 1.9).getpixel((45, 30))[0], 100)
                    concat = root / "concat.txt"
                    concat.write_text(f"file '{first.as_posix()}'\nfile '{second.as_posix()}'\n")
                    merged, final = root / "merged.mp4", root / "final.mp4"
                    with contextlib.redirect_stdout(io.StringIO()):
                        FFmpegClient.concat_videos(str(concat), str(merged))
                    FFmpegClient.add_background_music(str(merged), str(music), str(final))
                    self.assertLess(level(merged, .1), .001)  # Leading voice silence stays in audio.
                    self.assertGreater(level(merged, .6), .03)
                    self.assertLess(level(merged, 2.5), .001)  # Voice belongs to Scene 1 only.
                    self.assertGreater(level(final, .1), .005)  # Music starts immediately.
                    self.assertGreater(level(final, 2.5), .005)  # Short music track loops.
                    for output in (first, merged, final):
                        reference = frame(output, 1).getpixel((45, 30))
                        for timestamp in (0, .1, .5, 1):
                            pixel = frame(output, timestamp).getpixel((45, 30))
                            self.assertGreater(pixel[0], 180, (output, timestamp, pixel))
                            self.assertLess(max(abs(a-b) for a, b in zip(pixel, reference)), 8)
                        # Captions are scene-local static overlays in this renderer.
                        caption = frame(output, 0).crop((0, 80, 90, 160))
                        # Downsampling antialiases small text; the orange source
                        # has blue < 50, while white lettering raises blue > 100.
                        self.assertGreater(caption.getchannel("B").getextrema()[1], 100)
                    self.assertAlmostEqual(FFmpegClient.audio_duration(str(final)), 4, delta=.1)
                    probe = shutil.which("ffprobe")
                    self.assertIsNotNone(probe)
                    metadata = json.loads(subprocess.run(
                        [probe, "-v", "error", "-show_streams", "-of", "json", str(final)],
                        check=True, capture_output=True, text=True).stdout)
                    stream = next(s for s in metadata["streams"] if s["codec_type"] == "video")
                    self.assertEqual(float(stream["start_time"]), 0)
                    self.assertEqual((stream["codec_name"], stream["pix_fmt"], stream["width"], stream["height"]),
                                     ("h264", "yuv420p", 1080, 1920))
                    self.assertEqual(stream["r_frame_rate"], "30/1")
                    self.assertEqual(next(s for s in metadata["streams"] if s["codec_type"] == "audio")["codec_name"], "aac")
                    if os.environ.get("FIRST_VISUAL_ARTIFACTS"):
                        artifacts = Path(os.environ["FIRST_VISUAL_ARTIFACTS"])
                        artifacts.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(final, artifacts / f"reel-{source.suffix[1:]}.mp4")
                        for timestamp in (0, .1, .5, 1):
                            frame(final, timestamp).save(artifacts / f"{source.suffix[1:]}-{timestamp}s.png")


if __name__ == "__main__":
    unittest.main()

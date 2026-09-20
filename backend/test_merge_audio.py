import array
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

from app.core.ffmpeg_client import FFmpegClient
from PIL import Image


class MergeAudioTests(unittest.TestCase):
    def test_unvoiced_first_scene_keeps_later_narration_and_music(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "image.png"
            Image.new("RGB", (160, 160), "navy").save(source)
            ffmpeg = FFmpegClient.check_ffmpeg()
            voice, music = root / "voice.wav", root / "music.wav"
            for path, frequency in [(voice, 880), (music, 220)]:
                subprocess.run([ffmpeg, "-v", "error", "-f", "lavfi", "-i", f"sine=frequency={frequency}:sample_rate=48000:duration=1.5", str(path)], check=True)
            first, second = root / "silent.mp4", root / "voiced.mp4"
            FFmpegClient.render_media(str(source), str(first), duration=1, width=160, height=160)
            result = FFmpegClient.render_media(str(source), str(second), duration=1, audio_path=str(voice), width=160, height=160)
            self.assertGreaterEqual(result["duration"], 1.5)
            concat = root / "concat.txt"
            concat.write_text(f"file '{first.as_posix()}'\nfile '{second.as_posix()}'\n", encoding="utf-8")
            merged, mixed = root / "merged.mp4", root / "mixed.mp4"
            FFmpegClient.concat_videos(str(concat), str(merged))
            FFmpegClient.add_background_music(str(merged), str(music), str(mixed))

            def samples(path, start):
                process = subprocess.run([ffmpeg, "-v", "error", "-ss", str(start), "-i", str(path), "-t", "0.3", "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True, check=True)
                values = array.array("f")
                values.frombytes(process.stdout)
                self.assertGreater(len(values), 1000)
                return values

            def rms(values):
                return math.sqrt(sum(value * value for value in values) / len(values))

            self.assertLess(rms(samples(merged, .2)), .001)
            self.assertGreater(rms(samples(merged, 1.2)), .03)
            self.assertGreater(rms(samples(mixed, .2)), .005)
            self.assertGreater(rms(samples(mixed, 1.2)), .03)


if __name__ == "__main__":
    unittest.main()

import array
import math
from pathlib import Path
import subprocess
import tempfile
import unittest

from app.core.ffmpeg_client import FFmpegClient


class AudioMixTests(unittest.TestCase):
    def test_music_volume_and_loop_preserve_video_duration(self):
        ffmpeg = FFmpegClient.check_ffmpeg()
        def command(*args):
            return subprocess.run([ffmpeg, "-v", "error", "-y", *map(str, args)], check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            music, video = folder / "music.wav", folder / "video.mp4"
            command("-f", "lavfi", "-i", "sine=frequency=440:duration=0.4", music)
            command("-f", "lavfi", "-i", "color=c=black:s=160x90:d=1.2", "-c:v", "libx264", video)
            levels = []
            for volume in (0, .2, .6):
                output = folder / f"mixed-{volume}.mp4"
                FFmpegClient.add_background_music(str(video), str(music), str(output), volume=volume)
                self.assertTrue(FFmpegClient.is_media_readable(str(output)))
                self.assertAlmostEqual(FFmpegClient.audio_duration(str(output)), 1.2, delta=.15)
                raw = command("-i", output, "-map", "0:a:0", "-f", "f32le", "-ac", "1", "-").stdout
                samples = array.array("f", raw)
                levels.append(math.sqrt(sum(x*x for x in samples) / len(samples)))
            self.assertLess(levels[0], .00001)
            self.assertGreater(levels[1], .001)
            self.assertGreater(levels[2], levels[1] * 2.5)

    def test_narration_survives_when_music_is_muted(self):
        ffmpeg = FFmpegClient.check_ffmpeg()
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            video, music, output = folder / "voice.mp4", folder / "music.wav", folder / "out.mp4"
            subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=160x90:d=1", "-f", "lavfi", "-i", "sine=frequency=880:duration=1", "-c:v", "libx264", "-c:a", "aac", "-shortest", str(video)], check=True)
            subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.3", str(music)], check=True)
            FFmpegClient.add_background_music(str(video), str(music), str(output), volume=0)
            raw = subprocess.run([ffmpeg, "-v", "error", "-i", str(output), "-f", "f32le", "-ac", "1", "-"], check=True, capture_output=True).stdout
            samples = array.array("f", raw)
            self.assertGreater(math.sqrt(sum(x*x for x in samples) / len(samples)), .05)


if __name__ == "__main__":
    unittest.main()

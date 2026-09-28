"""Decode every merged scene; container duration alone can hide lost video."""
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

from app.core.ffmpeg_client import FFmpegClient


class MergePlaybackTests(unittest.TestCase):
    def test_color_metadata_changes_preserve_every_scene(self):
        ffmpeg = FFmpegClient.check_ffmpeg()

        def run(*args):
            return subprocess.run([ffmpeg, "-v", "error", "-y", *map(str, args)],
                                  check=True, capture_output=True).stdout

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            clips = []
            for index, (color, space) in enumerate([
                ("red", "bt709"), ("green", "smpte170m"),
                ("blue", "bt709"), ("red", "smpte170m"),
            ]):
                clip = root / f"scene-{index}.mp4"
                run("-f", "lavfi", "-i", f"color={color}:s=160x160:r=30:d=1",
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-colorspace", space, "-color_primaries", space,
                    "-color_trc", space, "-c:a", "aac", clip)
                clips.append(clip)
            concat = root / "concat.txt"
            concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips))
            merged = root / "merged.mp4"
            with contextlib.redirect_stdout(io.StringIO()):
                FFmpegClient.concat_videos(str(concat), str(merged))
            raw = run("-i", merged, "-map", "0:v:0", "-vf", "scale=1:1",
                      "-pix_fmt", "rgb24", "-f", "rawvideo", "-")
            frames = [raw[i:i + 3] for i in range(0, len(raw), 3)]
            self.assertAlmostEqual(len(frames), 120, delta=2)
            # The middle of each scene must contain that scene's visual.
            for frame_index, channel in [(15, 0), (45, 1), (75, 2), (105, 0)]:
                pixel = frames[frame_index]
                self.assertGreater(pixel[channel], 80)
                self.assertEqual(max(range(3), key=lambda i: pixel[i]), channel)


if __name__ == "__main__":
    unittest.main()

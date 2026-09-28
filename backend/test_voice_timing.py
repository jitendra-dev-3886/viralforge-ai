import array
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.core.ffmpeg_client import FFmpegClient


class VoiceTimingTests(unittest.TestCase):
    def test_narration_controls_scene_boundaries_after_merge(self):
        ffmpeg = FFmpegClient.check_ffmpeg()

        def run(*args):
            return subprocess.run([ffmpeg, "-v", "error", "-y", *map(str, args)],
                                  capture_output=True, check=True).stdout

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            clips = []
            durations = []
            for index, (color, frequency, speech, planned) in enumerate([
                ("red", 440, 1.2, 8), ("blue", 880, 2.2, 1),
            ]):
                source = root / f"source{index}.png"
                Image.new("RGB", (160, 160), color).save(source)
                audio = root / f"voice{index}.wav"
                run("-f", "lavfi", "-i",
                    f"sine=frequency={frequency}:sample_rate=48000:duration={speech}", audio)
                clip = root / f"scene{index}.mp4"
                result = FFmpegClient.render_media(
                    str(source), str(clip), duration=planned, audio_path=str(audio),
                    width=160, height=160, transition="none", overlay_text=f"Scene {index + 1}")
                self.assertAlmostEqual(result["duration"], speech + .2, delta=1 / 30)
                clips.append(clip)
                durations.append(result["duration"])
            manifest = root / "concat.txt"
            manifest.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips))
            merged = root / "merged.mp4"
            with contextlib.redirect_stdout(io.StringIO()):
                FFmpegClient.concat_videos(str(manifest), str(merged))
            self.assertAlmostEqual(FFmpegClient.audio_duration(str(merged)), sum(durations), delta=.1)

            # Sample both sides of the join: each scene's visual and tone must
            # change together, with no silent hold from the original 8s plan.
            for timestamp, channel, frequency in [(.5, 0, 440), (durations[0] + .4, 2, 880)]:
                pixel = run("-ss", timestamp, "-i", merged, "-frames:v", "1",
                            "-vf", "crop=80:40:0:0,scale=1:1", "-pix_fmt", "rgb24", "-f", "rawvideo", "-")
                self.assertEqual(max(range(3), key=lambda i: pixel[i]), channel)
                samples = array.array("f")
                samples.frombytes(run("-ss", timestamp, "-i", merged, "-t", "0.2",
                                      "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"))
                self.assertGreater(max(samples), .03)
                crossings = sum(a <= 0 < b for a, b in zip(samples, samples[1:]))
                self.assertAlmostEqual(crossings / (len(samples) / 48000), frequency, delta=15)


if __name__ == "__main__":
    unittest.main()

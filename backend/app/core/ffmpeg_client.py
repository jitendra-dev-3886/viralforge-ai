import os
import shutil
import subprocess


class FFmpegClient:

    @staticmethod
    def check_ffmpeg():

        ffmpeg_path = shutil.which("ffmpeg")

        if not ffmpeg_path:
            raise Exception(
                "FFmpeg is not installed or not added to PATH."
            )

        return ffmpeg_path

    @staticmethod
    def merge_video_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
    ):

        FFmpegClient.check_ffmpeg()

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )

        ext = os.path.splitext(video_path)[1].lower()

        image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]

        if ext in image_extensions:

            command = [

                "ffmpeg",

                "-y",

                "-loop", "1",

                "-i", video_path,

                "-i", audio_path,

                "-vf", "scale=1080:1920",

                "-c:v", "libx264",

                "-pix_fmt", "yuv420p",

                "-c:a", "aac",

                "-shortest",

                output_path,
            ]

        else:

            command = [

                "ffmpeg",

                "-y",

                "-i", video_path,

                "-i", audio_path,

                "-map", "0:v:0",

                "-map", "1:a:0",

                "-c:v", "libx264",

                "-preset", "fast",

                "-crf", "23",

                "-c:a", "aac",

                "-b:a", "192k",

                "-ar", "48000",

                "-ac", "2",

                "-shortest",

                output_path,
            ]

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        print("=" * 80)
        print(process.stdout)
        print(process.stderr)
        print("=" * 80)

        if process.returncode != 0:
            raise Exception(process.stderr)

        return {
            "success": True,
            "output": output_path,
        }
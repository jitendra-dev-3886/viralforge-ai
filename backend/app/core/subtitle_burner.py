import os
import shutil
import subprocess


class SubtitleBurner:

    @staticmethod
    def check_ffmpeg():

        ffmpeg_path = shutil.which("ffmpeg")

        if not ffmpeg_path:
            raise Exception(
                "FFmpeg is not installed or not found in PATH."
            )

        return ffmpeg_path

    @staticmethod
    def burn(
        video_path: str,
        subtitle_path: str,
        output_path: str,
    ):

        SubtitleBurner.check_ffmpeg()

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )

        # Windows path fix
        subtitle = (
            subtitle_path
            .replace("\\", "/")
            .replace(":", "\\:")
        )

        subtitle_filter = (
            f"subtitles='{subtitle}':"
            "force_style="
            "'FontName=Arial,"
            "FontSize=22,"
            "PrimaryColour=&HFFFFFF&,"
            "OutlineColour=&H000000&,"
            "Outline=2,"
            "Shadow=1,"
            "Alignment=2,"
            "MarginV=35'"
        )

        command = [

            "ffmpeg",

            "-y",

            "-i",
            video_path,

            "-vf",
            subtitle_filter,

            "-c:v",
            "libx264",

            "-preset",
            "fast",

            "-crf",
            "23",

            "-c:a",
            "copy",

            output_path,

        ]

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        print(process.stdout)
        print(process.stderr)

        if process.returncode != 0:
            raise Exception(process.stderr)

        return {

            "success": True,

            "output": output_path,

        }
import os
import shutil
import subprocess


class FFmpegClient:

    # ==========================================================
    # Check FFmpeg
    # ==========================================================

    @staticmethod
    def check_ffmpeg():

        ffmpeg_path = shutil.which("ffmpeg")

        if not ffmpeg_path:
            raise RuntimeError(
                "FFmpeg is not installed or not available in PATH."
            )

        return ffmpeg_path

    # ==========================================================
    # Merge Video/Image + Audio
    # ==========================================================

    @staticmethod
    def merge_video_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
    ):

        ffmpeg = FFmpegClient.check_ffmpeg()

        if not os.path.isfile(video_path):
            raise FileNotFoundError(
                f"Video/Image file not found: {video_path}"
            )

        if not os.path.isfile(audio_path):
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        output_dir = os.path.dirname(
            os.path.abspath(output_path)
        )

        os.makedirs(
            output_dir,
            exist_ok=True,
        )

        extension = os.path.splitext(
            video_path
        )[1].lower()

        image_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        )

        # ======================================================
        # IMAGE + AUDIO
        # ======================================================

        if extension in image_extensions:

            command = [
                ffmpeg,

                "-y",

                "-loop",
                "1",

                "-i",
                os.path.abspath(video_path),

                "-i",
                os.path.abspath(audio_path),

                "-vf",
                (
                    "scale=1080:1920:"
                    "force_original_aspect_ratio=increase,"
                    "crop=1080:1920"
                ),

                "-c:v",
                "libx264",

                "-preset",
                "fast",

                "-crf",
                "23",

                "-pix_fmt",
                "yuv420p",

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-ac",
                "2",

                "-shortest",

                os.path.abspath(output_path),
            ]

        # ======================================================
        # VIDEO + AUDIO
        # ======================================================

        else:

            command = [
                ffmpeg,

                "-y",

                "-i",
                os.path.abspath(video_path),

                "-i",
                os.path.abspath(audio_path),

                "-map",
                "0:v:0",

                "-map",
                "1:a:0",

                "-c:v",
                "libx264",

                "-preset",
                "fast",

                "-crf",
                "23",

                "-pix_fmt",
                "yuv420p",

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-ac",
                "2",

                "-shortest",

                os.path.abspath(output_path),
            ]

        # ======================================================
        # Execute
        # ======================================================

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:

            raise RuntimeError(
                "FFmpeg merge failed:\n"
                + process.stderr
            )

        if not os.path.isfile(output_path):

            raise RuntimeError(
                "FFmpeg completed but output file "
                "was not created."
            )

        if os.path.getsize(output_path) <= 0:

            raise RuntimeError(
                "FFmpeg created an empty output file."
            )

        return {
            "success": True,
            "output": output_path,
        }

    # ==========================================================
    # Concatenate Rendered Scene Videos
    # ==========================================================

    @staticmethod
    def concat_videos(
        concat_file: str,
        output_path: str,
    ):

        ffmpeg = FFmpegClient.check_ffmpeg()

        concat_file = os.path.abspath(
            concat_file
        )

        output_path = os.path.abspath(
            output_path
        )

        if not os.path.isfile(concat_file):

            raise FileNotFoundError(
                f"Concat file not found: {concat_file}"
            )

        output_dir = os.path.dirname(
            output_path
        )

        os.makedirs(
            output_dir,
            exist_ok=True,
        )

        # ======================================================
        # FFmpeg Concat
        # ======================================================

        command = [
            ffmpeg,

            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            concat_file,

            "-c",
            "copy",

            output_path,
        ]

        # ======================================================
        # Execute
        # ======================================================

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:

            raise RuntimeError(
                "FFmpeg concat failed:\n"
                + process.stderr
            )

        # ======================================================
        # Validate
        # ======================================================

        if not os.path.isfile(output_path):

            raise RuntimeError(
                "FFmpeg completed but final video "
                "was not created."
            )

        if os.path.getsize(output_path) <= 0:

            raise RuntimeError(
                "Final video is empty."
            )

        return {
            "success": True,
            "output": output_path,
        }
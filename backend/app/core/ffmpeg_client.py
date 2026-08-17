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

            raise Exception(
                "FFmpeg is not installed or not added to PATH."
            )

        return ffmpeg_path

    # ==========================================================
    # Merge Video + Audio
    # ==========================================================

    @staticmethod
    def merge_video_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
    ):

        FFmpegClient.check_ffmpeg()

        output_dir = os.path.dirname(output_path)

        if output_dir:

            os.makedirs(
                output_dir,
                exist_ok=True,
            )

        # ======================================================
        # Detect Image
        # ======================================================

        ext = os.path.splitext(
            video_path
        )[1].lower()

        image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]

        # ======================================================
        # Image + Audio
        # ======================================================

        if ext in image_extensions:

            command = [

                "ffmpeg",

                "-y",

                "-loop",
                "1",

                "-i",
                video_path,

                "-i",
                audio_path,

                "-vf",
                "scale=1080:1920",

                "-c:v",
                "libx264",

                "-pix_fmt",
                "yuv420p",

                "-c:a",
                "aac",

                "-shortest",

                output_path,
            ]

        # ======================================================
        # Video + Audio
        # ======================================================

        else:

            command = [

                "ffmpeg",

                "-y",

                "-i",
                video_path,

                "-i",
                audio_path,

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

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-ar",
                "48000",

                "-ac",
                "2",

                "-shortest",

                output_path,
            ]

        # ======================================================
        # Execute FFmpeg
        # ======================================================

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,
        )

        print("=" * 80)
        print(process.stdout)
        print(process.stderr)
        print("=" * 80)

        # ======================================================
        # Error
        # ======================================================

        if process.returncode != 0:

            raise Exception(
                process.stderr
            )

        # ======================================================
        # Validate Output
        # ======================================================

        if not os.path.exists(output_path):

            raise Exception(
                "FFmpeg completed but output file was not created."
            )

        return {

            "success": True,

            "output": output_path,

        }

    # ==========================================================
    # Concatenate Videos
    # ==========================================================

    @staticmethod
    def concat_videos(
        concat_file: str,
        output_path: str,
    ):

        FFmpegClient.check_ffmpeg()

        output_dir = os.path.dirname(output_path)

        if output_dir:

            os.makedirs(
                output_dir,
                exist_ok=True,
            )

        # ======================================================
        # Validate Concat File
        # ======================================================

        if not os.path.exists(concat_file):

            raise Exception(
                "FFmpeg concat file not found."
            )

        # ======================================================
        # FFmpeg Command
        # ======================================================

        command = [

            "ffmpeg",

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
        # Execute FFmpeg
        # ======================================================

        process = subprocess.run(

            command,

            capture_output=True,

            text=True,
        )

        print("=" * 80)
        print(process.stdout)
        print(process.stderr)
        print("=" * 80)

        # ======================================================
        # Error
        # ======================================================

        if process.returncode != 0:

            raise Exception(
                process.stderr
            )

        # ======================================================
        # Validate Output
        # ======================================================

        if not os.path.exists(output_path):

            raise Exception(
                "FFmpeg completed but final video was not created."
            )

        return {

            "success": True,

            "output": output_path,

        }
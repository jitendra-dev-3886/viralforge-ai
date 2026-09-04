import os
import shutil
import subprocess
from pathlib import Path


class FFmpegClient:

    @staticmethod
    def is_media_readable(path: str) -> bool:
        """Return True only when FFmpeg can decode the first video frame."""
        if not os.path.exists(path) or os.path.getsize(path) <= 0:
            return False
        try:
            process = subprocess.run(
                [
                    FFmpegClient.check_ffmpeg(), "-v", "error", "-i", path,
                    "-map", "0:v:0", "-frames:v", "1", "-f", "null", "-",
                ],
                capture_output=True,
                timeout=30,
            )
            return process.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    @staticmethod
    def add_background_music(video_path: str, music_path: str, output_path: str):
        """Mix looping background music under narration, or add it to silent video."""
        ffmpeg = FFmpegClient.check_ffmpeg()
        ffprobe = shutil.which("ffprobe")
        has_audio = False
        if ffprobe:
            probe = subprocess.run(
                [ffprobe, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", video_path],
                capture_output=True, text=True,
            )
            has_audio = bool(probe.stdout.strip())
        else:
            probe = subprocess.run([ffmpeg, "-i", video_path], capture_output=True, text=True)
            has_audio = "Audio:" in probe.stderr
        command = [ffmpeg, "-y", "-i", video_path, "-stream_loop", "-1", "-i", music_path]
        if has_audio:
            command += [
                "-filter_complex", "[1:a]volume=0.18[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]",
                "-map", "0:v:0", "-map", "[a]",
            ]
        else:
            command += ["-filter:a", "volume=0.18", "-map", "0:v:0", "-map", "1:a:0", "-shortest"]
        command += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output_path]
        process = subprocess.run(command, capture_output=True, text=True)
        if process.returncode != 0:
            raise Exception(process.stderr)
        if not os.path.exists(output_path) or os.path.getsize(output_path) <= 0:
            raise Exception("Background music output was not created.")
        return {"success": True, "output": output_path}

    @staticmethod
    def render_media(video_path: str, output_path: str, duration: int = 5, audio_path: str | None = None, width: int = 1080, height: int = 1920, overlay_text: str = "", username: str = "", logo_path: str | None = None, text_x_pct: float = 50, text_y_pct: float = 68, logo_x_pct: float = 10, logo_y_pct: float = 8, username_x_pct: float = 82, username_y_pct: float = 92, transition: str = "fade"):
        """Normalize an image/video scene to MP4, with optional narration."""
        ffmpeg = FFmpegClient.check_ffmpeg()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output = Path(output_path)
        temporary_output = output.with_name(f"{output.stem}.rendering{output.suffix}")
        temporary_output.unlink(missing_ok=True)
        is_image = os.path.splitext(video_path)[1].lower() in {".jpg", ".jpeg", ".png", ".webp"}
        command = [ffmpeg, "-y"]
        if is_image:
            command += ["-loop", "1", "-framerate", "30", "-i", video_path]
        else:
            command += ["-stream_loop", "-1", "-i", video_path]
        if audio_path:
            command += ["-i", audio_path]
        logo_index = 2 if audio_path else 1
        if logo_path:
            command += ["-i", logo_path]
        # Passing user text directly in a drawtext expression breaks on common
        # punctuation (especially apostrophes) and can also be interpreted as
        # filter syntax. Text files keep captions Unicode-safe and literal.
        overlay_text_path = Path(f"{output_path}.overlay.txt")
        username_text_path = Path(f"{output_path}.username.txt")
        overlay_text_path.write_text(str(overlay_text or ""), encoding="utf-8")
        username_text_path.write_text(str(username or ""), encoding="utf-8")
        def filter_path(value):
            return str(Path(value).resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        def position(value, default):
            try:
                return max(3.0, min(97.0, float(value))) / 100
            except (TypeError, ValueError):
                return default / 100
        text_x, text_y = position(text_x_pct, 50), position(text_y_pct, 68)
        logo_x, logo_y = position(logo_x_pct, 10), position(logo_y_pct, 8)
        username_x, username_y = position(username_x_pct, 82), position(username_y_pct, 92)
        font_candidates = [
            Path("C:/Windows/Fonts/NirmalaB.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]
        font_path = next((item for item in font_candidates if item.exists()), None)
        font_option = f"fontfile='{filter_path(font_path)}':" if font_path else ""
        fade_filter = f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(0.3, duration - 0.35)}:d=0.35," if transition == "fade" else ""
        base_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps=30,"
            "eq=contrast=1.035:saturation=1.08,"
            f"{fade_filter}"
            f"drawbox=x=0:y=ih*0.56:w=iw:h=ih*0.44:color=black@0.48:t=fill,"
            f"drawtext={font_option}textfile='{filter_path(overlay_text_path)}':fontcolor=white:fontsize={max(30, int(width * .047))}:"
            f"line_spacing=12:borderw=3:bordercolor=black@0.7:x=w*{text_x}-text_w/2:y=h*{text_y}-text_h/2,"
            f"drawtext={font_option}textfile='{filter_path(username_text_path)}':fontcolor=white:fontsize={max(20, int(width * .024))}:"
            f"box=1:boxcolor=black@0.55:boxborderw=12:x=w*{username_x}-text_w/2:y=h*{username_y}-text_h/2"
        )
        if logo_path:
            filter_arg = f"[0:v]{base_filter}[base];[{logo_index}:v]scale={max(70, int(width*.10))}:-1[logo];[base][logo]overlay=W*{logo_x}-w/2:H*{logo_y}-h/2[v]"
        else:
            filter_arg = f"[0:v]{base_filter}[v]"
        command += [
            "-filter_complex", filter_arg, "-map", "[v]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
        ]
        if audio_path:
            command += ["-map", "1:a:0", "-c:a", "aac", "-b:a", "192k", "-shortest"]
        else:
            command += ["-an", "-t", str(max(1, duration))]
        command += ["-movflags", "+faststart", str(temporary_output)]
        try:
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode != 0:
                raise Exception(process.stderr)
            if not FFmpegClient.is_media_readable(str(temporary_output)):
                raise Exception("FFmpeg created an unreadable scene video.")
            os.replace(temporary_output, output)
        finally:
            overlay_text_path.unlink(missing_ok=True)
            username_text_path.unlink(missing_ok=True)
            temporary_output.unlink(missing_ok=True)
        if not output.exists() or output.stat().st_size <= 0:
            raise Exception("FFmpeg completed but the scene output was not created.")
        return {"success": True, "output": output_path}

    # ==========================================================
    # Check FFmpeg
    # ==========================================================

    @staticmethod
    def check_ffmpeg():

        ffmpeg_path = shutil.which("ffmpeg")

        if not ffmpeg_path:
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            except (ImportError, RuntimeError, OSError):
                ffmpeg_path = None

        if not ffmpeg_path:

            raise Exception(
                "FFmpeg is unavailable. Install backend requirements to add the bundled encoder."
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

                FFmpegClient.check_ffmpeg(),

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

                FFmpegClient.check_ffmpeg(),

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

            FFmpegClient.check_ffmpeg(),

            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            concat_file,

            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",

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

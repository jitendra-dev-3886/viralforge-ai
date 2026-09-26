import os
import shutil
import subprocess
import re
from pathlib import Path

from app.core.text_overlay import render_caption, render_logo
from app.core.platform_branding import render_platform_username
from app.core.visual_style import get_style, render_style_frame, default_layout


class FFmpegClient:

    @staticmethod
    def audio_duration(path: str) -> float:
        probe = subprocess.run([FFmpegClient.check_ffmpeg(), "-hide_banner", "-i", path], capture_output=True, text=True)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", probe.stderr)
        if not match or "Audio:" not in probe.stderr:
            raise ValueError("The selected voice recording is unreadable. Generate the voice again before merging.")
        hours, minutes, seconds = map(float, match.groups())
        return hours * 3600 + minutes * 60 + seconds

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
    def add_background_music(video_path: str, music_path: str, output_path: str, volume: float = 0.18):
        """Mix looping background music under narration, or add it to silent video."""
        volume = max(0.0, min(1.0, float(volume)))
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
                "-filter_complex", f"[1:a]volume={volume}[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,alimiter=limit=0.95:level=0[a]",
                "-map", "0:v:0", "-map", "[a]",
            ]
        else:
            command += ["-filter:a", f"volume={volume}", "-map", "0:v:0", "-map", "1:a:0", "-shortest"]
        command += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output_path]
        process = subprocess.run(command, capture_output=True, text=True)
        if process.returncode != 0:
            raise Exception(process.stderr)
        if not os.path.exists(output_path) or os.path.getsize(output_path) <= 0:
            raise Exception("Background music output was not created.")
        return {"success": True, "output": output_path}

    @staticmethod
    def render_media(video_path: str, output_path: str, duration: int = 5, audio_path: str | None = None, width: int = 1080, height: int = 1920, overlay_text: str = "", username: str = "", logo_path: str | None = None, text_x_pct: float | None = None, text_y_pct: float | None = None, logo_x_pct: float | None = None, logo_y_pct: float | None = None, username_x_pct: float | None = None, username_y_pct: float | None = None, transition: str = "fade", visual_style: str | None = None, as_image: bool = False, overlay_opacity: dict | None = None, platform: str | None = None, entrance_transition: bool = False):
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
            duration = max(float(duration), FFmpegClient.audio_duration(audio_path))
        else:
            command += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        logo_index = 2
        preset = get_style(visual_style)
        if preset and preset["logo"].get("visible") is False:
            logo_path = None
        if preset and preset["username"].get("visible") is False:
            username = ""
        overlay_opacity = overlay_opacity or {}
        styled_logo_path = Path(f"{output_path}.logo.png")
        if logo_path:
            command += ["-i", str(styled_logo_path) if preset else logo_path]
        overlay_text_path = Path(f"{output_path}.overlay.png")
        username_text_path = Path(f"{output_path}.username.png")
        frame_path = Path(f"{output_path}.frame.png")
        try:
            render_caption(overlay_text, overlay_text_path, width, height, visual_style=visual_style, opacity=overlay_opacity.get("text"))
            render_platform_username(username, username_text_path, width, height, platform=platform, visual_style=visual_style, opacity=overlay_opacity.get("username"))
            render_style_frame(visual_style, frame_path, width, height)
            if logo_path and preset:
                render_logo(logo_path, styled_logo_path, width, visual_style, height=height, opacity=overlay_opacity.get("logo"))
        except Exception:
            overlay_text_path.unlink(missing_ok=True)
            username_text_path.unlink(missing_ok=True)
            frame_path.unlink(missing_ok=True)
            styled_logo_path.unlink(missing_ok=True)
            raise
        text_index = logo_index + (1 if logo_path else 0)
        username_index = text_index + 1
        command += ["-i", str(overlay_text_path), "-i", str(username_text_path), "-i", str(frame_path)]
        def position(value, default):
            try:
                return max(3.0, min(97.0, float(value))) / 100
            except (TypeError, ValueError):
                return default / 100
        defaults = default_layout(visual_style)
        text_x, text_y = position(text_x_pct, defaults["text"]["x"]), position(text_y_pct, defaults["text"]["y"])
        logo_x, logo_y = position(logo_x_pct, defaults["logo"]["x"]), position(logo_y_pct, defaults["logo"]["y"])
        username_x, username_y = position(username_x_pct, defaults["username"]["x"]), position(username_y_pct, defaults["username"]["y"])
        # Standalone/first scenes start fully visible; only later scenes enter.
        fade_filter = ""
        if transition == "fade" and not as_image:
            if entrance_transition:
                fade_filter += "fade=t=in:st=0:d=0.25,"
            fade_filter += f"fade=t=out:st={max(0.3, duration - 0.35)}:d=0.35,"
        media_x, media_y, media_w, media_h = preset["mediaRect"] if preset else (0, 0, 1, 1)
        fit_width, fit_height = max(2, round(width * media_w / 2) * 2), max(2, round(height * media_h / 2) * 2)
        offset_x, offset_y = round(width * media_x / 2) * 2, round(height * media_y / 2) * 2
        background = preset["background"] if preset else "black"
        focus_y = preset.get("mediaFocusY", .5) if preset else .5
        base_filter = (
            f"setpts=PTS-STARTPTS,scale={fit_width}:{fit_height}:force_original_aspect_ratio=increase,crop={fit_width}:{fit_height}:(iw-ow)/2:(ih-oh)*{focus_y},"
            f"pad={width}:{height}:{offset_x}:{offset_y}:color={background},fps=30,"
            "eq=contrast=1.035:saturation=1.08,"
            f"{fade_filter}"
            + ("null" if get_style(visual_style) else "drawbox=x=0:y=ih*0.56:w=iw:h=ih*0.44:color=black@0.48:t=fill")
        )
        margin = max(4, int(width * .03))
        def caption_position(x, y):
            return f"x='max({margin},min(W-w-{margin},W*{x}-w/2))':y='max({margin},min(H-h-{margin},H*{y}-h/2))'"
        filter_arg = (
            f"[0:v]{base_filter}[source];"
            f"[source][{username_index + 1}:v]overlay=0:0[base];"
            f"[base][{text_index}:v]overlay={caption_position(text_x, text_y)}[captioned];"
            f"[captioned][{username_index}:v]overlay={caption_position(username_x, username_y)}[branded]"
        )
        if logo_path:
            logo_filter = "null" if preset else f"scale={max(70, int(width*.10))}:-1"
            filter_arg += f";[{logo_index}:v]{logo_filter}[logo];[branded][logo]overlay={caption_position(logo_x, logo_y)}[v]"
        else:
            filter_arg += ";[branded]null[v]"
        command += [
            "-filter_complex", filter_arg, "-map", "[v]",
        ]
        # Every clip needs the same audio stream layout for safe concatenation.
        # Pad short narration and extend the scene when narration is longer.
        if as_image:
            command += ["-frames:v", "1", "-c:v", "png", "-update", "1"]
        else:
            command += ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
                        "-map", "1:a:0", "-af", "apad", "-ar", "48000", "-ac", "2",
                        "-c:a", "aac", "-b:a", "192k", "-t", str(max(1, duration)), "-movflags", "+faststart"]
        command += [str(temporary_output)]
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
            frame_path.unlink(missing_ok=True)
            styled_logo_path.unlink(missing_ok=True)
            temporary_output.unlink(missing_ok=True)
        if not output.exists() or output.stat().st_size <= 0:
            raise Exception("FFmpeg completed but the scene output was not created.")
        return {"success": True, "output": output_path, "duration": max(1, duration)}

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

            # AAC priming in the concat input can offset the first video PTS.
            # Anchor visuals independently; keep narration/music timing intact.
            "-vf", "setpts=PTS-STARTPTS",
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

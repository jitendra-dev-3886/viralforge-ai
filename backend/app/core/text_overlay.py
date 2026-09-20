"""Shape and fit Unicode captions before compositing them into video."""
import os
import math
import re
import unicodedata
from pathlib import Path

# Pillow's Windows wheel loads FriBiDi at runtime. Reuse a configured install
# or the standard Tesseract installation without copying system DLLs.
_fribidi_dll = None
_dll_directory = None
if os.name == "nt":
    import ctypes
    candidates = [
        os.environ.get("FRIBIDI_DLL_PATH", ""),
        str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Tesseract-OCR" / "libfribidi-0.dll"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            try:
                _dll_directory = os.add_dll_directory(str(Path(candidate).resolve().parent))
                _fribidi_dll = ctypes.WinDLL(str(Path(candidate).resolve()))
                break
            except OSError:
                if _dll_directory:
                    _dll_directory.close()

from PIL import Image, ImageDraw, ImageFont, features


def caption_font(text):
    hindi = bool(re.search(r"[\u0900-\u097f]", text))
    candidates = [
        os.environ.get("OVERLAY_FONT_PATH", ""),
        "C:/Windows/Fonts/NirmalaB.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    ]
    if not hindi:
        candidates += ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("Install a Devanagari font (Nirmala UI or Noto Sans Devanagari), or set OVERLAY_FONT_PATH to a compatible font file.")


def wrap_words(text, font, max_width):
    """Never split a word: Hindi marks and conjuncts stay with their base letters."""
    lines = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            if line and font.getlength(candidate) > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return "\n".join(lines)


def render_caption(text, output_path, width, height, size_ratio=.047):
    text = unicodedata.normalize("NFC", str(text or "")).strip()
    if not text:
        Image.new("RGBA", (1, 1)).save(output_path)
        return
    if not features.check_feature("raqm"):
        raise RuntimeError("Overlays require Pillow with libraqm and FriBiDi text shaping. On Windows install FriBiDi and set FRIBIDI_DLL_PATH to libfribidi-0.dll, then restart the backend.")
    font_path = caption_font(text)
    padding = max(6, round(width * .014))
    max_width = max(1, int(width * .84) - padding * 2)
    max_height = max(1, int(height * .42) - padding * 2)
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    # Measure shaped glyphs, not code points; retain all words and explicit lines.
    for size in range(max(12, round(width * size_ratio)), 7, -1):
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        wrapped = wrap_words(text, font, max_width)
        spacing = max(4, round(size * .32))
        stroke = max(1, round(size * .035))
        options = dict(font=font, spacing=spacing, align="center", stroke_width=stroke)
        box = draw.multiline_textbbox((0, 0), wrapped, **options)
        if box[2] - box[0] <= max_width and box[3] - box[1] <= max_height:
            break
    else:
        raise ValueError("Overlay text is too long to fit legibly. Shorten the scene text or split it across more scenes.")
    image = Image.new("RGBA", (math.ceil(box[2] - box[0]) + padding * 2, math.ceil(box[3] - box[1]) + padding * 2))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=padding, fill=(0, 0, 0, 125))
    draw.multiline_text((padding - box[0], padding - box[1]), wrapped, fill="white", stroke_fill=(0, 0, 0, 180), **options)
    image.save(output_path)

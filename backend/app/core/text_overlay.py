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
from app.core.visual_style import get_style


def caption_font(text, family="sans"):
    hindi = bool(re.search(r"[\u0900-\u097f]", text))
    candidates = [
        os.environ.get("OVERLAY_FONT_PATH", ""),
        "C:/Windows/Fonts/NirmalaB.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    ]
    if not hindi:
        families = {
            "serif": ["C:/Windows/Fonts/georgia.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
            "mono": ["C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"],
            "condensed": ["C:/Windows/Fonts/impact.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"],
            "rounded": ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
            "sans": ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
        }
        candidates[1:1] = families.get(family, families["sans"])
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


def render_caption(text, output_path, width, height, size_ratio=.047, visual_style=None, role="text", opacity=None):
    style = get_style(visual_style)
    text = unicodedata.normalize("NFC", str(text or "")).strip()
    if not text:
        Image.new("RGBA", (1, 1)).save(output_path)
        return
    if not features.check_feature("raqm"):
        raise RuntimeError("Overlays require Pillow with libraqm and FriBiDi text shaping. On Windows install FriBiDi and set FRIBIDI_DLL_PATH to libfribidi-0.dll, then restart the backend.")
    if style:
        return render_design_caption(text, output_path, width, height, style, role, opacity)
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
        stroke = 0 if style else max(1, round(size * .035))
        options = dict(font=font, spacing=spacing, align="center", stroke_width=stroke)
        box = draw.multiline_textbbox((0, 0), wrapped, **options)
        if box[2] - box[0] <= max_width and box[3] - box[1] <= max_height:
            break
    else:
        raise ValueError("Overlay text is too long to fit legibly. Shorten the scene text or split it across more scenes.")
    image = Image.new("RGBA", (math.ceil(box[2] - box[0]) + padding * 2, math.ceil(box[3] - box[1]) + padding * 2))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=round(width * style["radius"]) if style else padding, fill=style["panel"] if style else (0, 0, 0, 125))
    draw.multiline_text((padding - box[0], padding - box[1]), wrapped, fill=style["ink"] if style else "white", stroke_fill=(0, 0, 0, 180), **options)
    image.save(output_path)


def render_design_caption(text, output_path, width, height, style, role, opacity=None):
    """Fit shaped text within the preset's own composition, keeping every word."""
    spec = style[role]
    if spec.get("uppercase"):
        text = text.upper()
    font_path = caption_font(text, spec["font"])
    pad = max(3, round(min(width * .022, height * (.018 if role == "username" else .04))))
    canvas_width = max(30, round(width * spec["width"]))
    max_height = round(height * (.34 if role == "text" else .12))
    mode = spec["mode"]
    extra = pad * 2 if mode in ("paper", "bubble", "cinema", "byline") else pad
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(max(12, round(width * spec["size"])), 7, -1):
        font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        wrapped = wrap_words(text, font, canvas_width - pad * 2)
        spacing = max(4, round(size * (spec.get("lineHeight", 1.4 if mode == "paper" else 1.28) - 1)))
        options = dict(font=font, spacing=spacing, align=spec["align"], stroke_width=max(1, round(width * .0015)))
        box = draw.multiline_textbbox((0, 0), wrapped, **options)
        measured_height = box[3] - box[1]
        if mode == "strips":
            measured_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + pad + max(2, pad // 3) for line in wrapped.splitlines())
        if box[2] - box[0] <= canvas_width - pad * 2 and measured_height + pad + extra <= max_height:
            break
    else:
        raise ValueError("Overlay text is too long for this design. Shorten the text or split it across more scenes.")

    canvas_height = math.ceil(measured_height) + pad + extra
    if mode in ("caption", "strips"):
        canvas_width = min(canvas_width, math.ceil(box[2] - box[0]) + pad * 2)
    image = Image.new("RGBA", (canvas_width, canvas_height))
    draw = ImageDraw.Draw(image)
    bounds = (0, 0, canvas_width - 1, canvas_height - 1)
    top = pad
    bottom = canvas_height - 1
    if mode == "strips":
        y = 0
        lines = wrapped.splitlines()
        for index, line in enumerate(lines):
            b = draw.textbbox((0, 0), line, font=font)
            line_width, line_height = b[2] - b[0], b[3] - b[1]
            x = pad if spec["align"] == "left" else (canvas_width - line_width) / 2
            draw.rectangle((x - pad, y, x + line_width + pad - 1, y + line_height + pad - 1), fill=spec["background"])
            draw.line((x - pad, y + line_height + pad - 1, x + line_width + pad - 1, y + line_height + pad - 1), fill=style["accent"], width=max(1, round(width * .003)))
            draw.text((x - b[0], y + pad / 2 - b[1]), line, font=font, fill=spec["color"])
            y += line_height + pad + max(2, pad // 3)
    else:
        if mode == "bubble":
            bottom -= pad
            draw.rounded_rectangle((pad // 2, pad // 2, canvas_width - 1, bottom + pad // 2), radius=round(width * .05), fill=style["accent"])
            draw.rounded_rectangle((0, 0, canvas_width - pad // 2 - 1, bottom), radius=round(width * .05), fill=spec["background"], outline=spec["color"], width=max(2, round(width * .005)))
            draw.polygon([(pad * 2, bottom - 2), (pad * 3, bottom - 2), (pad * 2, bottom + pad)], fill=spec["background"])
        elif mode == "paper":
            top += pad
            draw.rectangle((0, pad, canvas_width - 1, bottom), fill=spec["background"])
            for y in range(pad * 2 + size, bottom, size + spacing):
                draw.line((pad, y, canvas_width - pad, y), fill="#b7cad3", width=max(1, width // 900))
            draw.line((pad * 2 // 3, pad, pad * 2 // 3, bottom), fill="#d69c94", width=max(1, width // 700))
            draw.rectangle((canvas_width * .32, 0, canvas_width * .68, pad * 1.5), fill=style["accent"])
            for x in range(0, canvas_width, max(4, pad // 2)):
                draw.polygon([(x, bottom), (x + pad / 4, bottom - pad / 5), (x + pad / 2, bottom)], fill=(0, 0, 0, 0))
        else:
            draw.rounded_rectangle(bounds, radius=round(width * spec["radius"]), fill=spec["background"])
        if mode in ("cinema", "byline"):
            top += pad
            start = canvas_width * .35 if mode == "cinema" else pad
            draw.line((start, pad // 2, start + canvas_width * .3, pad // 2), fill=style["accent"], width=max(1, round(width * .002)))
        if mode in ("underline", "label"):
            draw.line((pad, bottom - 1, canvas_width - pad, bottom - 1), fill=style["accent"], width=max(1, round(width * .002)))
        if mode == "sidebar":
            draw.rectangle((0, pad, max(1, width * .005), bottom - pad), fill=style["accent"])
        if mode == "tag":
            draw.rectangle(bounds, outline=style["accent"], width=max(1, round(width * .003)))
        x = pad if spec["align"] == "left" else (canvas_width - (box[2] - box[0])) / 2
        draw.multiline_text((x - box[0], top - box[1]), wrapped, fill=spec["color"], stroke_fill=(0, 0, 0, 190), **options)
    decoration = spec.get("decoration")
    accent = style["accent"]
    weight = max(1, round(width * .003))
    if decoration == "titleCorners":
        arm = min(pad * 2, canvas_width * .12)
        draw.line([(2, pad), (2, 2), (arm, 2)], fill=accent, width=weight)
        draw.line([(canvas_width - arm, bottom - 2), (canvas_width - 3, bottom - 2), (canvas_width - 3, bottom - pad)], fill=accent, width=weight)
    elif decoration == "bulletin":
        draw.rectangle((0, 0, weight * 2, bottom), fill=accent)
        draw.rectangle((0, 0, canvas_width * .22, weight), fill=accent)
    elif decoration == "diamond":
        cx, cy = canvas_width / 2, bottom - 3
        draw.line((canvas_width * .28, cy, cx - pad, cy), fill=accent, width=max(1, weight // 2))
        draw.line((cx + pad, cy, canvas_width * .72, cy), fill=accent, width=max(1, weight // 2))
        draw.polygon([(cx - 3, cy), (cx, cy - 3), (cx + 3, cy), (cx, cy + 3)], fill=accent)
    elif decoration == "signature":
        draw.line((pad, bottom - 2, min(canvas_width - pad, pad + width * .13), bottom - 2), fill=accent, width=weight)
    elif decoration == "cinema":
        for y in (2, bottom - 2):
            draw.line((canvas_width * .32, y, canvas_width * .68, y), fill=accent, width=max(1, weight // 2))
    elif decoration == "rail":
        draw.rectangle((0, pad // 2, weight * 2, bottom - pad // 2), fill=accent)
    elif decoration == "doodle":
        for offset in (2, 6):
            draw.line((canvas_width * .18, bottom - offset, canvas_width * .80, bottom - offset - 2), fill=accent, width=weight)
        cx, cy = canvas_width - pad // 2 - 1, pad // 2
        draw.line((cx - pad // 3, cy, cx + pad // 3, cy), fill=accent, width=weight)
        draw.line((cx, cy - pad // 3, cx, cy + pad // 3), fill=accent, width=weight)
    elif decoration == "notes":
        for x in range(pad, canvas_width - pad, max(4, pad)):
            draw.line((x, bottom - 2, min(x + pad // 2, canvas_width - pad), bottom - 2), fill=accent, width=weight)
        draw.line((2, 2, pad, 2), fill=accent, width=weight)
        draw.line((2, 2, 2, pad), fill=accent, width=weight)
    if spec["rotation"]:
        image = image.rotate(-spec["rotation"], Image.Resampling.BICUBIC, expand=True)
    apply_opacity(image, opacity, spec.get("opacity", 1)).save(output_path)


def render_logo(logo_path, output_path, width, visual_style, height=None, opacity=None):
    """Contain the original mark in a style-specific badge; never crop its artwork."""
    from PIL import ImageOps

    spec = get_style(visual_style)["logo"]
    width = min(width, height or width)
    size = max(24, round(width * spec["size"]))
    if spec["shape"] == "transparent":
        with Image.open(logo_path) as source:
            inset = max(2, round(size * .15)) if spec.get("decoration") else 0
            artwork = ImageOps.contain(source.convert("RGBA"), (size - inset * 2, size - inset * 2), Image.Resampling.LANCZOS)
        mark = Image.new("RGBA", (size, size))
        mark.alpha_composite(artwork, ((size - artwork.width) // 2, (size - artwork.height) // 2))
        draw = ImageDraw.Draw(mark)
        accent = get_style(visual_style)["accent"]
        stroke = max(1, round(size * .018))
        edge, end = max(1, round(size * .04)), size - max(2, round(size * .04))
        motif = spec.get("decoration")
        if motif == "orbit":
            draw.arc((edge, edge, end, end), 25, 155, fill=accent, width=stroke)
            draw.arc((edge, edge, end, end), 205, 335, fill=accent, width=stroke)
        elif motif in ("corners", "bracket"):
            arm = round(size * .22)
            draw.line([(edge, edge + arm), (edge, edge), (edge + arm, edge)], fill=accent, width=stroke)
            draw.line([(end - arm, end), (end, end), (end, end - arm)], fill=accent, width=stroke)
        elif motif == "signature":
            draw.line((size * .3, end, size * .7, end), fill=accent, width=stroke)
        elif motif == "spark":
            cx, cy, r = size * .83, size * .17, size * .1
            draw.line((cx-r, cy, cx+r, cy), fill=accent, width=stroke)
            draw.line((cx, cy-r, cx, cy+r), fill=accent, width=stroke)
        apply_opacity(mark, opacity, spec.get("opacity", 1)).save(output_path)
        return
    polaroid = spec["shape"] == "polaroid"
    image = Image.new("RGBA", (size, round(size * 1.2) if polaroid else size))
    draw = ImageDraw.Draw(image)
    border = max(1, round(width * spec["borderWidth"]))
    bounds = (border // 2, border // 2, size - 1 - border // 2, image.height - 1 - border // 2)
    if spec["shape"] in ("circle", "seal", "sticker"):
        draw.ellipse(bounds, fill=spec["background"], outline=spec["border"], width=border)
        if spec["shape"] == "seal":
            inset_ring = max(border + 2, round(size * .09))
            draw.ellipse((inset_ring, inset_ring, size - inset_ring - 1, size - inset_ring - 1), outline=spec["border"], width=max(1, border // 2))
    else:
        draw.rounded_rectangle(bounds, radius=round(size * .14) if spec["shape"] == "tile" else 0, fill=spec["background"], outline=spec["border"], width=border)
    inset = round(size * (.2 if spec["shape"] in ("circle", "seal", "sticker") else .13))
    with Image.open(logo_path) as source:
        mark = ImageOps.contain(source.convert("RGBA"), (size - inset * 2, size - inset * 2), Image.Resampling.LANCZOS)
    image.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    if polaroid:
        draw.line((inset, size + size * .06, size - inset, size + size * .06), fill=spec["border"], width=max(1, border))
    if spec["rotation"]:
        image = image.rotate(-spec["rotation"], Image.Resampling.BICUBIC, expand=True)
    image.save(output_path)


def apply_opacity(image, value, default=1):
    try:
        opacity = max(0, min(1, float(default if value is None else value)))
    except (TypeError, ValueError):
        opacity = default
    image.putalpha(image.getchannel("A").point(lambda alpha: round(alpha * opacity)))
    return image

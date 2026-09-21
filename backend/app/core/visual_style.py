"""Visual presets shared by the browser previews and media renderer."""
import json
from pathlib import Path

STYLES = {item["id"]: item for item in json.loads(
    (Path(__file__).resolve().parents[1] / "config" / "visual_styles.json").read_text(encoding="utf-8")
)}


def get_style(style_id):
    # Existing content without a preset retains its original renderer.
    return STYLES.get(style_id) if isinstance(style_id, str) else None


def default_layout(style_id):
    style = get_style(style_id)
    return style["layout"] if style else {"text": {"x": 50, "y": 68}, "logo": {"x": 10, "y": 8}, "username": {"x": 82, "y": 92}}


def resolve_layout(style_id, config):
    """Upgrade the old shared defaults while retaining manually moved overlays."""
    saved = config.get("overlay_layout") or {}
    old_y = {"minimal": 72, "bold": 65, "cinematic": 72, "professional": 72, "playful": 65, "scrapbook": 70}
    legacy = {"text": {"x": 50, "y": old_y.get(style_id, 68)}, "logo": {"x": 10, "y": 8}, "username": {"x": 82, "y": 92}}
    if config.get("visual_layout_version") != 2 and saved == legacy:
        saved = {}
    return {name: {**position, **saved.get(name, {})} for name, position in default_layout(style_id).items()}


def render_style_frame(style_id, output_path, width, height):
    # PromptEngine loads the preset catalog during API startup. Import Pillow
    # only when rendering, after text_overlay has loaded Windows FriBiDi.
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (width, height))
    style = get_style(style_id)
    if style:
        draw = ImageDraw.Draw(image)
        if style.get("gradient"):
            for y in range(height):
                alpha = round(225 * max(0, min(1, (y / height - .25) / .65)))
                draw.line((0, y, width, y), fill=(5, 9, 16, alpha))
        for x, y, w, h, color in style["shapes"]:
            left, top = round(x * width), round(y * height)
            draw.rectangle((left, top, max(left, round((x + w) * width) - 1),
                            max(top, round((y + h) * height) - 1)), fill=color)
        for x, y, diameter, color in style.get("circles", []):
            radius = diameter * width / 2
            draw.ellipse((x * width - radius, y * height - radius, x * width + radius, y * height + radius), fill=color)
    image.save(output_path)

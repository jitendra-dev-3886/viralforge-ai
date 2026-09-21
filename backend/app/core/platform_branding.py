"""Platform identifiers beside creator handles; uploaded brand logos stay intact."""
def format_username(text, platform):
    value = str(text or "").strip()
    return "@" + value.lstrip("@") if value and str(platform).lower() in ("instagram", "youtube") else value


def render_platform_username(text, output_path, width, height, platform=None, visual_style=None, opacity=None):
    from app.core.text_overlay import render_caption, apply_opacity
    from app.core.visual_style import get_style
    from PIL import Image, ImageDraw
    brand_credit = (get_style(visual_style) or {}).get("username", {}).get("source") == "brand_name"
    key = "" if brand_credit else str(platform or "").lower()
    render_caption(format_username(text, key), output_path, width, height, size_ratio=.024, visual_style=visual_style, role="username", opacity=opacity)
    colors = {"instagram": "#e1306c", "facebook": "#1877f2", "youtube": "#ff0033"}
    if not str(text or "").strip() or key not in colors:
        return
    size = max(12, round(width * .036))
    # Draw large and downsample to keep tiny platform marks smooth.
    icon = Image.new("RGBA", (120, 120))
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle((0, 0, 119, 119), radius=22, fill=colors[key])
    if key == "instagram":
        draw.rounded_rectangle((23, 23, 97, 97), radius=21, outline="white", width=7)
        draw.ellipse((42, 42, 78, 78), outline="white", width=7)
        draw.ellipse((79, 32, 86, 39), fill="white")
    elif key == "youtube":
        draw.rounded_rectangle((18, 30, 102, 90), radius=16, outline="white", width=6)
        draw.polygon([(51, 44), (51, 76), (78, 60)], fill="white")
    else:
        draw.line([(75, 25), (62, 25), (51, 36), (51, 102)], fill="white", width=13)
        draw.line((32, 53, 78, 53), fill="white", width=12)
    spec = (get_style(visual_style) or {}).get("username", {})
    icon = apply_opacity(icon.resize((size, size), Image.Resampling.LANCZOS), opacity, spec.get("opacity", 1))
    with Image.open(output_path) as source:
        caption = source.convert("RGBA")
    gap = max(2, round(width * .008))
    result = Image.new("RGBA", (caption.width + size + gap, max(size, caption.height)))
    result.alpha_composite(icon, (0, (result.height - size) // 2))
    result.alpha_composite(caption, (size + gap, (result.height - caption.height) // 2))
    limit = round(width * spec.get("width", .84))
    if result.width > limit:
        result = result.resize((limit, max(1, round(result.height * limit / result.width))), Image.Resampling.LANCZOS)
    result.save(output_path)

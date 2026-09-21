"""Render the brand credit without social-handle formatting."""


def render_platform_username(text, output_path, width, height, platform=None, visual_style=None, opacity=None):
    from app.core.text_overlay import render_caption
    render_caption(str(text or "").strip(), output_path, width, height,
                   size_ratio=.024, visual_style=visual_style, role="username", opacity=opacity)

def output_brand_name(content):
    """Use saved branding, or the project's brand for older content."""
    branding = (content.generation_config or {}).get("branding") or {}
    name = str(branding.get("brand_name") or "").strip()
    if name:
        return name
    brand = content.project.brand if content.project else None
    return brand.name if brand else ""

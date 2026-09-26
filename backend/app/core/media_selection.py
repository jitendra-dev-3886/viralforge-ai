"""Utilities for choosing stock media that fits the final social format."""

from __future__ import annotations

import math
import re
from urllib.parse import unquote, urlparse
from typing import Any, Callable, Iterable


def best_for_query(items, dimensions, *, query, media_type, orientation):
    """Require descriptive metadata overlap before considering crop/resolution.

    This is a conservative text check, not visual recognition. Missing or
    unrelated metadata is rejected so the other stock provider can be tried.
    """
    ignored = set("a an the of on in at to with and or for from by is are stock photo video image footage clip person people man woman hands background close up beautiful shot view morning evening daytime cinematic lighting sunlight sunlit softly natural".split())

    def terms(text):
        words = set()
        for word in re.findall(r"[a-z]+", str(text).lower()):
            if word in ignored or len(word) < 3:
                continue
            if word.endswith("s") and not word.endswith("ss"):
                word = word[:-1]
            if word.endswith("ing") and len(word) > 5:
                word = word[:-3]
            elif word.endswith("ion") and len(word) > 6:
                word = word[:-3]
            if word.endswith("e") and len(word) > 4:
                word = word[:-1]
            words.add(word)
        return words

    required = terms(query)
    if not required:
        return None
    ranked = []
    for index, item in enumerate(items):
        # Pexels videos expose descriptive page slugs, photos also have alt;
        # Pixabay exposes tags. Never use the download URL or photographer name.
        page = item.get("pageURL") or item.get("url") or ""
        metadata = " ".join(str(item.get(key) or "") for key in ("alt", "tags", "title"))
        metadata += " " + unquote(urlparse(page).path).replace("-", " ")
        matched = required & terms(metadata)
        # Partial overlap can omit the actual subject (e.g. "solar" in
        # "solar panel installation") while accepting an unrelated asset.
        if matched != required:
            continue
        fit = dimension_score(*dimensions(item), media_type=media_type, orientation=orientation)
        if math.isfinite(fit):
            ranked.append((fit, -index, item))
    return max(ranked, key=lambda row: row[:2])[2] if ranked else None


def normalise_orientation(value: str | None) -> str:
    value = (value or "").strip().lower()
    return value if value in {"portrait", "landscape", "square"} else "square"


def target_aspect_ratio(media_type: str, orientation: str | None) -> float:
    """Return a useful post-ready ratio instead of just the largest source file."""
    orientation = normalise_orientation(orientation)
    if orientation == "portrait":
        # 4:5 works well for feeds; 9:16 is the right source shape for clips.
        return 9 / 16 if media_type == "video" else 4 / 5
    if orientation == "landscape":
        return 16 / 9
    return 1.0


def dimension_score(
    width: int | float | None,
    height: int | float | None,
    *,
    media_type: str,
    orientation: str | None,
) -> float:
    """Score a candidate by crop suitability first, then usable resolution."""
    width = float(width or 0)
    height = float(height or 0)
    if width <= 0 or height <= 0:
        return float("-inf")

    aspect = width / height
    desired = target_aspect_ratio(media_type, orientation)
    aspect_match = -abs(math.log(aspect / desired))
    resolution_bonus = min(math.log10(width * height), 8) / 20
    return aspect_match * 100 + resolution_bonus


def best_by_dimensions(
    items: Iterable[Any],
    dimensions: Callable[[Any], tuple[int | float | None, int | float | None]],
    *,
    media_type: str,
    orientation: str | None,
) -> Any | None:
    candidates = list(items)
    if not candidates:
        return None

    return max(
        candidates,
        key=lambda item: dimension_score(
            *dimensions(item),
            media_type=media_type,
            orientation=orientation,
        ),
    )

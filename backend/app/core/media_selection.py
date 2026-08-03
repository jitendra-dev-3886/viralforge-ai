"""Utilities for choosing stock media that fits the final social format."""

from __future__ import annotations

import math
from typing import Any, Callable, Iterable


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
